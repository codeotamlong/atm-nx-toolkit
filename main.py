#!/usr/bin/python
import os
import src.sd.setup

### FUNCTIONS ###

def display_banner():
    # Clears the terminal screen, and displays a title bar.
    os.system('clear')
              
    print("\t****************************************")
    print("\t***  NSW - CWF & Homebrew Utilities  ***")
    print("\t****************************************")
    
def get_choice():
    # Let users know what they can do.
    print("\n[1] SD Setup ")
    print("[2] Download firmware")
    print("[3] Splash Atmosphere")
    print("[4] Cheat management")
    print("[q] Quit.")
    
    return input("What would you like to do? ")

def get_nand_choice():
     # Let users know what they can do.
    print("\n[1] EmuNAND ")
    print("[2] SysNAND")
    
    i =  input("What would you like to do? ")

    if i=='1':
        return "emunand"
    elif i=='2':
        return "sysnand"
    else:
        return None

def get_nsw_codename():
    # Let users know what they can do.
    print("\n[1] Switch v1 (Unpatched): Need RCM Loader")
    print(  "[2] Switch v1 (Patched)  : Need hard-mod (solderring) SX Core / HWFLY.")
    print(  "[3] Switch v2/Lite/OLED  : Need hard-mod (solderring) HWFLY")
    
    i =  input("What would you like to do? ")

    if i=='1':
        return "erista-unpatched"
    elif i=='2':
        return "erista-patched"
    elif i=='2':
        return "mariko"
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
    elif choice == 'q':
        print("\nThanks for playing. Bye.")
    else:
        print("\nI didn't understand that choice.\n")