# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BigdataPipeline:
    def process_item(self, item, spider):
        return item


class LocServiceAdPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)
        # Remove leading and trailing whitespaces   
        for key in adapter.keys():
            value = adapter.get(key)
            if value and key != "url" and key != "features":
                adapter[key] = value.strip()   
        # Convert features to float 
        for key in ["longitude", "latitude", "price", "area"]:
            value = adapter.get(key)
            if value:
                adapter[key] = float(value)    
        return item