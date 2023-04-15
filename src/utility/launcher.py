import json
import os
from pathlib import Path
from clint.textui import progress, puts, indent, colored, prompt, validators

from . import logo_patch, splash
from .. import misc



def launch(root, cfg):
    choice = misc.get_choice(
        options=[
            {"selector":1, "desc":"Change boot logo (friedkeenan/switch-logo-patcher)", "return":"change-boot-logo"},
            {"selector":2, "desc":"Insert custom splash (Atmosphere-NX/Atmosphere)", "return":"change-splash-screen"}
        ]
    )
    if choice == "change-boot-logo":
        with open(Path("./cfg/custom-bootlogo.json"), 'r') as config_file:
            patch_data = json.load(config_file)
        print(patch_data["desc"])
        patched_dir = prompt.query('Destination dir', default=os.path.join(root["sd"], root["custom-bootlogo"]["dst"], root["custom-bootlogo"]["dir"]), validators=[validators.PathValidator()])
        new_logo = prompt.query('Image', default=os.path.join(root["custom-bootlogo"]["src"], root["custom-bootlogo"]["default"]), validators=[validators.PathValidator()])        
        logo_patch.generate2(
            old_logo=None,
            patches_dir=patched_dir,
            new_logo=new_logo,
            patch_data=patch_data["patch_info"]
        )
    elif choice == "change-splash-screen":
        src = prompt.query('Source image', default=os.path.join(root["custom-splash"]["src"], root["custom-splash"]["default"]), validators=[validators.FileValidator()])
        dst = prompt.query('Destination package3', default=os.path.join(root["sd"], root["custom-splash"]["dst"]), validators=[validators.FileValidator()])    
        splash.insert(
            src=src,
            dst=dst
        )