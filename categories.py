import common
from simple_term_menu import TerminalMenu

if __name__ == "__main__":
    common.directlyError()

def addCategory(feedCategoryName):
	categoryID = common.executeQuery("SELECT ID FROM categories WHERE Name =?;", (feedCategoryName,))
	if categoryID == []:
		common.executeQuery("INSERT INTO categories (Name) VALUES (?);", (feedCategoryName,))
		return(1)
	else:
		return(0)
	
def getCategoryID(feedCategoryName):
	categoryID = common.executeQuery("SELECT ID FROM categories WHERE Name ='" + feedCategoryName + "';")
	if categoryID == []:
		common.unexpectedMatch()
	else:
		return(categoryID[0][0])

def chooseCategory():
	categoryListRaw = common.executeQuery("SELECT Name FROM categories;")
	if categoryListRaw == []:
		categoryToAdd = input("No categories found, please input the category you want to add and press enter: ")
		addCategory(categoryToAdd)
		categoryListRaw = common.executeQuery("SELECT Name FROM categories;")

	categoryList = [t[0] for t in categoryListRaw]
	terminal_menu = TerminalMenu(categoryList, title="Choose the category or press Ctrl + c to choose another feed")
	terminal_menu.show()
	category_choice = terminal_menu.chosen_menu_entry
	match category_choice:
		case None |'Exit':
			return
		case _:
			feedCategoryID = common.executeQuery("SELECT ID FROM categories WHERE Name ='" + category_choice + "';")
			return(feedCategoryID)