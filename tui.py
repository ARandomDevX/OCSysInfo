from platform import system
from turtle import home
import src.info
import os
import requests
from src.info import get_latest_version, format_text, AppInfo, color_text
import queue
from threading import Thread
from update.updater import OCSIUpdater
from src.managers import devicemanager

from src.util.dump_functions import text, json, xml, plist

import logging

toggle_opts = ['CPU', 'GPU', 'Motherboard', 'Memory', 'Storage', 'Network', 'Audio', 'Input']
all_opts = ['CPU', 'GPU', 'Motherboard', 'Memory', 'Storage', 'Network', 'Audio', 'Input']
offline = False
sl_fin = False

dformat = None
dumpdir = os.getcwd()

fndumpdir = False

def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])

(width, height) = getTerminalSize()

STYLED_TITLE = """
  #############################################
 #                 OCSysInfo                 #
############################################# 
""".center(width)

def clear():
    if system() == 'Windows':
        os.system('cls')
    else:
        os.system("clear")

def title():
    print(STYLED_TITLE + "\n\n")

def input_handler(poss_options, text):

    while True:
        try:
            user_input = int(input(text))
            if user_input in poss_options:
                return user_input
            else:
                print("ERR: Invalid input '" + str(user_input) + "'")
        except ValueError:
            print("ERR: Invalid input")

def update():
    if not offline:
        # Get info for latest version
        que = queue.Queue()
        thread = Thread(target=lambda q: q.put(get_latest_version()), args=(que,))

        # We start the thread while the script is discovering the data
        thread.start()
        thread.join()

        # We have the latest version!
        latest_version = que.get()

        if latest_version != AppInfo.version:
            import os
            import sys

            # Formatted 'n coloured
            fnc = color_text(
                format_text(
                    f"NEW VERSION ({latest_version}) AVAILABLE!\nInstall? (y/n): ",
                    "bold+underline"
                ),
                "red"
            )
            res = input(fnc)

            if "y" in res.lower():
                update = OCSIUpdater()

                update.run()

                print("\nRunning OCSysInfo after update...")

                # Restart with the updated version
                os.execv(sys.executable, ['python'] + [sys.argv[0]])

def homescreen():
    global sl_fin, toggle_opts
    clear()
    title()

    print("First, let's finialize on what you want dumped:\n")

    print(f"- [{'X' if 'CPU' in toggle_opts else ' '}] 1. Toggle CPU info")
    print(f"- [{'X' if 'GPU' in toggle_opts else ' '}] 2. Toggle GPU info")
    print(f"- [{'X' if 'Motherboard' in toggle_opts else ' '}] 3. Toggle Motherboard info")
    print(f"- [{'X' if 'Memory' in toggle_opts else ' '}] 4. Toggle RAM info")
    print(f"- [{'X' if 'Storage' in toggle_opts else ' '}] 5. Toggle Disk info")
    print(f"- [{'X' if 'Network' in toggle_opts else ' '}] 6. Toggle Network info")
    print(f"- [{'X' if 'Audio' in toggle_opts else ' '}] 7. Toggle Audio info")
    print(f"- [{'X' if 'Input' in toggle_opts else ' '}] 8. Toggle Input info")
    print("\n- [CMD] 9. Finalize selection")
    print(f"\n- [CMD] 10. Exit\n")


    inp = input_handler([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "root@Homescreen> ")

    if inp == 10:
        print("Bye!")
        exit()

    elif inp == 9:
        sl_fin = True

    else:

        if inp in toggle_opts:
            toggle_opts.remove(toggle_opts[inp - 1])
            toggle_opts.insert(inp - 1, toggle_opts[inp - 1])

        else:
            toggle_opts.remove(toggle_opts[inp - 1])
            toggle_opts.insert(inp - 1, "")
            print(toggle_opts[inp - 1])

def dump_format_choice():
    global dformat
    clear()
    title()

    print("Great! Now let's choose how you want the data to be formatted:\n")

    print("- [1] Plain text (.txt)")
    print("- [2] XML (.xml)")
    print("- [3] JSON (.json)")
    print("- [4] PLIST (.plist)")
    print("\n- [CMD] 5. Change dump directory")
    print("\n- [CMD] 6. Exit\n")

    inp = input_handler([1, 2, 3, 4, 5, 6], "root@DataFormatHandler> ")

    if inp == 5:
        chdumpdir()

    if inp == 6:
        print("Bye!")
        exit()
    
    if inp == 1:
        dformat = text.dump_txt
    elif inp == 2:
        dformat = xml.dump_xml
    elif inp == 3:
        dformat = json.dump_json
    elif inp == 4:
        dformat = plist.dump_plist


def chdumpdir():
    clear()
    title()

    print("Let's change the directory of the output file\n\n")

    inp = input("root@DumpDirHandler ? press Q to return> ")
    dumpdir = inp
    while not os.path.exists(dumpdir) and inp != "Q":
        print("That directory doesn't exist!")
        inp = input("root@DumpDirHandler> ")
        dumpdir = inp

    if not os.path.exists(dumpdir):
        dumpdir = os.path()

def iTestScreen():
    clear()
    title()

    print("Testing internet connection...")
    try:
        requests.get("https://www.google.com")
        offline = False
        print("Machine has an available connection!")
    except Exception:
        offline = True
        print("Internet connection not available!")

if __name__ == "__main__":
    iTestScreen()
    update()
    while sl_fin == False:
        homescreen()
    
    while dformat == None:
        dump_format_choice()

    clear()
    title()

    logger = logging.getLogger(__name__)
    print("Please stand by while we are dumping the data. This may take a while...\n\n")
    for i in toggle_opts:
        all_opts.remove(i)
    dm = devicemanager.DeviceManager(logger, all_opts, offline)
    dformat(dm, dumpdir, logger)