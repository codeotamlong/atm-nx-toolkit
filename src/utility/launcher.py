from pathlib import Path
from clint.textui import progress, puts, indent, colored, prompt

from . import logo_patch, splash



def launch(root, cfg):
    inst_options = [
        {'selector': 1, 'prompt': 'Generate patches to change the Switch logo on boot (friedkeenan/switch-logo-patcher)', 'return': 1},
        {'selector': 2, 'prompt': 'Insert custom splash screen (Atmosphere-NX/Atmosphere)', 'return': 2}]
    print("Hello")
    choice = prompt.options("What would you like to do?", inst_options, default='1')
   

    if choice == 1:
        logo_patch.generate(
            old_logo=None, 
            patches_dir=Path(".").joinpath(root["sd"], root["custom-bootlogo"]["dst"], root["custom-logo"]["dir"]), 
            new_logo=Path(".").joinpath(root["custom-bootlogo"]["src"], root["custom-logo"]["default"])
        )
    elif choice ==2:
        splash.insert(
            src=Path(".").joinpath(root["custom-splash"]["src"], root["custom-splash"]["default"]),
            dst=Path(".").joinpath(root["sd"], root["custom-splash"]["dst"])
        )