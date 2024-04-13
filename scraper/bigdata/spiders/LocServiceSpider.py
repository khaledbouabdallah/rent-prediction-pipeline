import scrapy
import csv
import functools
import os
from scrapy_splash import SplashRequest
import base64 
import re
from bigdata.items import AdItem


project_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    
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
            

# Spider to get the urls of the ads and the ads details            
class LocServiceSpider(scrapy.Spider):
    name = "loc_service"
    allowed_domains = ['locservice.fr']
    start_urls = []
    
    lua_script = """
                function main(splash, args)
                    assert(splash:go(args.url))
                    assert(splash:wait(0.5))
                    splash:har_reset()
                    splash.response_body_enabled = true
                    local map = splash:select('#staticmap')
                    map:mouse_click()
                    splash:wait(0.5)
                    return {
                      html = splash:html(),
                      har = splash:har(),
                    }
                end
                """
    
    def start_requests(self):
        with open("/home/khaled/scraper/scraper/bigdata/data/locservice_cities_href.csv", mode='r') as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)
            # Skip the header
            next(csv_reader)
            for i,row in enumerate(csv_reader):
                if i < 46:
                    continue
                if i == 10000:
                    break
                # logger.info(f"*************************")
                # logger.info(f"Department: {row[0]} - {row[1]}")
                # logger.info(f"*************************")
                partial_callback = functools.partial(self.parse, metadata=row[0:3], first=True)
                yield scrapy.Request(url=row[3], callback=partial_callback) 



    def parse(self, response, **kwargs):
        
        # get metadata
        metadata = kwargs.get("metadata")
        first = kwargs.get("first")
        department_name,department_number,city_name = metadata
        
        # logger.info(f"****")
        # logger.info(f"{response.url}")
        # logger.info(f"{department_name} - {department_number} - {city_name}")
        # logger.info(f"****")
       
        
        # parse ads urls
        ads_links = response.css(".extraitproprietaires a")
        for ad in ads_links:
            ad_link = ad.xpath("@href").get()
            partial_callback = functools.partial(self.parse_ad_splash, metadata=metadata)
            yield response.follow(ad_link, callback=partial_callback)
        
            
        #check for other pages
        if first:
            last_page = response.css(".pagination ::text").getall()
            if last_page:
                last_page = last_page[-1]
                next_pages = self._next_pages_(response.url, int(last_page))
                for page in next_pages:
                    partial_callback = functools.partial(self.parse, metadata=metadata, first=False)
                    yield response.follow(page, callback=partial_callback)
    
            
    
    def parse_ad_splash(self, response, **kwargs):
        
        
        metadata = kwargs.get("metadata")
        to_splash = response.css("#propKQ").getall()
        url = response.url
        
        if to_splash:
            partial_callback = functools.partial(self.parse_ad, metadata=metadata, splash=True)
            yield  SplashRequest(
                        url, 
                        callback=partial_callback, 
                        endpoint='execute', 
                        args={'wait': 0, 'lua_source': self.lua_script, url: url}
                        )
        else:
            department_name,department_number,city_name = metadata
            html = response
            lat_value = None
            lon_value = None
             # parse html content
            price = html.css(".loyer ::text").getall()[1].split(" ")[0].replace(".","")
            area = html.css(".surface ::text").getall()[1].split(" ")[0]
            available = html.css(".dispo ::text").getall()[1]
            furniture = html.css(".meuble ::text").getall()[1]
            energy_DPE,energy_GES = self.extract_dpe_ges(html.css(".dpe div ::text").getall())
            description = html.css(".innerDetail p ::text").getall()[0].replace("\n", "")
            features = html.css(".innerDetail ul li ::text").getall()
            ad_item = AdItem()
            ad_item['department_name'] = department_name
            ad_item['department_number'] = department_number
            ad_item['city_name'] = city_name
            ad_item['title'] = html.css("title::text").get()
            ad_item['ad_type'] = html.css("#listing_type .current ::text").get()
            ad_item['latitude'] = lat_value
            ad_item['longitude'] = lon_value
            ad_item['price'] = price
            ad_item['area'] = area
            ad_item['available'] = available
            ad_item['furniture'] = furniture
            ad_item['energy_DPE'] = energy_DPE
            ad_item['energy_GES'] = energy_GES
            ad_item['description'] = description
            ad_item['features'] = features
            ad_item['url'] = response.url

            yield ad_item
      
        
    def parse_ad(self, response, **kwargs):
        
        # get metadata
        metadata = kwargs.get("metadata")
        splash = kwargs.get("splash")
        department_name,department_number,city_name = metadata
        
        
        if splash:
            # get latitudes and longitudes from Network tab
            xml = response.data["har"]["log"]["entries"][0]["response"]["content"]["text"]
            xml = base64.b64decode(xml).decode("utf-8")
            lat_value = re.findall(r'lat="([^"]+)"', xml)[0]
            lon_value = re.findall(r'lon="([^"]+)"', xml)[0]
            # get html content
            source = response.data["html"].replace("=\\", "=")
            html = scrapy.Selector(text=source)
        else:
            html = response
            lat_value = ''
            lon_value = ''
        
        # parse html content
        price = html.css(".loyer ::text").getall()[1].split(" ")[0].replace(".","")
        area = html.css(".surface ::text").getall()[1].split(" ")[0]
        available = html.css(".dispo ::text").getall()[1]
        furniture = html.css(".meuble ::text").getall()[1]
        energy_DPE,energy_GES = self.extract_dpe_ges(html.css(".dpe div ::text").getall())
        description = html.css(".innerDetail p ::text").getall()[0].replace("\n", "")
        features = html.css(".innerDetail ul li ::text").getall()
        
        ad_item = AdItem()
        
        ad_item['department_name'] = department_name
        ad_item['department_number'] = department_number
        ad_item['city_name'] = city_name
        ad_item['title'] = html.css("title::text").get()
        ad_item['ad_type'] = html.css("#listing_type .current ::text").get()
        ad_item['latitude'] = lat_value
        ad_item['longitude'] = lon_value
        ad_item['price'] = price
        ad_item['area'] = area
        ad_item['available'] = available
        ad_item['furniture'] = furniture
        ad_item['energy_DPE'] = energy_DPE
        ad_item['energy_GES'] = energy_GES
        ad_item['description'] = description
        ad_item['features'] = features
        ad_item['url'] = response.url
        
        yield ad_item
              
        # function to format the next pages 
    
    def _next_pages_(self,link,max_pages):
        x,y = link[:-5], link[-5:]
        x = x + "-p"
        return [x + str(i) + y for i in range(2,max_pages+1)]
    
    def extract_dpe_ges(self,texts): # list of strings
        l = []
        for t in texts:
            if ":" in t:
                x = t.split(":")
                for i in x:
                    if i.strip():
                        l.append(i.strip())
            else:
                l.append(t.strip())
        if l:
            return l[1], l[3]
        else:
            return None, None
    
    

    # Test Spider

