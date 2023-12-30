#!/usr/bin/env python3

from menu import main_menu, printHelpMenu
from setup import init_db
from os import getcwd, path
from glob import glob
from opml import opmlImport
from simple_term_menu import TerminalMenu
from common import addFeed, validateURL

opml_directory_path = getcwd()
opml_wildcard_pattern = '*.opml'

if __name__ == "__main__":
    try:
        if init_db() > 0:
            print("Database initialized successfully!")
            print("First run of pyfeedmanager, please decide if you want to import an opml file or add feeds manually")
            options = ["Import OPML", "Add feed manually", "Exit"]
            terminal_menu = TerminalMenu(options)
            match terminal_menu.show():
                case 0:
                    opmlFiles = glob(path.join(opml_directory_path, opml_wildcard_pattern))
                    if opmlFiles == []:
                        print('ERROR: No opml file could be found, please put your opml file in the directory of this script, make sure the python process can read it and it follows the following pattern: ' + opml_wildcard_pattern)
                    for opmlFile in opmlFiles:
                        opmlImport(opmlFile)
                    print('OPML import finished')
                case 1:
                    unsafeAddChoice = input('Please add the name/URL you want to add ')
                    safeInput =  validateURL(unsafeAddChoice)
                    if safeInput[0] == False:
                        print(safeInput[1])
                    addFeed(safeInput[0],safeInput[1],safeInput[2])
                case _:
                    exit()
        main_menu()
    except KeyboardInterrupt:
        exit()