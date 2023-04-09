#!/usr/bin/python
import os
import json
from clint.textui import puts, colored
from clint.textui import columns

import src.sd.setup
import src.fw.download

### FUNCTIONS ###

def display_banner():
    # Clears the terminal screen, and displays a title bar.
    os.system('clear')
    
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
    # Let users know what they can do.
    puts(columns(
            [(colored.clean('[1] SD Setup')), 50], 
            [(colored.clean('[2] Firmware Download')), 50]
        ))
    puts(columns(
            [(colored.clean('[3] Splash Atmosphere')), 50], 
            [(colored.clean('[4] Cheat management')), 50]
        ))
    puts(columns(
            [(colored.clean('[q] Quit')), 50]
        ))
    
    return input("What would you like to do? ")

def get_nand_choice():
     # Let users know what they can do.

    puts(columns(
            [(colored.clean('[1] EmuNAND')), 50], 
            [(colored.clean('[2] SysNAND')), 50]
        ))
    
    i =  input("What would you like to do? ")

    if i=='1':
        return "emunand"
    elif i=='2':
        return "sysnand"
    else:
        return None

def get_nsw_codename():
    # Let users know what they can do.
    puts("\n[1] Switch v1 (Unpatched): Need RCM Loader")
    puts(  "[2] Switch v1 (Patched)  : Need hard-mod (solderring) SX Core / HWFLY.")
    puts(  "[3] Switch v2/Lite/OLED  : Need hard-mod (solderring) HWFLY")
    
    i =  input("What would you like to do? ")

    if i=='1':
        return "erista-unpatched"
    elif i=='2':
        return "erista-patched"
    elif i=='3':
        return "mariko"
    else:
        return None

def get_fw_site_choice(sites):
    for (i, s) in enumerate(sites):
        puts(s="["+str(i)+"] "+ s['url'])

    i =  input("What would you like to do? ")
    return sites[int(i)]

def get_fw_table_choice(site):
    # Let users know what they can do.
    for (i, t) in enumerate(site["table"]):
        puts(s="["+str(i)+"] "+ t['name'])

    i =  input("What would you like to do? ")
    return site["table"][int(i)]

def get_fw_version_choice(table):
    # Let users know what they can do.
    puts(columns(
            [(colored.green("No.")), 5],
            [(colored.green("Version")), 40],
            [(colored.green("MD5")), 50]
        ))
    for (i, fw) in enumerate(table):
        puts(columns(
            [(colored.clean(i)), 5],
            [(colored.clean(fw.version)), 40],
            [(colored.clean(fw.md5)), 50]
        ))
        # print(i, fw.version, fw.md5, fw.filesize, fw.mega_nz, fw.archive_org)
    
    i =  input("What would you like to do? ")

    return table[int(i)]

def get_fw_dload_option(fw):
    puts("%s - %s - %s" %(fw.version, fw.filesize, fw.md5))
    print("[1]",fw.mega_nz)
    print("[2]", fw.archive_org)
    i =  input("What would you like to do? ")
    if i=='1':
        return fw.mega_nz
    elif i=='2':
        return fw.archive_org
    else:
        return None


### MAIN PROGRAM ###

# Set up a loop where users can choose what they'd like to do.
choice = ''
display_banner()
while choice != 'q':    
    # Respond to the user's choice.
    display_banner()
    choice = get_choice()
    
    if choice == '1':
        nand = get_nand_choice()
        nsw = get_nsw_codename()
        if (nand is None) or (nsw is None):
            print("Bad choice")
            input("Press Enter to continue...")
            continue
        src.sd.setup.run(cfg={
            "nsw": nsw,
            "nand": nand
        })
        input("Press Enter to continue...")
    if choice == '2':
        path = os.path.join(
            "/".join([".", "cfg", "fw.json"]))
        with open(path, 'r') as config_file:
            fw_config = json.load(config_file)
            site = get_fw_site_choice(fw_config)
            table = get_fw_table_choice(site)
            data = src.fw.download.run(site["url"], table["class"])
            version = get_fw_version_choice(data.firmware)
            dl_link = get_fw_dload_option(version)
            src.fw.download.open_(dl_link)
        input("Press Enter to continue...")
    elif choice == 'q':
        print("\nThanks for playing. Bye.")
        input("Press Enter to continue...")
    else:
        print("\nI didn't understand that choice.\n")
        input("Press Enter to continue...")