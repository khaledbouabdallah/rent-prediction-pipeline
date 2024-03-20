import scrapy
from scrapy_splash import SplashRequest

base_url = "https://www.seloger.com"
location_paris = 'list.htm?projects=1&types=2,1&places=[{"divisions":[2238]}]&sort=d_dt_crea&mandatorycommodities=0&enterprise=0&qsVersion=1.0&m=search_hp_last'
splash_url = "http://localhost:8050/render.html"


args = {
    'wait': 3,
    'headers': {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,fr;q=0.8,ar;q=0.7",
        "Cache-Control": "max-age=0",
        "Cookie": "__gtm_referrer=https%3A%2F%2Fduckduckgo.com%2F; ep-authorization=isDisconnected; sl-pdd_LD_UserId=df09c180-745a-456e-9ab8-f9fd8e2823db; didomi_token=eyJ1c2VyX2lkIjoiMThlMzQ2N2QtMjk1OS02ZThjLTg1NDktNjdjN2M1YjQxZTMxIiwiY3JlYXRlZCI6IjIwMjQtMDMtMTJUMjA6NDM6MjMuMTU3WiIsInVwZGF0ZWQiOiIyMDI0LTAzLTEyVDIwOjQzOjI5LjA5NloiLCJ2ZW5kb3JzIjp7ImVuYWJsZWQiOlsic2FsZXNmb3JjZSIsImdvb2dsZSIsImM6ZHYzNjAtbVJIZnFxaEciLCJjOnBlcnNvbmFsaXotTUVreVc2Mm0iLCJjOmZhY2Vib29rLUxmNlFrVTNIIiwiYzpnb29nbGVhbmEtUGdlWGpFbWsiLCJjOnlvdXR1YmUtOFQ2OENWN1YiLCJjOmludGVyY29tLXlCWjdrbnEzIiwiYzptYXBib3gtWkJSZVpaSE0iLCJjOmFsZ29saWEtZlVZTDJobVciLCJjOnBvbHlmaWxsLW"
}
}



class SelogerSpider(scrapy.Spider):
    
    name = 'seloger'
    #user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    start_urls = [base_url + '/' + location_paris]
    
    
    def start_requests(self):
        url = self.start_urls[0]
        yield SplashRequest(url, self.parse, args={'wait': 3})

    def parse(self, response):
        yield {'response': response}