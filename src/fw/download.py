import requests
import os
import webbrowser
from bs4 import BeautifulSoup
from urllib.parse import unquote
from clint.textui import progress, puts, indent, colored


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
        download(url)
    else:
        webbrowser.open(url)

def download(url):
    filename = url.split('/')[-1].replace(" ", "_")

    dst = os.path.join(".", filename)

    r = requests.get(url, stream=True)
    if r.ok:
        puts(s="Save "+filename+" to "+dst)
        with open(dst, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=2391975), expected_size=(total_length/1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(
            r.status_code, r.text))
    return

def run(url, class_):
    # url = 'https://darthsternie.net/switch-firmwares/'
    dt = Scraper(url=url)
    dt.fetch(class_) 
    return dt
    


