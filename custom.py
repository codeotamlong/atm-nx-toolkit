import re
import os
import shutil

from clint.textui import progress, puts, indent, colored



def rename(args):
    regex = args["regex"] if "regex" in args else None
    src = args["src"] if "src" in args else None
    dst = args["dst"] if "dst" in args else None

    if (regex is None) or (src is None) or (dst is None):
        puts(s="Need regex, src, dst in args")
        return

    puts(s="Rename "+regex+" in dir "+src+" to "+dst)
    regex = re.compile(regex)
    for filename in os.listdir(src):  # loop through items in dir
        if regex.match(filename):
            puts(s="Found: "+filename+"=> Rename to"+dst.split("/")[-1])
            os.rename(os.path.join(src, filename),
                    os.path.join(src, dst))

def copy(args):
    regex = args["regex"] if "regex" in args else None
    src = args["src"] if "src" in args else None
    dst = args["dst"] if "dst" in args else None

    if (regex is None) or (src is None) or (dst is None):
        puts(s="Need regex, src, dst in args")
        return
    puts(s="Copy "+regex+" from "+src+" to "+dst)

    if os.path.exists(os.path.join(src, regex)):
        shutil.copy(os.path.join(src, regex), os.path.join(dst, regex))
        if os.path.isfile(os.path.join(dst, regex)):
            puts(s=colored.yellow(("Success")))
