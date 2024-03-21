# import scrapy
# from scrapy_splash import SplashRequest

# base_url = "https://www.seloger.com"
# location_paris = 'list.htm?projects=1&types=2,1&places=[{"divisions":[2238]}]&sort=d_dt_crea&mandatorycommodities=0&enterprise=0&qsVersion=1.0&m=search_hp_last'
# splash_url = "http://localhost:8050/render.html"


# args = {
#     'wait': 3,
#     'headers': {
#       "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)/"
#     }
# }



# class SelogerSpider(scrapy.Spider):
    
#     name = 'seloger'
#     #user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
#     start_urls = [base_url + '/' + location_paris]
    
    
#     def start_requests(self):
#         url = self.start_urls[0]
#         yield SplashRequest(url, self.parse, args={'wait': 3})

#     def parse(self, response):
#         yield {'response': response}