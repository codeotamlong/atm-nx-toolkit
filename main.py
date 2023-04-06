# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import re
import os
import zipfile
import shutil
import uuid
import importlib.machinery
import importlib.util
from string import Template
from pathlib import Path

import requests
from clint.textui import progress, puts, indent, colored

class Segment:
    def __init__(self, segment:dict(), **kwargs):
        self.description = segment["description"] if "description" in segment else "No description"
        
        self.dl_parent = kwargs["dl_parent"] if "dl_parent" in kwargs else "./download"
        self.dl_path = os.path.join(self.dl_parent, segment["dl_path"] if "dl_path" in segment else "")
        self.sd_parent = kwargs["sd_parent"] if "sd_parent" in kwargs else "./sdcard"
        self.sd_path = os.path.join(self.sd_parent, segment["sd_path"] if "sd_path" in segment else "")
        
        if not os.path.exists(self.dl_path):
            os.makedirs(self.dl_path)  # create folder if it does not exist
        if not os.path.exists(self.sd_path):
            os.makedirs(self.sd_path)  # create folder if it does not exist

        self.component = []
        if "component" in segment:
            for c in segment["component"]:
                self.component.append(self.Component(c, dl_parent=self.dl_path, sd_parent=self.sd_path))

        self.ini = []
        if "ini" in segment:
            for ini in segment["ini"]:
                self.ini.append(self.Ini(ini, sd_parent=self.sd_path))

        self.external = self.External(segment["external"]) if "external" in segment else None

    def build(self):
        puts(s=colored.blue(self.description))
        puts(s='Download path: '+self.dl_path)
        puts(s=' SD card path: '+self.sd_path)

        puts(s=colored.cyan("Download component(s)"))
        for component in self.component:
            component.download()

        if (len(self.component) > 0):
            puts(s=colored.cyan("Build SD Card"))

            for item in (os.listdir(self.dl_path)):
                full_path = os.path.join(self.dl_path, item)
                src = Path(full_path)
                with indent(indent=TAB):
                    puts(s=colored.yellow("Extract " if src.suffix == ".zip" else "Move ") +
                        src.name+" to "+sd_path)
                    if item.endswith(".zip"):
                        zip_obj = zipfile.ZipFile(src)  # create zipfile object
                        zip_obj.extractall(sd_path)  # extract file to dir
                        zip_obj.close()
                    elif (src.suffix in [".bin", ".nro", ".config", ".ovl"]):
                        shutil.copy(src, os.path.join(self.sd_path, item))
                        if os.path.isfile(os.path.join(self.sd_path, item)):
                            puts(s=colored.green(("=> Success")))
                    else:
                        puts(s=colored.red("=> Unknown file type. Skip!"))

        if (len(self.ini) > 0):
            puts(s=colored.cyan("Create .ini file(s)"))
            for ini in self.ini:
                ini.build()

        if (self.external is not None):
            puts(s=colored.cyan("Run custom script(s) from external file"))
            self.external.run()

    class External:
        def __init__(self, external:dict(), **kwargs):
            self.path = external["path"] if "path" in external else "custom.py"
            self.function = []
            if "function" in external:
                for f in external["function"]:
                    self.function.append(f)
            pass

        def run(self):
            # Get path to mymodule
            script_dir = Path( __file__ ).parent
            mymodule_path = str( script_dir.joinpath( '.', self.path ) )

            # Import mymodule
            loader = importlib.machinery.SourceFileLoader( 'custom', mymodule_path )
            spec = importlib.util.spec_from_loader( 'custom', loader )
            mymodule = importlib.util.module_from_spec( spec )
            loader.exec_module( mymodule )

            # Use mymodule
            for f in self.function:
                with indent(indent=TAB, quote="-"):
                    if "description" in f:
                        puts(s=f["description"])
                    else:
                        puts(s="Custom function from external file")
                puts(s="Call "+f["name"]+"() in custom.py")
                getattr(mymodule, f["name"])(f["args"] if "args" in f else None)
            pass
    
    class Ini:
        def __init__(self, ini:dict, **kwargs):

            self.sd_parent = kwargs["sd_parent"] if "sd_parent" in kwargs else "./sdcard"
            self.sd_path = os.path.join(self.sd_parent, ini["path"] if "path" in ini else "./"+str(uuid.uuid1())+".ini")
            
            self.description = ini["description"] if "description" in ini else "Create config.ini"
            self.line = ini["line"] if "line" in ini else []

        def build(self):
            with indent(indent=TAB,):
                puts(s=colored.green("Create ")+self.sd_path)

            src=self.line
            dst = Path(self.sd_path)
            dst.parent.mkdir(parents=True, exist_ok=True)

            puts(s="Write "+str(len(src))+" lines(s) to "+str(dst))
            with open(dst, "w") as f:  # Opens file and casts as f
                for (i, line) in enumerate(self.line):
                    f.write(line + ("\n" if i<(len(self.line)-1) else ""))  # Writing
                # File closed automatically
            return

    class Component:
        class Github:
            def __init__(self, github:dict(), **kwargs):
                self.repo = github["repo"] if "repo" in github else None
                self.query = github["query"] if "query" in github else "releases/latest"
                self.regex = github["regex"] if "regex" in github else []

        def __init__(self, component:dict({}), **kwargs):
            self.name = component['name'] if 'name' in component else ""
            self.description = component['description'] if "description" in component else ""

            self.github = self.Github(component["github"]) if "github" in component else None
            self.url = component['url'] if "url" in component else ""
            self.regex = component['regex'] if "regex" in component else []
            self.is_disabled = component['isDisabled'] if 'isDisabled' in component else False
            
            self.dl_parent = kwargs["dl_parent"] if "dl_parent" in kwargs else "./download"
            self.dl_path = os.path.join(self.dl_parent, component["dl_path"] if "dl_path" in component else "")
            self.sd_parent = kwargs["sd_parent"] if "sd_parent" in kwargs else "./sdcard"
            self.sd_path = os.path.join(self.sd_parent, component["sd_parent"] if "sd_parent" in component else "")
            if not os.path.exists(self.dl_path):
                os.makedirs(self.dl_path)  # create folder if it does not exist
            if not os.path.exists(self.sd_path):
                os.makedirs(self.sd_path)  # create folder if it does not exist

            self.filename = ""

        def download(self):
            if len(self.name) > 0:
                with indent(indent=TAB):
                    puts(s=colored.yellow("Download ")+self.name)
            
            if len(self.description) > 0:
                puts(s=self.description)

            if self.is_disabled:
                puts(s="Skip as config!")
                return

            if self.github is not None :
                puts(s="Repo: github/"+self.github.repo)
                self.download_from_github()
            elif len(self.url) > 0:
                puts(s="URL: "+self.url)
                self.download_from_url()
            return

        def download_from_url(self, **kwargs):
            url = kwargs["url"] if "url" in kwargs else self.url
            self.filename = url.split('/')[-1].replace(" ", "_")
            
            dst = kwargs["dst"] if "dst" in kwargs else os.path.join(self.dl_path, self.filename)

            r = requests.get(url, stream=True)
            if r.ok:
                puts(s="Save "+self.filename+" to "+dst)
                with open(dst, 'wb') as f:
                    total_length = int(r.headers.get('content-length'))
                    for chunk in progress.bar(r.iter_content(chunk_size=2391975), expected_size=(total_length/1024) + 1):
                        # for chunk in r.iter_content(chunk_size=1024 * 8):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                            os.fsync(f.fileno())
            else:  # HTTP status code 4XX/5XX
                print("Download failed: status code {}\n{}".format(r.status_code, r.text))
            return
        
        def download_from_github(self):
            if not os.path.exists(self.dl_parent):
                os.makedirs(self.dl_parent)  # create folder if it does not exist

            puts(s="API URL: "+self.get_github_api_url())

            response = requests.get(self.get_github_api_url())
            res_data = response.json() if response and response.status_code == 200 else None

            if "assets" in res_data:
                for assets in res_data["assets"]:
                    puts(s="Found "+assets["name"]+": "+assets["browser_download_url"])
                    for p in self.github.regex:
                        puts(s="Test regex"+p)
                        pattern = re.compile(p)
                        if pattern.match(assets["name"]):
                            puts(s=" => Match! Download: "+assets["name"])
                            puts(s="URL: "+assets["browser_download_url"])
                            self.download_from_url(url=assets["browser_download_url"])
                        else:
                            puts(s="=> Not Match. Skip!")

        def get_github_api_url(self):
            api_template = Template(
                "https://api.github.com/repos/$repo/$query")
            url = api_template.substitute({
                'repo': self.github.repo,
                'query': self.github.query
            })
            return url


def main():
    return


if __name__ == '__main__':
    TAB = 2

    with open('config.json', 'r') as config_file:
        CONFIG = json.load(config_file)
    if "master" in CONFIG:
        dl_path = os.path.join(CONFIG["master"]["dl_path"] if ("dl_path" in CONFIG["master"]) else "./download")
        sd_path = os.path.join(CONFIG["master"]["sd_path"] if ("sd_path" in CONFIG["master"]) else "./sdcard")
        puts(colored.magenta('> '+CONFIG["master"]["description"]+' <'))
        puts(colored.magenta('> Download: '+dl_path+' <'))
        puts(colored.magenta('>  SD card: '+sd_path+' <'))

        # Try to remove the tree; if it fails, throw an error using try...except.
        try:
            puts(s=colored.blue("Clean previous build in "+sd_path))
            shutil.rmtree(os.path.join(sd_path))
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

        index = 0
        for (name, config) in CONFIG.items():
            if name in ["master"]:
                continue
            else:
                index+=1
                puts(s=colored.blue("Step "+str(index)+". "), newline="")
                segment = Segment(config, dl_parent=dl_path, sd_parent=sd_path)
                segment.build()