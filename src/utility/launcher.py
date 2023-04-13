from clint.textui import progress, puts, indent, colored, prompt

import logo_patch



def launch(root, cfg):
    inst_options = [{'selector': 1, 'prompt': 'Generate patches to change the Switch logo on boot (friedkeenan/switch-logo-patcher)', 'return': 1}]
    print("Hello")
    choice = prompt.options("What would you like to do?", inst_options, default='1')
   

    if choice == 1:
        print(0)
        logo_patch.generate(
            old_logo=None, 
            patches_dir=Path("%s"%(root["custom-logo"]["dst"])), 
            new_logo=Path("%s/%s"%(root["custom-logo"]["src"], "default.png")))
    pass
