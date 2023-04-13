import os
import re
from pathlib import Path
from urllib.parse import unquote
import requests
from clint.textui import progress, puts, indent, colored

def print_header(s, newline=True):
    puts(s=colored.magenta(s), newline=newline)

def print_level1(s, newline=True):
    puts(s=colored.blue(s), newline=newline)

def print_level2(s, newline=True):
    puts(s=colored.cyan(s), newline=newline)

def print_level3(s, newline=True):
    puts(s=colored.green(s), newline=newline)

def print_result(s, newline=True):
    puts(s=colored.yellow(s), newline=newline)


def download(url, dst="."):

    filename = url.split('/')[-1].replace(" ", "_")

    dst = os.path.join(
        dst, filename)

    r = requests.get(unquote(url), stream=True)
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


def download_from_github(repo, query, regex):

    response = requests.get(get_github_api_url(repo, query))
    res_data = response.json() if response and response.status_code == 200 else None

    if "assets" in res_data:
        for assets in res_data["assets"]:
            for p in regex:
                pattern = re.compile(p)
                if pattern.match(assets["name"]):
                    puts(s=colored.yellow("Download: ")+assets["name"])
                    download(url=unquote(assets["browser_download_url"]))


def get_github_api_url(repo, query):
    api_template = Template(
        "https://api.github.com/repos/$repo/$query")
    url = api_template.substitute({
        'repo': repo,
        'query': query
    })
    return url
