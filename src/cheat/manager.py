import os
import json
import re
from string import Template
from pathlib import Path
from unidecode import unidecode
from bs4 import BeautifulSoup
from clint.textui import prompt, validators, indent

from .. import misc

class CheatList:
    class Cheat:
        def __init__(self, cheat_obj):
            self.desc = cheat_obj["desc"]
            self.patch = cheat_obj["patch"]


    def __init__(self, textfile):
        with open(Path(textfile), encoding="utf8",errors='ignore', mode= 'r') as f:
            lines = f.readlines()
        self.cheat = []

        cheat_obj = dict({
            "desc": "",
            "patch": []
        })
        re_header = re.compile(r"\[(.*)*?\]")
        re_patch = re.compile(r"([0-9a-fA-F]){8}")
        for l in lines:
            l = l.strip()
            if re_header.match(l):
                if re_header.match(cheat_obj["desc"]):
                    self.cheat.append(self.Cheat(cheat_obj))
                    cheat_obj = dict({
                        "desc": "",
                        "patch": []
                    })
                cheat_obj["desc"] = l
            elif re_patch.match(l):
                cheat_obj["patch"].append(l)
        self.cheat.append(self.Cheat(cheat_obj))

        self.desc = []
        for ch in self.cheat:
            if len(ch.patch) < 1:
                self.desc.append(ch.desc)
                self.cheat.remove(ch)

    def show_cheat_desc(self):
        for d in self.desc:
            print(d)

    def get_cheat_list(self):
        return self.cheat


