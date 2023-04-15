import os
import re
from pathlib import Path
from string import Template

from urllib.parse import unquote
import requests
from clint.textui import progress, puts, indent, colored, prompt,validators

'''
### CLI BEAUTY
'''
def print_header(s, newline=True):
    puts(s=colored.magenta(s), newline=newline)

def print_level1(s, newline=True):
    puts(s=colored.cyan(s), newline=newline)

def print_level2(s, newline=True):
    puts(s=colored.blue(s), newline=newline)

def print_level3(s, newline=True):
    puts(s=colored.black(s), newline=newline)

def print_success(s, newline=True):
    puts(s=colored.green(s), newline=newline)

def print_warning(s, newline=True):
    puts(s=colored.yellow(s), newline=newline)

def print_error(s, newline=True):
    puts(s=colored.red(s), newline=newline)

def get_choice(question="What would you like to do?", options=[], answer="What would you like to do?", default=None):
    class Choice:
        def __init__(self, option):
            self.selector = str(option["selector"])
            self.desc = option["desc"]
            self.return_ = option["return"]

        def show(self, placeholder=0):
            puts(s=("[%*s]%s") %(placeholder, self.selector, self.desc))
    
    puts(s=question)
    o_list = []
    input_list = []
    for o in options:
        choice_obj = Choice(o)
        o_list.append(choice_obj)
        input_list.append(choice_obj.selector)

    for o in o_list:
        o.show()
    
    choice = None
    while choice not in input_list:
        choice = prompt.query(answer, default=default)

    for o in o_list:
        if o.selector == choice:
            return o.return_

'''
DOWNLOAD
'''

def download(url, dst="."):

    filename = url.split('/')[-1].replace(" ", "_")
    dst = os.path.join(dst, filename)
    ret = []

    r = requests.get(unquote(url), stream=True)
    if r.ok:
        puts(s="Save "+filename+" to "+dst)
        ret.append(filename)
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

    return ret


def download_github(repo, query, regex, dst="."):
    
    response = requests.get(get_github_api_url(repo, query))
    res_data = response.json() if response and response.status_code == 200 else None
    ret = []

    if "assets" in res_data:
        for assets in res_data["assets"]:
            for p in regex:
                pattern = re.compile(p)
                if pattern.match(assets["name"]):
                    ret.append(assets["name"])
                    puts(s=colored.yellow("Download: ")+assets["name"])
                    download(url=unquote(assets["browser_download_url"]), dst=dst)
    
    return ret


def get_github_api_url(repo, query):
    api_template = Template(
        "https://api.github.com/repos/$repo/$query")
    url = api_template.substitute({
        'repo': repo,
        'query': query
    })
    return url
