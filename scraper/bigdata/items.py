# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BigdataItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class AdItem(scrapy.Item):
    title = scrapy.Field()
    ad_type = scrapy.Field()
    
    department_name = scrapy.Field()
    department_number = scrapy.Field()
    city_name = scrapy.Field()
    
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    price = scrapy.Field()
    area = scrapy.Field()
    available = scrapy.Field()
    furniture = scrapy.Field()
    energy_DPE = scrapy.Field()
    energy_GES = scrapy.Field()
    description = scrapy.Field()
    features = scrapy.Field()
    url = scrapy.Field()