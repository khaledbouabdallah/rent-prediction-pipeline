# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# Postgres library
import psycopg2


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
    



class SaveToPostgresPipeline:

    def __init__(self):
        ## Connection Details
        hostname = 'localhost'
        username = 'admin'
        password = 'your_password' # your password
        database = 'bigdata'
        port = 5432

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database, port=port)
        
        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()
        
        ## Create books table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id serial PRIMARY KEY, 
            url VARCHAR(255),
            title text,
            upc VARCHAR(255),
            product_type VARCHAR(255),
            price_excl_tax DECIMAL,
            price_incl_tax DECIMAL,
            tax DECIMAL,
            price DECIMAL,
            availability INTEGER,
            num_reviews INTEGER,
            stars INTEGER,
            category VARCHAR(255),
            description text
        )
        """)

    def process_item(self, item, spider):
        return item