from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from .services import FeedService


class AllPostsFeed(Feed):
    """Combined RSS feed of every live post: jobs, co-founder searches, and
    professional ("hire me") profiles, newest first."""

    feed_type = Rss201rev2Feed
    title = "Estonian Startup Jobs"
    link = "/"  # the site this feed describes (channel link points at the homepage)
    description = "Latest jobs, co-founder searches, and professional profiles from Estonia's startup ecosystem."

    def items(self):
        return FeedService().get_feed_items()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.link

    def item_guid(self, item):
        return item.guid

    def item_pubdate(self, item):
        return item.pubdate

    def item_categories(self, item):
        return item.categories
