---
title: 'Replace Tailwind CSS with local stylesheet'
type: 'refactor'
created: '2026-04-08'
status: 'done'
baseline_commit: 'bb794aa'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The site loads Tailwind via CDN (`cdn.tailwindcss.com` with plugins) which adds an external dependency, increases page load time, and scatters styling logic across HTML attributes instead of maintainable CSS.

**Approach:** Extend the existing `theme.css` (which already has CSS variables, dark mode, and component classes) with semantic component/layout classes that replace all Tailwind utility classes in templates. Then strip Tailwind from every template and remove the CDN script.

## Boundaries & Constraints

**Always:**
- Preserve the current visual appearance exactly (same layout, spacing, colors, responsiveness, dark mode)
- Use the existing CSS custom properties (`--primary`, `--bg-body`, `--text-main`, etc.) for all values
- Use semantic class names (`.job-grid`, `.page-section`) not utility clones (`.flex`, `.gap-4`)
- Keep CSS DRY — shared patterns extracted into reusable classes, no copy-paste blocks
- Maintain existing responsive breakpoints (641px, 785px, 1024px)

**Ask First:**
- If a template's layout seems wrong/inconsistent in current Tailwind version, ask before "fixing" it during migration

**Never:**
- Add any external CSS framework, reset, or CDN resource
- Change HTML structure or Django template logic — only class attributes change
- Break dark mode theming

</frozen-after-approval>

## Code Map

- `tallinnstartups/static/css/theme.css` -- existing 1599-line stylesheet with CSS vars, dark mode, component classes; extend this
- `tallinnstartups/templates/tallinnstartups/base.html` -- loads Tailwind CDN (line 47), preconnect (line 10); remove these
- `tallinnstartups/templates/tallinnstartups/index.html` -- landing page: hero, featured jobs grid, category cards
- `tallinnstartups/templates/tallinnstartups/jobs_list.html` -- job listing grid with filters
- `tallinnstartups/templates/tallinnstartups/job_detail.html` -- job detail with prose content, sidebar, apply CTA
- `tallinnstartups/templates/tallinnstartups/companies_list.html` -- company directory grid
- `tallinnstartups/templates/tallinnstartups/post_job.html` -- job posting form
- `tallinnstartups/templates/tallinnstartups/post_cofounder.html` -- cofounder posting form
- `tallinnstartups/templates/tallinnstartups/hire_me_list.html` -- talent directory
- `tallinnstartups/templates/tallinnstartups/hire_me_detail.html` -- talent profile detail
- `tallinnstartups/templates/tallinnstartups/job_status.html` -- job status checker
- `tallinnstartups/templates/tallinnstartups/category_jobs.html` -- category filtered jobs
- `tallinnstartups/templates/tallinnstartups/company_jobs.html` -- company filtered jobs
- `tallinnstartups/templates/tallinnstartups/job_submission_success.html` -- success page
- `tallinnstartups/templates/tallinnstartups/hire_me_submission_success.html` -- success page
- `tallinnstartups/templates/tallinnstartups/privacy_policy.html` -- legal page
- `tallinnstartups/templates/tallinnstartups/terms_of_service.html` -- legal page
- `tallinnstartups/templates/404.html` -- error page
- `tallinnstartups/templates/tallinnstartups/components/header.html` -- sticky nav, mobile menu, theme toggle
- `tallinnstartups/templates/tallinnstartups/components/footer.html` -- 4-column footer grid
- `tallinnstartups/templates/tallinnstartups/components/job_card.html` -- job listing card
- `tallinnstartups/templates/tallinnstartups/components/search_bar.html` -- search input with icon
- `tallinnstartups/templates/tallinnstartups/components/pagination.html` -- page navigation
- `tallinnstartups/templates/tallinnstartups/components/breadcrumbs.html` -- breadcrumb nav
- `tallinnstartups/templates/tallinnstartups/components/tag_cloud.html` -- tag display
- `tallinnstartups/templates/tallinnstartups/components/success_card.html` -- success message card
- `tallinnstartups/templates/tallinnstartups/components/hire_me_card.html` -- talent card
- `tallinnstartups/static/js/theme.js` -- uses `hidden`, `dark-theme` classes; no changes needed

## Tasks & Acceptance

