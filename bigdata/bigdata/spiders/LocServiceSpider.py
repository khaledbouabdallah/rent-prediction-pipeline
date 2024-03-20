import scrapy

class LocServiceSpider(scrapy.Spider):
    name = "loc_service"
    start_urls = [
       "https://www.locservice.fr/location-carte.html" 
    ]

    def parse(self, response):
        # Add your parsing logic here
        pass
    
    
class LocServiceSpider_departements(scrapy.Spider):
    # Spider to get the urls of the departements
    name = "loc_service_departements"
    allowed_domains = ['locservice.fr']
    start_urls = ['https://www.locservice.fr/location-carte.html']
   

    def parse(self, response):
        # Add your parsing logic here
        departements_urls = response.css("area").xpath("@href").getall()
        print(len(departements_urls))
        for url in departements_urls:
            splits = url.split("/")[1].split("-")
            yield {
                'nom': "-".join(splits[:-1]),
                'number': splits[-1],
                'url': url,
            }
            