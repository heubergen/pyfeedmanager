from manage import manageData
from common import directlyError, printVersion
from simple_term_menu import TerminalMenu
from os import getcwd

opml_directory_path = getcwd()
opml_wildcard_pattern = '*.opml'
helpMenu = 'Welcome to pyfeedmanager! \nThis tool knows three different data: \n* Feeds (The URL where new articles can be found) \n* Articles (Each article is connected to a feed and contains the URL where you can read it \n* Categories (Each feed may be assinged to exactly one category))'

def printHelpMenu():
	print(helpMenu)

if __name__ == "__main__":
	directlyError()

def general_menu():
	while True:
		options = ["Print Version", "Print Help", "Back"]
		terminal_menu = TerminalMenu(options)
		match terminal_menu.show():
			case 0:
				printVersion()
			case 1:
				printHelpMenu()
			case None:
				exit()
			case _:
				return
			
def category_menu():
	manageData('Categories')

def feed_menu():
	manageData('Feeds')

def article_menu():
	manageData('Articles')

def main_menu():
	menu_count = 0
	while True:
		options = ["General", "Categories", "Feeds", "Articles", "Exit"]
		if menu_count == 0:
			menu_count += 1
			terminal_menu = TerminalMenu(options, title=helpMenu)
		else:
			terminal_menu = TerminalMenu(options)
		match terminal_menu.show():
			case 0:
				general_menu()
			case 1:
				category_menu()
			case 2:
				feed_menu()
			case 3:
				article_menu()
			case 4:
				exit()
			case None:
				exit(0)