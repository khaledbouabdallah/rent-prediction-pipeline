import scrapy
import csv
import functools
import os


project_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))


class LocServiceSpider(scrapy.Spider):
    name = "loc_service"
    start_urls = [
       "https://www.locservice.fr/location-carte.html" 
    ]

    def parse(self, response):
        # Add your parsing logic here
        pass
    

# Spider to get the urls of the departments
class LocServiceSpider_departements(scrapy.Spider):
    
    name = "loc_service_departments"
    allowed_domains = ['locservice.fr']
    start_urls = ['https://www.locservice.fr/location-carte.html']
   

    def parse(self, response):
        # Add your parsing logic here
        departments_urls = response.css("area").xpath("@href").getall()
        print(len(departments_urls))
        for url in departments_urls:
            splits = url.split("/")[1].split("-")
            yield {
                'nom': "-".join(splits[:-1]),
                'number': splits[-1],
                'url': url,
            }
    
# Spider to get the urls of the cities        
class LocServiceSpider_cities(scrapy.Spider):
    
    name = "loc_service_cities"
    allowed_domains = ['locservice.fr']
    base_url = 'https://www.locservice.fr'
    start_urls = []
    
    def start_requests(self):
        with open("/home/khaled/scraper/bigdata/bigdata/data/locservice_depart_href.csv", mode='r') as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)
            # Skip the header
            next(csv_reader)
            for row in csv_reader:
                partial_callback = functools.partial(self.parse, name=row[0], number=row[1])
                yield scrapy.Request(url=self.base_url + row[2], callback=partial_callback) 
                

    def parse(self, response,name,number):
        cities = response.css(".ville_liste li a")    
        for city in cities:
            yield {
            'department_name': name,
            'department_number': number,
            'city_name': city.css("::text").get(),
            'city_url': city.xpath("@href").get()
            }     