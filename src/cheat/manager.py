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

def update_title_db(title_cfg):
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

        misc.write(src=json.dumps(misc.unique(title_id_db), ensure_ascii=False), dst=title_id_file)
    except FileNotFoundError:
        print("The 'docs' directory does not exist")


def update_cheat_db(cheat_cfg):
    misc.print_level3(s=cheat_cfg["desc"])
    # misc.download_raw(
    #     url=cheat_cfg["url"], 
    #     filename=cheat_cfg["download"],
    #     dst=Path(cheat_cfg["dst"])
    # )
    downloaded_cheat = Path(cheat_cfg["dst"]).joinpath(cheat_cfg["download"])

    if not misc.unrarfile(src=downloaded_cheat, dst=Path(cheat_cfg["dst"])):
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


def is_title_id(s:str):
    re_title_id = re.compile(r"[a-fA-F0-9]{8}")
    return re_title_id.match(s)

def get_title_id(keywords=[], db=[]):
    ret = []

    if len(keywords) < 1:
        misc.print_error(s="Empty keywords. Skip...")
        return ret
    
    if len(db) < 1:
        misc.print_error(s="Empty database. Skip...")
        return ret

    for d in db:
        if all([kw.lower() in d["title"].lower() for kw in keywords]):
            ret.append(d)

    return ret

def name_by_tid(tid="", db=[]):
    ret = []

    if not is_title_id(s=tid):
        misc.print_error(s="%s is not Title ID"%tid)
        return ret
    
    if len(db) < 1:
        misc.print_error(s="Empty database. Skip...")
        return ret

    for d in db:
        if d["id"] == tid:
            ret.append(d)

    return ret

def is_cheat_available(tid, db=[]):
    if not is_title_id(s=tid):
        return False

    if len(db) < 1:
        misc.print_error(s="Empty database. Skip...")
        return False
    
    if tid in db:
        return True