def main(config):
    options = []
    cheat_cfg = config["cheat-mng"]["cheat-db"]
    cheat_sd_dir = Template(os.path.join(config["sd"], config["cheat-mng"]["sd"]))
    title_cfg = config["cheat-mng"]["title-db"]

    if not Path(title_cfg["dst"]).joinpath(title_cfg["db"]).exists():
        options.append({"desc": "Not Found Title ID <<< MUST RUN", "selector":1, "return":"update-title-id"})
    else:
        with open(Path(title_cfg["dst"]).joinpath(title_cfg["download"]), encoding="utf8", errors='ignore', mode= 'r') as f:
            tinfoil_db = json.load(f)["data"]
        options.append({"desc": "Update Title ID (Currently: %s)"%(len(tinfoil_db)), "selector":1, "return":"update-title-id"})

    cheat_dir = Path(cheat_cfg["dst"]).joinpath("titles")
    if (not cheat_dir.exists()) or (len(os.listdir (cheat_dir)) < 1):
        options.append({"desc": "Not Found Cheat <<< MUST RUN", "selector":2, "return":"update-cheatcode-db"})
    else:
        options.append({"desc": "Update cheatcode (Currently: %s)"%(len(os.listdir (cheat_dir))), "selector":2, "return":"update-cheatcode-db"})

    
    options.append({"desc": "Search by name", "selector":3, "return":"search-by-name"})
    options.append({"desc": "Open by Title ID", "selector":4, "return":"open-by-tid"})
    options.append({"desc": "Batch cheat copy", "selector":5, "return":"batch-copy-all"})
    choice = misc.get_single_selection(
        question="Select your work",
        options=options,
        two_column=True
    )

    if choice == "update-title-id":
        misc.print_level3(s=title_cfg["desc"])
        misc.download_raw(
            url=title_cfg["url"], 
            filename=title_cfg["download"], 
            dst=Path(title_cfg["dst"])
        )
        with open(Path(title_cfg["dst"]).joinpath(title_cfg["download"]), encoding="utf8", errors='ignore', mode= 'r') as f:
            tinfoil_db = json.load(f)["data"]

        try:
            title_id_db = []
            title_id_file = Path(title_cfg["dst"]).joinpath(title_cfg["db"])
            for (i, tid) in enumerate(tinfoil_db):
                title = unidecode(BeautifulSoup(markup=tid["name"],features="html.parser").a.text.replace('\n', ' ').replace('\r', ''))
                title_id_db.append({
                    "id": tid["id"],
                    "title": title
                })
            misc.write(src=json.dumps(title_id_db, ensure_ascii=False), dst=title_id_file)
        except FileNotFoundError:
            print("The 'docs' directory does not exist")

    elif choice == "update-cheatcode-db":
        cheat_cfg = config["cheat-mng"]["cheat-db"]
        misc.print_level3(s=cheat_cfg["desc"])
        # misc.download_raw(
        #     url=cheat_cfg["url"], 
        #     filename=cheat_cfg["download"],
        #     dst=Path(cheat_cfg["dst"])
        # )
        downloaded_cheat = Path(cheat_cfg["dst"]).joinpath(cheat_cfg["download"])
        # try:
        unrar_success = True
        for ur_path in config["unrar"]:
            unrar_success = misc.unrar(src=downloaded_cheat, dst=Path(cheat_cfg["dst"]), unrar_path=ur_path)
            if unrar_success:
                break
        if not unrar_success:
            misc.print_error(s="Cannot extract %s"%(downloaded_cheat))
            misc.print_error(s="You might want extract manually %s"%(downloaded_cheat))
            misc.print_clean(s="Properly structure %s/titles/[TIDs]/cheats/[BIDs].txt - Eg:"%(cheat_cfg["dst"]))
            misc.print_clean(s="%s"%(cheat_cfg["dst"]))
            misc.print_clean(s="  |-titles\\")
            misc.print_clean(s="    |-0123456789ABCDEA\\")
            misc.print_clean(s="      |-cheats\\")
            misc.print_clean(s="        |-ABCDEF9876543210.txt")
            misc.print_clean(s="        |-ABCDEF9876543211.txt")
            misc.print_clean(s="          |-..\\")
            misc.print_clean(s="    |-0123456789ABCDEB\\")
            misc.print_clean(s="      |-cheats\\")
            misc.print_clean(s="        |-ABCDEF9876543210.txt")
            misc.print_clean(s="        |-ABCDEF9876543211.txt")
            misc.print_clean(s="        |-..\\")
            misc.print_clean(s="    |-...")
            misc.print_clean(s="Usually, just need call 'Extract here' the downloaded %s"%(downloaded_cheat))
            

    elif choice == "search-by-name":
        

        cheat_dir = Path(cheat_cfg["dst"]).joinpath("titles")
        filenames= os.listdir (cheat_dir) # get all files' and folders' names in the current directory

        cheat_id_db = []
        for filename in filenames: # loop through all the files and folders
            if os.path.isdir(os.path.join(cheat_dir, filename)): # check whether the current object is a folder or not
                cheat_id_db.append(filename)
        
        with open(Path(title_cfg["dst"]).joinpath(title_cfg["db"]), encoding="utf8",mode= 'r') as f:
            game_db = json.load(f)

        misc.print_level3(s="There are %s/%s title id has cheat"%(len(cheat_id_db), len(game_db)))

        qarg = prompt.query('Game name:')
        query = qarg.split(" ")
        
        found_by_name = []
        for game in game_db:
            if all([x.lower() in game["title"].lower() for x in query]):
                found_by_name.append(game)

        options = []
        index = 0
        for (tid) in (found_by_name):
            if tid["id"] in filenames:
                index +=1
                options.append({'selector':index, "desc":"[%s] %s"%(tid["id"],tid["title"]), "return":tid["id"]})
        selected_tid = misc.get_single_selection(options=options, answer="Select title")

        tite_id_cheat_dir = cheat_dir.joinpath(selected_tid, "cheats")
        options=[]
        index = 0
        for filename in os.listdir(str(tite_id_cheat_dir)): # loop through all the files and folders
            if os.path.isfile(tite_id_cheat_dir.joinpath(filename)): # check whether the current object is a folder or not
                with open(tite_id_cheat_dir.joinpath(filename), encoding="utf8", errors='ignore', mode= 'r') as cheat:
                    index+=1
                    first_line = cheat.readline().strip()
                    options.append({"selector":index, "desc":"%s (Eg. %s)"%(filename, first_line), "return":filename})
        options.append({"selector":"a", "desc":"Copy all", "return":"all"})
        selected_version = misc.get_single_selection(options=options, default="a")

        if selected_version == 'all':
            for filename in os.listdir(str(tite_id_cheat_dir)): # loop through all the files and folders
                if os.path.isfile(tite_id_cheat_dir.joinpath(filename)): # check whether the current object is a folder or not
                    misc.copy(
                        src=tite_id_cheat_dir.joinpath(filename), 
                        dst=cheat_sd_dir.substitute({"titleid": selected_tid})
                    )
            return

        ch_book = tite_id_cheat_dir.joinpath(selected_version)
        print("Open", ch_book)
        cheat = CheatList(ch_book)
        ch_list = cheat.get_cheat_list()
        
        ch_option = []
        for (i, ch) in enumerate(ch_list):
            ch_option.append({
                "selector": i+1,
                "desc": ch.desc,
                "return": dict({
                    "desc":ch.desc,
                    "patch": ch.patch
                })
            })

        ch_selections = misc.get_multiple_selection(
            question="Select cheats",
            options=ch_option,
            answer="Select [1, 2, 3-5, all]:",
            two_column=True
        )

        written_str = []
        if len(cheat.desc) > 0:
            for desc in cheat.desc:
                written_str.append(desc)
            written_str.append("")

        for (i,ch) in enumerate(ch_selections):
            written_str.append(ch["desc"])
            for p in ch["patch"]:
                written_str.append(p)
            if (i < len(ch_selections)-1):
                written_str.append('')
        misc.write(
            src=written_str, 
            dst=os.path.join(cheat_sd_dir.substitute({"titleid": selected_tid}), selected_version)
        )

    elif choice == "open-by-tid":
        selected_tid = prompt.query('Title ID:')

        cheat_cfg = config["cheat-mng"]["cheat-db"]
        cheat_dir = Path(cheat_cfg["dst"]).joinpath("titles")
        tite_id_cheat_dir = cheat_dir.joinpath(selected_tid, "cheats")

        options=[]
        index = 0
        for filename in os.listdir(str(tite_id_cheat_dir)): # loop through all the files and folders
            if os.path.isfile(tite_id_cheat_dir.joinpath(filename)): # check whether the current object is a folder or not
                with open(tite_id_cheat_dir.joinpath(filename), encoding="utf8", errors='ignore', mode= 'r') as cheat:
                    index+=1
                    first_line = cheat.readline().strip()
                    options.append({"selector":index, "desc":"%s (Eg. %s)"%(filename, first_line), "return":filename})
        selected_version = misc.get_single_selection(options=options)

        ch_book = tite_id_cheat_dir.joinpath(selected_version)
        print("Open", ch_book)
        cheat = CheatList(ch_book)
        ch_list = cheat.get_cheat_list()
        
        ch_option = []
        for (i, ch) in enumerate(ch_list):
            ch_option.append({
                "selector": i+1,
                "desc": ch.desc,
                "return": dict({
                    "desc":ch.desc,
                    "patch": ch.patch
                })
            })

        ch_selections = misc.get_multiple_selection(
            question="Select cheats",
            options=ch_option,
            answer="Select [1, 2, 3-5, all]:",
        )

        written_str = []
        if len(cheat.desc) > 0:
            for desc in cheat.desc:
                written_str.append(desc)
            written_str.append("")

        for (i,ch) in enumerate(ch_selections):
            written_str.append(ch["desc"])
            for p in ch["patch"]:
                written_str.append(p)
            if (i < len(ch_selections)-1):
                written_str.append('')
        misc.write(
            src=written_str, 
            dst=os.path.join(cheat_sd_dir.substitute({"titleid": selected_tid}), selected_version)
        )
    elif choice == "batch-copy-all":
        src = prompt.query('Source game list:', default=os.path.join(config["cheat-mng"]["batch-game-list"]), validators=[validators.FileValidator()])
        with open(Path(src)) as f:
            batchlist = f.readlines()

        cheat_dir = Path(cheat_cfg["dst"]).joinpath("titles")
        filenames= os.listdir (cheat_dir) # get all files' and folders' names in the current directory

        cheat_id_db = []
        for filename in filenames: # loop through all the files and folders
            if os.path.isdir(os.path.join(cheat_dir, filename)): # check whether the current object is a folder or not
                cheat_id_db.append(filename)
        
        with open(Path(title_cfg["dst"]).joinpath(title_cfg["db"]), encoding="utf8",mode= 'r') as f:
            game_db = json.load(f)

        misc.print_level3(s="There are %s/%s title id has cheat"%(len(cheat_id_db), len(game_db)))

        for name in batchlist:
            misc.print_level2("Search for: "+name.strip())
            query = name.strip().split(" ")
            
            found_by_name = []
            for game in game_db:
                if all([x.lower() in game["title"].lower() for x in query]):
                    found_by_name.append(game)

            options = []
            index = 0
            for (tid) in (found_by_name):
                if tid["id"] in filenames:
                    index +=1
                    options.append({"id": tid["id"], "title":tid["title"]})
            with indent(indent=2):
                if len(options) < 1:
                    misc.print_error(s="Not found title keywords! Skip...")
                    continue
                elif len(options) > 1:
                    misc.print_error(f"Found %s titles contain keywords - MUST more details! Skip..."%len(options))
                    for g in options:
                        misc.print_warning(f"%s: %s"%(g["id"], g["title"]))
                    continue
                misc.print_success(f"Found ONE title: %s"%options[0]["title"])
            
            selected_tid = options[0]["id"]
            tite_id_cheat_dir = cheat_dir.joinpath(selected_tid, "cheats")
            
            for filename in os.listdir(str(tite_id_cheat_dir)): # loop through all the files and folders
                if os.path.isfile(tite_id_cheat_dir.joinpath(filename)): # check whether the current object is a folder or not
                    misc.copy(
                        src=tite_id_cheat_dir.joinpath(filename), 
                        dst=cheat_sd_dir.substitute({"titleid": selected_tid})
                    )
        pass