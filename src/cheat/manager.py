import os
import json
import re
import shutil
from unidecode import unidecode
from pathlib import Path
from bs4 import BeautifulSoup
from clint.textui import prompt, validators

from .. import misc

class CheatList:
    class Cheat:
        def __init__(self, string):
            # print(string)
            lines = string.split("\n")
            self.address = []
            for (i, line) in enumerate(lines):
                if i==0:
                    self.desc = line
                else:
                    self.address.append(line)
            # print(self.desc)


    def __init__(self, textfile):
        with open(Path(textfile), encoding="utf8",mode= 'r') as cheat:
            lines = cheat.read().split("\n\n")
        self.cheat = []
        for (i, line) in enumerate(lines):
            if i==0:
                self.desc = line
            else:
                self.cheat.append(self.Cheat(line))
def main(config):
    choice = misc.get_choice(
        question="Select your work",
        options=[
            {"desc": "Update Title ID", "selector":1, "return":"update-title-id"},
            {"desc": "Update cheatcode database", "selector":2, "return":"update-cheatcode-db"},
            {"desc": "Search by name", "selector":3, "return":"search-by-name"},
            {"desc": "open by Title ID", "selector":4, "return":"open-by-tid"}
        ]
    )

    if choice == "update-title-id":
        tid_data = config["cheat-mng"]["title-db"]
        misc.print_level3(s=tid_data["desc"])
        misc.download_raw(url=tid_data["url"], filename="title_full.json", dst=os.path.join(config["dl"], tid_data["dst"]))
        with open(Path("./download/db/title_full.json"), encoding="utf8",mode= 'r') as config_file:
            tid_db = json.load(config_file)["data"]

        try:
            with open('./download/db/titleid.json', encoding="utf8",mode='w') as f:
                f.write("[\n")
                for (i, tid) in enumerate(tid_db):
                    f.write("  {\n")

                    title = unidecode(BeautifulSoup(markup=tid["name"],features="html.parser").a.text.replace('\n', ' ').replace('\r', '').replace('"', "'"))
                    title = re.sub('[^A-Za-z0-9\s]+','',title)
                    # f.write('    "%s":"%s"'%(tid["id"], title))
                    f.write('    "id":"%s",\n'%(tid["id"]))
                    f.write('    "title":"%s"\n'%(title))
                    if (i<len(tid_db)-1):
                        f.write('  },\n')
                    else:
                        f.write('  }\n')
                f.write("]")
                
        except FileNotFoundError:
            print("The 'docs' directory does not exist")
        
        # misc.download_urllib(url=tid_data["url"], dst=os.path.join(config["dl"], tid_data["dst"], "title.rar"))
    elif choice == "update-cheatcode-db":
        tid_data = config["cheat-mng"]["cheat-db"]
        misc.print_level3(s=tid_data["desc"])
        misc.download_raw(url=tid_data["url"], filename="title.rar", dst=os.path.join(config["dl"], tid_data["dst"]))
        misc.unrar(src=os.path.join(config["dl"], tid_data["dst"],"title.rar"), dst=os.path.join(config["dl"], tid_data["dst"]))
    elif choice == "search-by-name":
        tid_data = config["cheat-mng"]["cheat-db"]
        cheat_db = os.path.join(config["dl"], tid_data["dst"], "titles")
        filenames= os.listdir (cheat_db) # get all files' and folders' names in the current directory

        result = []
        for filename in filenames: # loop through all the files and folders
            if os.path.isdir(os.path.join(cheat_db, filename)): # check whether the current object is a folder or not
                result.append(filename)
        
        with open(Path("./download/db/titleid.json"), encoding="utf8",mode= 'r') as config_file:
            tid_db = json.load(config_file)

        misc.print_level3(s="There are %s/%s title id has cheat"%(len(result), len(tid_db)))

        qarg = prompt.query('Game name:')
        query = qarg.split(" ")
        found_by_name = []
        for tid in tid_db:
            if all([x.lower() in tid["title"].lower() for x in query]):
                found_by_name.append(tid)

        options = []
        # options.append({'selector':i, "desc":"Copy all", "return":"all"}) 
        for (index,tid) in enumerate(found_by_name):
            options.append({'selector':index+1, "desc":"[%s] %s"%(tid["id"],tid["title"]), "return":tid["id"]})
        selected_tid = misc.get_choice(options=options)

        if selected_tid == "all":
            pass
            # tid = prompt.query('Title ID:')
            # shutil.copytree(
            #     src=Path("./download/db/titles/%s/"%(tid)),
            #     dst=Path("./sdcard/atmosphere/contents/%s/"%(tid))
            #     )
            # print ("Copy all to sdcard/atmospshere/contents/%s"%(tid))
        else:
            # result = []
            filenames= os.listdir (Path("./download/db/titles/%s/cheats/"%(selected_tid)))
            options=[]
            index = 0
            for filename in filenames: # loop through all the files and folders
                if os.path.isfile(os.path.join(Path("./download/db/titles/%s/cheats/"%(selected_tid)), filename)): # check whether the current object is a folder or not
                    # cheat = CheatList(os.path.join(Path("./download/db/titles/%s/cheats/"%(x)), filename))
                    with open(os.path.join(Path("./download/db/titles/%s/cheats/"%(selected_tid)), filename), encoding="utf8",mode= 'r') as cheat:
                        index+=1
                        lines = cheat.read().split("\n\n")
                        options.append({"selector":index, "desc":lines[0], "return":filename})
            selected_version = misc.get_choice(options=options)
            with open(os.path.join(Path("./download/db/titles/%s/cheats/"%(selected_tid)), selected_version), encoding="utf8",mode= 'r') as cheat:
                cheat = CheatList(os.path.join(Path("./download/db/titles/%s/cheats/"%(selected_tid)), filename))
                print(cheat.desc)
            # print(result)

    elif choice == "open-by-tid":
        tid = prompt.query('Title ID:')
        result = []
        filenames= os.listdir (Path("./download/db/titles/%s/cheats/"%(tid)))
        for filename in filenames: # loop through all the files and folders
            if os.path.isfile(os.path.join(Path("./download/db/titles/%s/cheats/"%(tid)), filename)): # check whether the current object is a folder or not
                result.append(filename)
        # with open(Path("./download/db/titles/%s/cheats/%s.txt"%(tid, tid)), encoding="utf8",mode= 'r') as config_file:
        #     contents = config_file.read()
        #     print(contents)
        print(result)
        
