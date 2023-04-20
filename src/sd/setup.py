#!/usr/bin/python
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
from urllib.parse import unquote

import requests
from clint.textui import progress, puts, indent, colored

from .. import misc


class Config:
    class Segment:
        def __init__(self, root, segment, **kwargs):
            self.root = root
            self.description = segment["description"] if "description" in segment else "No description"
            self.dl = os.path.join(
                root.dl, segment["dl"] if "dl" in segment else "")
            self.sd = os.path.join(
                root.sd, segment["sd"] if "sd" in segment else "")

            if not os.path.exists(self.dl):
                os.makedirs(self.dl)  # create folder if it does not exist
            if not os.path.exists(self.sd):
                os.makedirs(self.sd)  # create folder if it does not exist

            self.component = []
            if "component" in segment:
                for c in segment["component"]:
                    self.component.append(self.Component(
                        self.root, c, dl=self.dl, sd=self.sd))

            self.ini = []
            if "ini" in segment:
                for ini in segment["ini"]:
                    self.ini.append(self.Ini(self.root, ini))

            self.external = []
            if "external" in segment:
                for ext in segment["external"]:
                    self.external.append(self.External(self.root, ext))
            # self.External(segment["external"]) if "external" in segment else []

        def build(self):
            misc.print_level1(s=(self.description))
            puts(s='Download path: '+self.dl)
            puts(s=' SD card path: '+self.sd)

            if (len(self.component) > 0):
                misc.print_level2(s=("Setup component(s)"))

                for (component) in (self.component):
                    component.download()
                    component.build()

            if (len(self.ini) > 0):
                misc.print_level2(s=("Create .ini file(s)"))
                for ini in self.ini:
                    ini.build()

            if (len(self.external) > 0):
                misc.print_level2(s=("Run custom script(s) from external file"))
                for ext in self.external:
                    ext.run()

        class External:
            def __init__(self, root, external, **kwargs):
                self.root = root
                self.path = external["path"] if "path" in external else "custom.py"
                self.description = external["description"] if "description" in external else ""
                self.function = external["function"] if "function" in external else None
                self.args = external["args"] if "args" in external else None

            def run(self):
                # Get path to mymodule
                script_dir = Path(__file__).parent
                mymodule_path = str(script_dir.joinpath('.', self.path))

                # Import mymodule
                loader = importlib.machinery.SourceFileLoader(
                    'custom', mymodule_path)
                spec = importlib.util.spec_from_loader('custom', loader)
                mymodule = importlib.util.module_from_spec(spec)
                loader.exec_module(mymodule)

                # Use mymodule
                with indent(indent=2, quote="-"):
                    if "description" in self.function:
                        puts(s=self.function["description"])
                    else:
                        puts(s="Custom function from external file")
                puts(s="Call " + self.function+"() in "+self.path)
                getattr(mymodule, self.function)(self.args)

        class Ini:
            def __init__(self, root, ini, **kwargs):
                self.root = root
                self.sd = os.path.join(
                    self.root.sd, ini["path"] if "path" in ini else "./"+str(uuid.uuid1())+".ini")
                self.description = ini["description"] if "description" in ini else "Create config.ini"
                self.line = ini["line"] if "line" in ini else []

            def build(self):
                with indent(indent=2):
                    misc.print_level3(s=("Create ")+self.sd)

                src = self.line
                dst = Path(self.sd)
                dst.parent.mkdir(parents=True, exist_ok=True)

                puts(s="Write "+str(len(src))+" lines(s) to "+str(dst))
                with open(dst, "w") as f:  # Opens file and casts as f
                    for (i, line) in enumerate(self.line):
                        # Writing
                        f.write(line + ("\n" if i < (len(self.line)-1) else ""))
                    # File closed automatically
                return

        class Component:
            class Github:
                def __init__(self, root, github, **kwargs):
                    self.root = root
                    self.repo = github["repo"] if "repo" in github else None
                    self.query = github["query"] if "query" in github else "releases/latest"
                    self.regex = github["regex"] if "regex" in github else []

            def __init__(self, root, component: dict({}), **kwargs):
                self.root = root
                self.name = component['name'] if 'name' in component else ""
                self.description = component['description'] if "description" in component else ""

                self.github = self.Github(
                    self.root, component["github"]) if "github" in component else None
                self.url = component['url'] if "url" in component else ""
                self.regex = component['regex'] if "regex" in component else []
                self.is_disabled = component['isDisabled'] if 'isDisabled' in component else False

                self.dl = os.path.join(kwargs["dl"] if "dl" in kwargs else "")
                self.sd = os.path.join(kwargs["sd"] if "sd" in kwargs else "")

                if not os.path.exists(self.dl):
                    os.makedirs(self.dl)  # create folder if it does not exist
                if not os.path.exists(self.sd):
                    os.makedirs(self.sd)  # create folder if it does not exist

                self.filename = list([])

            def download(self):

                if len(self.name) > 0:
                    with indent(indent=2):
                        misc.print_level3(s=("- Download ")+self.name)

                if len(self.description) > 0:
                    puts(s=self.description)

                if self.is_disabled:
                    puts(s="Skip as config!")
                    return

                if self.github is not None:
                    puts(s="Repo: github/"+self.github.repo)
                    self.filename = misc.download_github(repo = self.github.repo, query = self.github.query, regex=self.github.regex, dst=self.dl)
                    # self.download_from_github()
                elif len(self.url) > 0:
                    puts(s="URL: "+self.url)
                    self.filename = misc.download(url = self.url, dst = self.dl)
                    # self.download_from_url()
                return

            def build(self):
                for file in self.filename:
                    full_path = os.path.join(self.dl, file)
                    src = Path(full_path)
                    if file.endswith(".zip"):
                        misc.unzip(
                            src=src,
                            dst=self.root.sd
                        )
                    elif (src.suffix in [".bin", ".nro", ".config", ".ovl"]):
                        misc.copy(
                            src=src,
                            dst=self.sd
                        )
                    else:
                        misc.print_error(s=(" => Unknown file type. Skip!"))
                return

    class Root(object):
        def __init__(self, config: dict()):
            self.dl = config["dl"] if "dl" in config else ""
            self.sd = config["sd"] if "sd" in config else ""
            self.tab = config["tab"] if "tab" in config else 2
            self.description = config["description"] if "description" in config else ""

    def __init__(self, root, config):

        self.root = self.Root(root)

        misc.print_header(s=('> '+self.root.description+' <'))
        misc.print_header(s=('> Download: '+self.root.dl+' <'))
        misc.print_header(s=('>  SD card: '+self.root.sd+' <'))

        self.seg = []
        for (name, config) in config.items():
            if name in ["root"]:
                continue
            else:
                self.seg.append(self.Segment(self.root, config))
                # s.build()

    def build(self):
        print("Auto setup sd-card as config in: ", self.root.sd)

        try:
            misc.print_level1(s=("Clean previous build in "+self.root.sd))
            shutil.rmtree(os.path.join(self.root.sd))
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

        for (index, seg) in enumerate(self.seg):
            misc.print_level2(s=(str(index+1)+". "), newline=False)
            seg.build()


def run(root, cfg):
    config = Config(root, cfg)
    config.build()
