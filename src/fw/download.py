import requests
import os
import webbrowser
from bs4 import BeautifulSoup
from urllib.parse import unquote
from clint.textui import progress, puts, indent, colored

from .. import misc

class Scraper:
    class Firmware:
        def __init__(self, data):
            self.version = data["version"]
            self.md5 = data["md5"]
            self.filesize = data["filesize"]
            self.mega_nz = data["mega_nz"]
            self.archive_org = data["archive_org"]
            pass

    def __init__(self, url):
        self.url = url
        self.class_ = ""
        self.firmware = []

    def fetch(self, class_):
        self.class_ = class_
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_ = class_)

        for t in table.find_all('tbody'):
            rows = t.find_all('tr')
            for row in rows:
                fw = {
                    "version": row.find_all('td')[0].text,
                    "md5": row.find_all('td')[1].text,
                    "filesize": row.find_all('td')[2].text,
                    "mega_nz": row.find_all('td')[3].a["href"],
                    "archive_org": row.find_all('td')[4].a["href"],
                }
                self.firmware.append(self.Firmware(fw))

def open_(url):
    url = unquote(url)
    
    if ("archive.org" in url) and (url.endswith(".zip")):
        misc.download(url)
    else:
        webbrowser.open(url)
        misc.print_warning(s="If web-browser not open, you might want to open url manually:")
        misc.print_level2(s=url)

def run(url, class_):
    dt = Scraper(url=url)
    dt.fetch(class_) 
    return dt
    


