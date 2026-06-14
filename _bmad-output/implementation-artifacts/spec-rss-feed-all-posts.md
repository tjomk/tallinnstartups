---
title: 'RSS feed for all posts'
type: 'feature'
created: '2026-06-14'
status: 'done'
context: []
baseline_commit: '97b0d6b089893665a60394643ca7a592f8110d4b'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The site has no machine-readable feed. Visitors and aggregators cannot subscribe to new postings (jobs, co-founder searches, professional/"hire me" profiles) without polling HTML pages.

**Approach:** Add a single combined RSS 2.0 feed at `/feed/` listing every live, non-expired post across all three types (regular `Job`, co-founder `Job`, `HireMePost`), newest first, built with Django's `django.contrib.syndication` framework. Add an autodiscovery `<link>` to the site head.

## Boundaries & Constraints

**Always:**
- Include only public-visible posts: `Job` with `status='live'` and not expired (both `job_type='job'` and `'cofounder'`), plus `HireMePost` with `status='live'` and not expired.
- Sort all items together by `created_at` descending; cap at the 50 most recent.
- Build absolute item links from `settings.SITE_BASE_URL` + the post's existing detail URL (`job_detail` for Jobs, `hire_me_detail` for HireMePosts), matching how the codebase already produces canonical URLs.
- Keep DB access in repositories and orchestration/normalization in the service layer (project convention).

**Ask First:**
- Adding pagination, per-type feeds, or Atom format (out of current scope — combined feed only).

**Never:**
- Expose non-live, expired, in-review, or rejected posts.
- Pull in `django.contrib.sites` or new third-party dependencies (syndication ships with Django; sites framework is not installed).
- Change existing views, models, or URLs unrelated to the feed.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Mixed live posts | Live jobs, cofounder posts, hire-me posts exist | `GET /feed/` → 200, `application/rss+xml`, all three types interleaved by `created_at` desc | N/A |
| Expired / non-live | A job is expired or `status != 'live'` | That item is absent from the feed | N/A |
| Empty | No live posts of any type | 200 with a valid empty RSS channel (no `<item>`s) | N/A |
| Cap | More than 50 live posts | Only the 50 newest appear | N/A |
| Item links | Any item | `<link>` is absolute, e.g. `https://estonianstartupjobs.ee/job/<slug>/` or `/hire-me/<slug>/` | N/A |

</frozen-after-approval>

## Code Map

- `jobs/feeds.py` -- NEW: `AllPostsFeed(Feed)` syndication class (imperative shell / framework adapter).
- `jobs/services.py` -- add `FeedService.get_feed_items()` returning normalized, sorted, capped feed items.
- `jobs/repositories.py` -- reuse `JobRepository.get_all_jobs()` (returns all live, non-expired Jobs incl. cofounders) and `HireMeRepository.get_all_posts()`; no new query needed.
- `tallinnstartups/urls.py` -- register `path('feed/', AllPostsFeed(), name='feed')`.
- `tallinnstartups/templates/tallinnstartups/base.html` -- add RSS autodiscovery `<link rel="alternate" type="application/rss+xml">` in `<head>`.
- `tallinnstartups/settings.py` -- `SITE_BASE_URL` already defined (line 174); read it, do not modify.
- `jobs/tests.py` -- feed tests.

## Tasks & Acceptance

**Execution:**
- [x] `jobs/services.py` -- add a `FeedItem` lightweight value (e.g. `@dataclass` with `title, description, link, pubdate, guid, categories`) and a `FeedService` with `get_feed_items(limit=50)`. It calls `JobRepository.get_all_jobs()` and `HireMeRepository.get_all_posts()`, normalizes each model to a `FeedItem` (absolute `link` = `settings.SITE_BASE_URL` + `reverse('job_detail'/'hire_me_detail', ...)`; `guid` = absolute link; `categories` = `[get_job_type_display]`/`['Job']` etc.), merges, sorts by `pubdate` desc, returns first `limit`. Pure normalization given querysets. -- keeps logic testable and in the service layer.
- [x] `jobs/feeds.py` -- NEW: `AllPostsFeed(Feed)` with `title`, `link='/feed/'`, `description`; `items()` returns `FeedService().get_feed_items()`; `item_title/item_description/item_link/item_pubdate/item_guid/item_categories` read the `FeedItem` fields. Set `feed_type = Rss201rev2Feed`. -- standard syndication adapter.
- [x] `tallinnstartups/urls.py` -- import `AllPostsFeed` from `jobs.feeds`, add `path('feed/', AllPostsFeed(), name='feed')`. -- exposes the feed.
- [x] `tallinnstartups/templates/tallinnstartups/base.html` -- add `<link rel="alternate" type="application/rss+xml" title="Estonian Startup Jobs" href="{% url 'feed' %}">` inside `<head>`. -- feed autodiscovery.
- [x] `jobs/tests.py` -- add tests covering the I/O & Edge-Case Matrix (mixed types present & ordered, expired/non-live excluded, empty channel valid, 50-cap, absolute links). -- proves behavior.

**Acceptance Criteria:**
- Given live jobs, cofounder posts, and hire-me posts exist, when I `GET /feed/`, then I receive HTTP 200 with content-type `application/rss+xml` and one `<item>` per live post, ordered by `created_at` descending across all types.
- Given a post is expired or not `status='live'`, when I `GET /feed/`, then that post does not appear.
- Given any feed item, when I inspect its `<link>` and `<guid>`, then both are absolute URLs rooted at `SITE_BASE_URL`.
- Given more than 50 live posts exist, when I `GET /feed/`, then at most 50 items are returned (newest first).
- Given a request for any page, when the HTML loads, then the head contains an RSS autodiscovery link pointing to `/feed/`.

## Verification

**Commands:**
- `poetry run python manage.py test jobs` -- expected: all feed tests pass.
- `poetry run python manage.py runserver` then `curl -s http://127.0.0.1:8000/feed/ | head -30` -- expected: valid `<rss version="2.0">` XML with `<item>` entries.

## Suggested Review Order

**Feed assembly (core)**

- Entry point: normalizes all three post types into a single sorted, capped list.
  [`services.py:550`](../../jobs/services.py#L550)
- The value object every item maps to — shared shape for jobs and profiles.
  [`services.py:505`](../../jobs/services.py#L505)
- Slug guard + `(pubdate, guid)` tie-break keep one bad row from 500-ing the feed.
  [`services.py:550`](../../jobs/services.py#L550)

**RSS emission (shell)**

- Thin syndication adapter; reads `FeedItem` fields, no logic.
  [`feeds.py:7`](../../jobs/feeds.py#L7)
- Channel link points at the homepage, not the feed itself.
  [`feeds.py:13`](../../jobs/feeds.py#L13)

**Wiring**

- Public route at `/feed/`.
  [`urls.py:43`](../../tallinnstartups/urls.py#L43)
- Autodiscovery link so readers find the feed from any page.
  [`base.html:19`](../../tallinnstartups/templates/tallinnstartups/base.html#L19)

**Tests**

- Covers all three types, exclusion, empty channel, 50-cap, slug guard, absolute links.
  [`tests.py:321`](../../jobs/tests.py#L321)
