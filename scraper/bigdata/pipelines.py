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
        
        # Convert features to str (for SQL insert)
        adapter["features"] = ";".join(adapter["features"])
        
        # Fill missing values with empty string
        for key in ["ad_type", "available","furniture", "description", "energy_DPE", "energy_GES"]:
            value = adapter.get(key)
            if not value:
                adapter[key] = ""
        
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
        CREATE TABLE IF NOT EXISTS ads(
            id serial PRIMARY KEY, 
            department_name VARCHAR(255),
            department_number INTEGER,
            city_name VARCHAR(255),
            title text,
            ad_type VARCHAR(255),
            latitude DECIMAL,
            longitude DECIMAL,
            price DECIMAL,
            area DECIMAL,
            available VARCHAR(255),
            furniture VARCHAR(255),
            energy_DPE VARCHAR(255),
            energy_GES VARCHAR(255),
            description text,
            features text,
            url VARCHAR(255)
        )
        """)

    def process_item(self, item, spider):

        ## Define insert statement
        self.cur.execute(""" insert into ads (
            department_name,
            department_number,
            city_name,
            title,
            ad_type,
            latitude,
            longitude,
            price,
            area,
            available,
            furniture,
            energy_DPE,
            energy_GES,
            description,
            features,
            url
            ) values (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
                )""", (
            item.get('department_name'),
            item.get('department_number'),
            item.get('city_name'),
            item.get('title'),
            item.get('ad_type'),
            item.get('latitude'),
            item.get('longitude'),
            item.get('price'),
            item.get('area'),
            item.get('available'),
            item.get('furniture'),
            item.get('energy_DPE'),
            item.get('energy_GES'),
            item.get('description'),
            item.get('features'),
            item.get('url')
        ))

        ## Execute insert of data into database
        self.connection.commit()
        return item

    def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cur.close()
        self.connection.close()