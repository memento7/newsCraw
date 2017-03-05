# -*- coding: utf-8 -*-
import scrapy
from scrapy.item import Item, Field


class newsCommentCrawItem(scrapy.Item):
    href = scrapy.Field()
    count = scrapy.Field()
    comments = scrapy.Field()
    # contents = scrapy.Field()
    # maskedUserId = scrapy.Field()
    # replyCount = scrapy.Field()
    # sympathyCount = scrapy.Field()
    # antipathyCount = scrapy.Field()
    # modTime = scrapy.Field()