# Spider to scrap one ad
# Run the spider with the following command:
# scrapy crawl testSpider -o test.json
class TestSpider(scrapy.Spider):
    name = "testSpider"
    allowed_domains = ['locservice.fr']
   
    lua_script = """
                function main(splash, args)
                    assert(splash:go(args.url))
                    assert(splash:wait(0.5))
                    splash:har_reset()
                    splash.response_body_enabled = true
                    local map = splash:select('#staticmap')
                    map:mouse_click()
                    splash:wait(0.5)
                    return {
                      html = splash:html(),
                      har = splash:har(),
                    }
                end
                """
                
    def start_requests(self):
        
        url = 'https://www.locservice.fr/paris-75/location-appartement-paris-13/5960.html'
        
        
        yield SplashRequest(
            url, 
            callback=self.parse, 
            endpoint='execute', 
            args={'wait': 1, 'lua_source': self.lua_script, url: url}
            )
    def parse(self, response):
        # get latitudes and longitudes from Network tab
        xml = response.data["har"]["log"]["entries"][0]["response"]["content"]["text"]
        xml = base64.b64decode(xml).decode("utf-8")
        lat_value = re.findall(r'lat="([^"]+)"', xml)[0]
        lon_value = re.findall(r'lon="([^"]+)"', xml)[0]
        # get html content
        source = response.data["html"].replace("=\\", "=")
        html = scrapy.Selector(text=source)
        # parse html content
        price = html.css(".loyer ::text").getall()[1].split(" ")[0].replace(".","")
        area = html.css(".surface ::text").getall()[1].split(" ")[0]
        available = html.css(".dispo ::text").getall()[1]
        furniture = html.css(".meuble ::text").getall()[1]
        energy_DPE,energy_GES = self.extract_dpe_ges(html.css(".dpe div ::text").getall())
        description = html.css(".innerDetail p ::text").getall()[0].replace("\n", "")
        features = html.css(".innerDetail ul li ::text").getall()
        
        ad_item = AdItem()
        
        ad_item['title'] = html.css("title::text").get()
        ad_item['ad_type'] = html.css("#listing_type .current ::text").get()
        ad_item['latitude'] = lat_value
        ad_item['longitude'] = lon_value
        ad_item['price'] = price
        ad_item['area'] = area
        ad_item['available'] = available
        ad_item['furniture'] = furniture
        ad_item['energy_DPE'] = energy_DPE
        ad_item['energy_GES'] = energy_GES
        ad_item['description'] = description
        ad_item['features'] = features
        ad_item['url'] = response.url
        
        yield ad_item
        
    def extract_dpe_ges(self,texts): # list of strings
        l = []
        for t in texts:
            if ":" in t:
                x = t.split(":")
                for i in x:
                    if i.strip():
                        l.append(i.strip())
            else:
                l.append(t.strip())
        return l[1], l[3]