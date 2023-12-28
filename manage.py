from simple_term_menu import TerminalMenu
from common import directlyError, executeQuery, tableListArticles, unexpectedMatch, validateURL, addFeed
from articles import updateFeeds
from categories import addCategory

if __name__ == "__main__":
    directlyError()

def getList(dataType):
	if dataType == 'Feeds':
		listallFeedsRaw = executeQuery("SELECT * FROM feeds;")
		listallFeedsList = [t[1] for t in listallFeedsRaw]
		return listallFeedsList
	elif dataType == 'Categories':
		categoryListRaw = executeQuery("SELECT Name FROM categories;")
		categoryList = [t[0] for t in categoryListRaw]
		return categoryList
	elif dataType == 'Articles':
		articlesListUnread = executeQuery("SELECT Title, case when Summary = '' then 'This article does not have a summary, please check visit the article directly' else Summary end as 'Summary', articleDate as 'Article Date', URL FROM articles WHERE read ='false';")
		return articlesListUnread
	else:
		unexpectedMatch()

def getData(dataType, listChoice='none'):
	if dataType == 'Feeds':
		return executeQuery("SELECT URL, Title, Type FROM feeds where Title = '" + listChoice + "';")[0]
	elif dataType == 'Categories':
		return executeQuery("SELECT ID, Name FROM categories WHERE Name ='" + listChoice + "';")
	elif dataType == 'Articles':
		return executeQuery("SELECT COUNT(ID) FROM articles where read = 'false'")
	else:
		unexpectedMatch()

def removeData(dataType, removalChoice):
	if input('Please confirm that you want to delete ' + removalChoice + ' [y/n] ').lower() == 'y':
		if dataType == 'Feeds':
			feedID = executeQuery("SELECT ID FROM feeds WHERE Title = '" + removalChoice + "';")
			executeQuery("DELETE FROM feeds WHERE ID = '" + str(feedID[0][0]) + "';")
			executeQuery("DELETE FROM articles WHERE feed_id = '" + str(feedID[0][0]) + "';")
			print(removalChoice + ' and all entries have been removed')
		elif dataType == 'Categories':
			categoryID = executeQuery("SELECT ID FROM categories WHERE Name = '" + removalChoice + "';")
			executeQuery("DELETE FROM categories WHERE Name = '" + removalChoice + "';")
			executeQuery("UPDATE feeds SET category_id = '0' WHERE category_id = '" + str(categoryID) + "';")
			print(removalChoice + ' has been removed')
		else:
			unexpectedMatch()
	else:
		print(removalChoice + ' was not removed')

def updateData(dataType, updateChoice):
	if dataType == 'Feeds':
		options = ['Title', 'URL']
		terminal_menu = TerminalMenu(options, title="Choose what you want to update")
		match terminal_menu.show():
			case 0:
				unsafeNewTitle = input('Please enter the new Title ')
				executeQuery("UPDATE feeds SET Title = ? WHERE Title = '" + updateChoice + "';", (unsafeNewTitle,))
				print('The feed title was changed to ' + unsafeNewTitle)
			case 1:
				unsafeNewURL = input('Please enter the new URL ')
				safeInput = validateURL(unsafeNewURL)
				if safeInput[0] == False:
					print(safeInput[1])
				else:
					executeQuery("UPDATE feeds SET URL = ? WHERE Title = '" + updateChoice + "';", (safeInput[0],))
					print('The feed URL was changed to ' + safeInput[0])
			case None:
				exit(0)
	elif dataType == 'Categories':
		unsafeNewTitle = input('Please enter the new Title ')
		executeQuery("UPDATE categories SET Name = ? WHERE Name = '" + updateChoice + "';", (unsafeNewTitle,))
		print('The category title was changed to ' + unsafeNewTitle)
	else:
		unexpectedMatch()

def addData(dataType):
	unsafeAddChoice = input('Please add the name/URL you want to add ')
	if dataType == 'Feeds':
		safeInput =  validateURL(unsafeAddChoice)
		if safeInput[0] == False:
			print(safeInput[1])
			return
		addFeed(safeInput[0],safeInput[1],safeInput[2])
	elif dataType == 'Categories':
		categoryReturn = addCategory(unsafeAddChoice)
		if categoryReturn == 1:
			print(unsafeAddChoice + ' added')
		elif categoryReturn == 0:
			print(unsafeAddChoice + ' already exists')
		else:
			unexpectedMatch()
	else:
		unexpectedMatch()

def manageData(dataType):
	data = getList(dataType)
	if dataType in('Feeds', 'Categories'):
		if data == []:
			errorMsg = 'No ' + dataType.lower() + ' could be found'
			return False,errorMsg
		terminal_menu = TerminalMenu(data + ['Add', 'Back', 'Exit'], title="Choose the " + dataType.lower() + " you want to manage")
		terminal_menu.show()
		data_choice = terminal_menu.chosen_menu_entry
		match data_choice:
			case None | 'Exit':
				exit()
			case 'Back':
				return
			case 'Add':
				addData(dataType)
			case _:
				options = ['Get', 'Update', 'Remove']
				terminal_menu = TerminalMenu(options)
				match terminal_menu.show():
					case 0:
						ouputraw = getData(dataType, data_choice)
						if dataType == 'Categories':
							print(ouputraw[0])
						elif dataType == 'Feeds':
							print(ouputraw[1] + ' | ' + ouputraw[0])
					case 1:
						updateData(dataType, data_choice)
					case 2:
						removeData(dataType, data_choice)
					case _:
						unexpectedMatch()
	elif dataType == 'Articles':
		if data == []:
			updateFeeds()
			data = getList(dataType)
			if data == []:
				print('No unread articles could be found')
				return

		tableListArticles(data)