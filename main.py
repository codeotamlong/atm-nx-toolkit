#!/usr/bin/python
import os
import json
from pathlib import Path
from clint.textui import prompt, puts, colored, validators, columns

import src.sd.setup
import src.fw.download
import src.utility.launcher
import src.cheat.manager
import src.misc

### FUNCTIONS ###


def display_banner():
    # Clears the terminal screen, and displays a title bar.
    os.system('cls||clear')

    puts(columns(
        [(colored.red('')), 17],
        [(colored.green('**************************************')), 50],
        [(colored.magenta('')), 25]
    ))
    puts(columns(
        [(colored.red('')), 17],
        [(colored.green('***  NSW - CWF & Homebrew Utilities  ***')), 50],
        [(colored.magenta('')), 25]
    ))
    puts(columns(
        [(colored.red('')), 17],
        [(colored.green('**************************************')), 50],
        [(colored.magenta('')), 25]
    ))


def get_choice():

    return src.misc.get_choice(
        question="What would you like to do?",
        options=[
            {'selector': '1', 'desc': 'SD Setup', 'return': 'sd-setup'},
            {'selector': '2', 'desc': 'Firmware Download', 'return': 'fw-dload'},
            {'selector': '3', 'desc': 'Atmosphere-NS Utilities', 'return': 'atm-utility'},
            {'selector': '4', 'desc': 'Cheat Management','return': 'cheat-mng'},
            {'selector': 'q', 'desc': 'Quit', 'return': 'quit'}
        ]
    )


def get_nand_choice():
    # Let users know what they can do.

    inst_options = [{'selector': '1', 'prompt': 'EmuNAND', 'return': 'emunand'},
                    {'selector': '2', 'prompt': 'SysNAND', 'return': 'sysnand'}]

    return prompt.options("What would you like to do?", inst_options)


def get_nsw_codename():
    # Let users know what they can do.

    inst_options = [{'selector': '1', 'prompt': 'Switch v1 (Unpatched): Need RCM Loader', 'return': 'erista-unpatched'},
                    {'selector': '2',
                        'prompt': 'Switch v1 (Patched)  : Need hard-mod (solderring) SX Core / HWFLY', 'return': 'erista-patched'},
                    {'selector': '3', 'prompt': 'Switch v2/Lite/OLED  : Need hard-mod (solderring) HWFLY', 'return': 'mariko'}]

    return prompt.options("What would you like to do?", inst_options)


def get_sd_config(nand, nsw):
    path = Path("/".join(["cfg", "sd", nand, nsw + ".json"]))
    with open(path, 'r') as config_file:
        cfg = json.load(config_file)
    return cfg


def get_fw_site_choice(sites):
    inst_options = []

    for (i, s) in enumerate(sites):
        inst_options.append({'selector': i, 'prompt': s["url"], 'return': i})

    choice = prompt.options("What would you like to do?", inst_options)
    return sites[int(choice)]


def get_fw_table_choice(site):
    # Let users know what they can do.
    inst_options = []

    for (i, t) in enumerate(site["table"]):
        inst_options.append({'selector': i, 'prompt': t['name'], 'return': i})
        # puts(s="["+str(i)+"] "+ t['name'])

    choice = prompt.options("What would you like to do?", inst_options)
    return site["table"][int(choice)]


def get_fw_version_choice(table):
    # Let users know what they can do.
    inst_options = []

    for (i, fw) in enumerate(table):
        inst_options.append(
            {'selector': i, 'prompt': '%-*s %s' % (40, fw.version, fw.md5), 'return': i})
        # puts(s="["+str(i)+"] "+ t['name'])

    choice = prompt.options("What would you like to do?", inst_options)
    return table[int(choice)]


def get_fw_dload_option(fw):
    puts("%s - %s - %s" % (fw.version, fw.filesize, fw.md5))

    inst_options = [{'selector': '1', 'prompt': "mega.nz - Open web-browser to download manually", 'return': fw.mega_nz},
                    {'selector': '2', 'prompt': "archive.org - Download automatically", 'return': fw.archive_org}]

    choice = prompt.options("What would you like to do?", inst_options)
    return choice


### MAIN PROGRAM ###
with open(Path("./cfg/config.json"), 'r') as config_file:
    root_cfg = json.load(config_file)
# Set up a loop where users can choose what they'd like to do.
choice = ''
display_banner()
while choice != 'quit':
    # Respond to the user's choice.
    display_banner()
    choice = get_choice()

    if choice == 'sd-setup':
        nand = get_nand_choice()
        nsw = get_nsw_codename()
        if (nand is None) or (nsw is None):
            print("Bad choice")
            input("Press Enter to continue...")
            continue
        src.sd.setup.run(root_cfg, get_sd_config(nand, nsw))
        input("Press Enter to continue...")
    if choice == 'fw-dload':
        with open(Path("./cfg/fw.json"), 'r') as config_file:
            fw_config = json.load(config_file)
            site = get_fw_site_choice(fw_config)
            table = get_fw_table_choice(site)
            data = src.fw.download.run(site["url"], table["class"])
            version = get_fw_version_choice(data.firmware)
            dl_link = get_fw_dload_option(version)
            src.fw.download.open_(dl_link)
        input("Press Enter to continue...")
    elif choice == 'atm-utility':
        with open(Path("./cfg/atm-utility.json"), 'r') as config_file:
            cfg = json.load(config_file)
        src.utility.launcher.launch(root_cfg, cfg)
        input("Press Enter to continue...")
    elif choice == 'cheat-mng':
        with open(Path("./cfg/atm-utility.json"), 'r') as config_file:
            cfg = json.load(config_file)
        src.cheat.manager.main()
        input("Press Enter to continue...")
    elif choice == 'quit':
        print("\nThanks for playing. Bye.")
        input("Press Enter to continue...")
    else:
        print("\nI didn't understand that choice.\n")
        input("Press Enter to continue...")