**Execution:**
- [x] `tallinnstartups/static/css/theme.css` -- Add semantic layout and component classes (page shell, grids, sections, prose, forms, cards) that replace all Tailwind utility patterns found across templates. Organize new rules into clearly commented sections.
- [x] `tallinnstartups/templates/tallinnstartups/base.html` -- Remove Tailwind CDN script and preconnect link. Replace Tailwind classes with semantic classes.
- [x] `tallinnstartups/templates/tallinnstartups/components/*.html` -- Replace all Tailwind classes in all 8 component templates with semantic classes from theme.css.
- [x] `tallinnstartups/templates/tallinnstartups/index.html` -- Replace Tailwind classes with semantic classes.
- [x] `tallinnstartups/templates/tallinnstartups/jobs_list.html`, `category_jobs.html`, `company_jobs.html` -- Replace Tailwind classes (these share job-grid layout patterns).
- [x] `tallinnstartups/templates/tallinnstartups/job_detail.html` -- Replace Tailwind classes including prose/typography styles.
- [x] `tallinnstartups/templates/tallinnstartups/companies_list.html` -- Replace Tailwind classes.
- [x] `tallinnstartups/templates/tallinnstartups/post_job.html`, `post_cofounder.html` -- Replace Tailwind classes (shared form patterns).
- [x] `tallinnstartups/templates/tallinnstartups/hire_me_list.html`, `hire_me_detail.html` -- Replace Tailwind classes.
- [x] `tallinnstartups/templates/tallinnstartups/job_status.html`, `job_submission_success.html`, `hire_me_submission_success.html` -- Replace Tailwind classes (simple status/success pages).
- [x] `tallinnstartups/templates/tallinnstartups/privacy_policy.html`, `terms_of_service.html` -- Replace Tailwind classes (legal/prose pages).
- [x] `tallinnstartups/templates/404.html` -- Replace Tailwind classes.

**Acceptance Criteria:**
- Given the site loads in a browser, when inspecting network requests, then no requests to `cdn.tailwindcss.com` or any external CSS resource are made
- Given any page is viewed, when compared to the current Tailwind version, then layout, spacing, colors, and typography are visually identical
- Given the theme toggle is clicked, when dark mode activates, then all pages render correctly in dark theme
- Given a mobile viewport (< 641px), when viewing any page, then responsive layouts match current behavior
- Given the CSS file is opened, when reviewing the code, then no duplicate rule blocks exist and shared patterns use reusable classes

## Verification

**Commands:**
- `poetry run python manage.py runserver` -- expected: site loads with no console errors, no external CSS requests
- `grep -r "tailwindcss\|cdn.tailwindcss" tallinnstartups/` -- expected: zero matches

**Manual checks:**
- Compare each page visually against current version in both light/dark mode at desktop and mobile widths

## Suggested Review Order

**CSS Architecture — new semantic classes**

- Entry point: all new classes organized in commented sections
  [`theme.css:1600`](../../tallinnstartups/static/css/theme.css#L1600)

- Page layout shell (page-wrapper, page-content, body-shell)
  [`theme.css:1604`](../../tallinnstartups/static/css/theme.css#L1604)

- Heading hierarchy (page, section, subsection, card)
  [`theme.css:1652`](../../tallinnstartups/static/css/theme.css#L1652)

- Job prose typography replacing Tailwind's prose plugin
  [`theme.css:1766`](../../tallinnstartups/static/css/theme.css#L1766)

- Status page components (badges, panels, step indicators)
  [`theme.css:1887`](../../tallinnstartups/static/css/theme.css#L1887)

**Tailwind CDN removal**

- CDN script and preconnect removed from base template
  [`base.html:9`](../../tallinnstartups/templates/tallinnstartups/base.html#L9)

**Core component migrations**

- Header: nav, mobile menu, theme toggle class replacements
  [`header.html:1`](../../tallinnstartups/templates/tallinnstartups/components/header.html#L1)

- Job card: semantic classes for logo, body, title, featured tag
  [`job_card.html:1`](../../tallinnstartups/templates/tallinnstartups/components/job_card.html#L1)

- Breadcrumbs: mobile/desktop responsive classes
  [`breadcrumbs.html:1`](../../tallinnstartups/templates/tallinnstartups/components/breadcrumbs.html#L1)

**High-complexity page migrations**

- Job detail: prose, detail grid, related jobs, expired notice
  [`job_detail.html:71`](../../tallinnstartups/templates/tallinnstartups/job_detail.html#L71)

- Job status: step indicators, status badges, panels
  [`job_status.html:6`](../../tallinnstartups/templates/tallinnstartups/job_status.html#L6)

- Post job form: form-stack, form-grid, form-field, form-label
  [`post_job.html:10`](../../tallinnstartups/templates/tallinnstartups/post_job.html#L10)

**Blog templates (caught by review, added post-spec)**

- Article list, detail, and category templates
  [`article_list.html:1`](../../blog/templates/blog/article_list.html#L1)
