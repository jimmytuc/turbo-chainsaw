from scrapy import Field, Item


class Metadata(Item):
    id = Field()
    title = Field()
    description = Field()
