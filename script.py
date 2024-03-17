import requests
from bs4 import BeautifulSoup

base_url = "https://www.seloger.com"
location_paris = 'list.htm?projects=1&types=2,1&places=[{"divisions":[2238]}]&sort=d_dt_crea&mandatorycommodities=0&enterprise=0&qsVersion=1.0&m=search_hp_last'
splash_url = "http://localhost:8050/render.html"

r = requests.get(splash_url, params={'url': base_url + '/' + location_paris, 'wait': 3})
print(r.status_code)
print(r.content)
soup = BeautifulSoup(r.content, 'html.parser')

