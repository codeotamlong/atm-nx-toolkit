import os
import re
from pathlib import Path
import urllib
from string import Template
import pyunpack

from urllib.parse import unquote
import requests
from clint.textui import progress, puts, indent, colored, prompt,validators, columns

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

def print_clean(s, newline=True):
    puts(s=colored.clean(s), newline=newline)

def get_single_selection(question="What would you like to do?", options=[], answer="Select", default=None, two_column=False):
    class Choice:
        def __init__(self, option):
            self.selector = str(option["selector"])
            self.desc = option["desc"]
            self.return_ = option["return"]

        def show(self, placeholder=0):
            puts(s=("[%*s] %s") %(placeholder, self.selector, self.desc))

        def get_command(self):
            return ("[%s] %s") %(self.selector, self.desc)
    

    puts(s=question)
    o_list = []
    input_list = []
    for o in options:
        choice_obj = Choice(o)
        o_list.append(choice_obj)
        input_list.append(choice_obj.selector)

    if two_column:
        index = 0
        while index < len(o_list)-1:
            puts(columns(
                [(o_list[index].get_command()), 45],
                [o_list[index+1].get_command(), 45]
            ))
            index += 2
    else:
        for o in o_list:
            puts(s=o.get_command())
    
    choice = None
    while choice not in input_list:
        choice = prompt.query(answer, default=default)

    for o in o_list:
        if o.selector == choice:
            return o.return_

def get_multiple_selection(question="What would you like to do?", options=[], answer="Select", default=None, two_column=False):
    class Choice:
        def __init__(self, option):
            self.selector = str(option["selector"])
            self.desc = option["desc"]
            self.return_ = option["return"]

        def show(self, placeholder=0):
            puts(s=("[%*s]%s") %(placeholder, self.selector, self.desc))

        def get_command(self, placeholder=0):
            return ("[%*s] %s") %(placeholder, self.selector, self.desc)
    

    puts(s=question)
    opt_list = []
    input_list = []
    for o in options:
        choice_obj = Choice(o)
        opt_list.append(choice_obj)
        # input_list.append(choice_obj.selector)

    input_list = [o.selector for o in opt_list]
    ret_list = [o.return_ for o in opt_list]
    
    if two_column:
        index = 0
        width = 0
        for o in opt_list:
            if len(o.desc) > width:
                width = len(o.desc)
        width -= 5
        while index < len(opt_list)-1:
            puts(columns(
                [opt_list[index].get_command(), width],
                [opt_list[index+1].get_command(), None]
            ))
            index += 2
    else:
        for o in opt_list:
            o.show()
    
    choice = ''
    while not all([x in input_list for x in choice]) or (len(choice) < 1):
        choice = prompt.query(answer, default=default)
        choice = choice.split(" ")
        for c in choice:
            print(c)
            if '-' in c:
                cc = c.split("-")
                for ccc in range(int(cc[0]), int(cc[1])+1):
                    choice.append(str(ccc))
                choice.remove(c)
        if 'all' in choice:
            choice = input_list
        

    ret = []
    for c in choice:
        ret.append([x for x in opt_list if x.selector == c][0].return_)
    # print (ret)
    return ret

'''
DOWNLOAD
'''

def download(url, dst="."):

    
    ret = []

    r = requests.get(unquote(url), stream=True)
    if r.ok:
        filename = url.split('/')[-1].replace(" ", "_")
        dst = Path(dst).joinpath(filename)
        dst.parent.mkdir(parents=True, exist_ok=True)
        puts(s="[No progress bar] Save "+filename+" to "+str(dst))
        ret.append(filename)
        with open(dst, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=2391975), expected_size=(total_length/1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        print_success(s="Downloaded success to %s"%dst)
    else:  # HTTP status code 4XX/5XX
        print_error("Download failed: status code {}\n{}".format(
            r.status_code, r.text))

    return ret

def download_raw(url,filename, dst="."):
    ret = []

    r = requests.get(unquote(url), stream=True, allow_redirects=True)
    if r.ok:
        if filename is None:
            filename = url.split('/')[-1].replace(" ", "_")
        dst = Path(dst).joinpath(filename)
        dst.parent.mkdir(parents=True, exist_ok=True)
        puts(s="[No progress bar] Save "+filename+" to "+str(dst))
        ret.append(filename)
        with open(dst, 'wb') as f:
           for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        print_success(s="Downloaded success to %s"%dst)
    else:  # HTTP status code 4XX/5XX
        print_error("Download failed: status code {}\n{}".format(
            r.status_code, r.text))

    return ret

def download_urllib(url, dst):
    url = unquote(url)
    # print(url)
    # urllib.request.urlretrieve(url, dst)
    print(url)
    response = urllib.request.urlopen(url)
    file = open(dst, 'wb')
    file.write(response.read())
    file.close()
    print("Completed")
        
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

'''
WRITE FILE
'''
def write(src=[], dst="temp.txt"):

    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dst, "w") as f:  # Opens file and casts as f
        if type(src) is str:
            print_warning(s="Print %s char(s) to %s"%(len(src), dst))
            f.write(src)
        elif type(src) is list:
            print_warning(s="Print %s line(s) to %s"%(len(src), dst))
            for (i, line) in enumerate(src):
                f.write(line + ("\n" if i < (len(src)-1) else ""))

'''
UNPACK
'''

def unrar(src, dst="."):
    pyunpack.Archive(src).extractall(dst)