def main(config):
    options = []

    cheat_cfg = config["cheat-mng"]["cheat-db"]
    cheat_sd_dir = Template(os.path.join(config["sd"], config["cheat-mng"]["sd"]))

    cheat_dir = Path(cheat_cfg["dst"]).joinpath("titles")
    cheat_list = []
    if (cheat_dir.exists()):
        for dir_ in os.listdir (cheat_dir): # loop through all the files and folders
            if os.path.isdir(cheat_dir.joinpath(dir_)): # check whether the current object is a folder or not
                cheat_list.append(dir_)

    title_cfg = config["cheat-mng"]["title-db"]
    try:
        with open(Path(title_cfg["dst"]).joinpath(title_cfg["db"]), encoding="utf8",mode= 'r') as f:
            title_list = json.load(f)
    except FileNotFoundError:
        title_list = []

    misc.print_level3(s="There are %s/%s Title IDs has cheat(s)"%(len(cheat_list), len(title_list)))
        
    options.append({"desc": "Update"+(" <= MUST RUN FIRST" if (len(cheat_list)==0) else ""), "selector":1, "return":"update"})
    options.append({"desc": "Search by Title ID or keywords", "selector":2, "return":"search"})
    options.append({"desc": "Batch cheat copy", "selector":3, "return":"batch"})
    
    choice = misc.get_single_selection(
        question="Select your work",
        options=options,
        two_column=True,
        default="1" if len(cheat_list)==0 else "2"
    )
    if choice == "update":
        update_title_db(title_cfg)
        update_cheat_db(cheat_cfg)

    elif choice == "search":
        query = prompt.query('Search for (keywords/Title ID):')
        if is_title_id(s=query):
            misc.print_clean("%s is Title ID"%query)

            tnames = name_by_tid(tid=query, db=title_list)
            with indent(indent=2):
                for tn in tnames:
                    misc.print_warning(s="%s: %s"%(tn["id"], tn["title"]))

            if len(tnames) > 1:
                misc.print_error(s="Something wrong! One ID should be paired ONLY ONE title")
                return

            if not tnames[0]["id"] in (cheat_list):
                misc.print_error(s="Cheat NOT FOUND! Maybe update or copy manually")
                return

            options=[]
            index = 0
            tite_id_cheat_dir = cheat_dir.joinpath(query, "cheats")
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
        else:
            query = query.split(" ")
            misc.print_clean("This is keywords: "+str(query))

            found_by_name = get_title_id(keywords=query, db=title_list)
            
            have_cheat = []
            no_cheat = []
            index = 0
            for (tid) in (found_by_name):
                if is_cheat_available(tid=tid["id"], db=cheat_list):
                    index +=1
                    have_cheat.append({'selector':index, "desc":"[%s] %s"%(tid["id"],tid["title"]), "return":tid["id"]})
                else:
                    no_cheat.append(f"[%s] %s"%(tid["id"],tid["title"]))
            
            misc.print_clean(s="These Titles have no cheat! May be you want to do it manually")
            with indent(indent=4):
                for nc in no_cheat:
                    misc.print_clean(s=nc)

            selected_tid = misc.get_single_selection(
                question="These Titles have cheats in database:",
                options=have_cheat, 
                answer="Select title"
            )

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

    elif choice == "batch":
        src = prompt.query('Source game list:', default=os.path.join(config["cheat-mng"]["batch-game-list"]), validators=[validators.FileValidator()])
        with open(Path(src)) as f:
            batchlist = f.readlines()
        for line in batchlist:
            line = line.strip()
            misc.print_level2("Search for: "+line)

            if is_title_id(line):
                misc.print_clean("%s looks like Title ID"%line)

                tnames = name_by_tid(tid=line, db=title_list)
                with indent(indent=2):
                    for tn in tnames:
                        misc.print_warning(s="%s: %s"%(tn["id"], tn["title"]))
                    if len(tnames) > 1:
                        misc.print_error(f"Found %s titles has same Title ID - MUST more details! Skip..."%len(tnames))
                
                cheat_available = []
                for t in tnames:
                    if is_cheat_available(tid=t["id"], db=cheat_list):
                        cheat_available.append(t)
                if len(cheat_available) < 1:
                    misc.print_error(s="Cheat not found! Skip...")
                    continue
                elif len(cheat_available) > 1:
                    misc.print_error(f"Found %s titles in Cheat DB - It MUST be ONLY ONE! Skip..."%len(cheat_available))
                    for g in cheat_available:
                        misc.print_warning(f"%s: %s"%(g["id"], g["title"]))
                    continue
                else:
                    misc.print_success(f"Found ONE title: %s"%cheat_available[0]["title"])

                selected_tid = cheat_available[0]["id"]
                tite_id_cheat_dir = cheat_dir.joinpath(selected_tid, "cheats")
                
                for filename in os.listdir(str(tite_id_cheat_dir)): # loop through all the files and folders
                    path = tite_id_cheat_dir.joinpath(filename)
                    if path.is_file():
                        misc.copy(
                            src=path, 
                            dst=cheat_sd_dir.substitute({"titleid": selected_tid})
                        )
                    
            else:
                query = line.split(" ")
                misc.print_clean("This is keywords: "+str(query))

                tid_by_name = get_title_id(keywords=query, db=title_list)
                cheat_available = []
                for (tid) in (tid_by_name):
                    if is_cheat_available(tid=tid["id"], db=cheat_list):
                        cheat_available.append({"id": tid["id"], "title":tid["title"]})
                        
                with indent(indent=2):
                    if len(cheat_available) < 1:
                        misc.print_error(s="Cheat not found! Skip...")
                        continue
                    elif len(cheat_available) > 1:
                        misc.print_error(f"Found %s titles in DB - It MUST be ONLY ONE! Skip..."%len(cheat_available))
                        for g in cheat_available:
                            misc.print_warning(f"%s: %s"%(g["id"], g["title"]))
                        continue
                    else:
                        misc.print_success(f"Found ONE title: %s"%cheat_available[0]["title"])
                
                selected_tid = cheat_available[0]["id"]
                tite_id_cheat_dir = cheat_dir.joinpath(selected_tid, "cheats")
                
                for filename in os.listdir(str(tite_id_cheat_dir)): # loop through all the files and folders
                    path = tite_id_cheat_dir.joinpath(filename)
                    if path.is_file():
                        misc.copy(
                            src=path, 
                            dst=cheat_sd_dir.substitute({"titleid": selected_tid})
                        )