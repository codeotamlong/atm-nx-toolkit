import json
import os
from pathlib import Path
from clint.textui import progress, puts, indent, colored, prompt, validators

from . import logo_patch, splash
from .. import misc



def launch(config):
    choice = misc.get_single_selection(
        options=[
            {"selector":1, "desc":"Change boot logo (friedkeenan/switch-logo-patcher)", "return":"custom-bootlogo"},
            {"selector":2, "desc":"Insert custom splash (Atmosphere-NX/Atmosphere)", "return":"custom-splashscreen"}
        ]
    )
    if choice == "custom-bootlogo":
        patch_data = config["custom-bootlogo"]
        misc.print_level3(s=patch_data["desc"])
        patched_dir = prompt.query('Destination dir', default=os.path.join(config["sd"], patch_data["dst"], patch_data["dir"]), validators=[])
        new_logo = prompt.query('Image', default=os.path.join(patch_data["src"], patch_data["default"]), validators=[validators.FileValidator()])        
        logo_patch.generate2(
            old_logo=None,
            patches_dir=Path(patched_dir),
            new_logo=Path(new_logo),
            patch_data=patch_data["patch_info"]
        )
        misc.print_success(s="Copy patched dir to %s"%(os.path.join(config["sd"], patch_data["dst"])))
    elif choice == "custom-splashscreen":
        splash_data=config["custom-splashscreen"]
        src = prompt.query('Source image', default=os.path.join(splash_data["src"], splash_data["default"]), validators=[validators.FileValidator()])
        dst = prompt.query('Destination package3', default=os.path.join(config["sd"], splash_data["dst"]), validators=[validators.FileValidator()])
        splash.insert(
            src=Path(src),
            dst=Path(dst)
        )
        misc.print_success(s="Overwrite patched package3 to %s"%(os.path.join(config["sd"], splash_data["dst"])))
