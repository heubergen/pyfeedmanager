from common import directlyError, HTMLFilter, tableListArticles, executeQuery
from feedparser import parse
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from config import configValues
from env_secrets import secretValues

if __name__ == "__main__":
	directlyError()

def cleanupFeeds():
	entryCount = executeQuery("SELECT COUNT(ID) FROM articles;")
	entryreadCount = executeQuery("SELECT COUNT(ID) FROM articles WHERE read = 'true';")
	if entryCount[0][0] > configValues.hardMaxFeedEntries:
		if input('The hard limit of ' + str(configValues.hardMaxFeedEntries) + ' has been reached, please confirm if want delete unread entries(' + str(entryCount[0][0]) + ') to decrease the database size [y/n]').lower() == 'y':
			toRemove = entryCount[0][0] - configValues.hardMaxFeedEntries
			executeQuery("DELETE FROM articles WHERE ID in (SELECT ID FROM articles ORDER BY addedDate ASC limit " + str(toRemove) + ");")
		else:
			pass
	elif entryreadCount[0][0] > configValues.softMaxFeedEntries:
		executeQuery("DELETE FROM articles WHERE read = 'true';")
		print("Cleanup of read feed entries performed")
	return

def updateFeeds():
	cleanupFeeds()
	todayext = datetime.now()
	today = todayext.strftime('%Y-%m-%d')
	feedRows = executeQuery("SELECT URL, LastUpdated, ID, Title FROM feeds;")
	refreshedCount = 0
	if len(feedRows) == 0:
		print('No feed could be found, please add one')
		return
	for feedRow in feedRows:
		feedUpdateDate = datetime.strptime(feedRow[1], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d')
		if today == feedUpdateDate:
			pass
		else:
			try:
				request = Request(feedRow[0], headers={'User-Agent': secretValues.http_custom_user_agent})
				feed_data = urlopen(request, timeout=3)
			except HTTPError as e:
				print('Opening ' + feedRow[0] + ' has failed with the httpd code ' + str(e.code))
				continue
			except URLError:
				print(feedRow[0] + ' could not be resolved or an unknown error occured')
				continue
			except TimeoutError:
				print(feedRow[0] + ' took too long to respond')
				continue
			content = parse(feed_data)
			if len(content.entries) == 0:
				pass
			else:
				for entry in content.entries:
					uniqueCheck = executeQuery("SELECT ID FROM articles WHERE URL = ?;", (entry.link,))
					if uniqueCheck == []:
						text2html = HTMLFilter()
						text2html.feed(entry.summary)
						executeQuery("INSERT OR IGNORE INTO articles (Title, Summary, URL, feed_id, read, addedDate, articleDate) VALUES (?,?,?,?,'false',?,?);", (entry.title,text2html.text[:50],entry.link,str(feedRow[2]),todayext, entry.published))
				print(str(feedRow[3]) + ' was processed')
				refreshedCount += 1
			executeQuery("UPDATE feeds SET LastUpdated ='" + str(todayext) + "' WHERE ID = ?;", (str(feedRow[2]),))
	if refreshedCount == 0:
		print('All feeds have already been updated today, no refresh.')

def loadArticles():
	articlesList = executeQuery("SELECT Title, Summary, URL FROM articles WHERE read ='false';")
	executeQuery("UPDATE articles SET read = 'true' WHERE read ='false';")
	return(articlesList)

def viewArticles():
	while True:
		articlesListUnread = executeQuery("SELECT Title, Summary, articleDate, URL FROM articles WHERE read ='false';")
		if articlesListUnread == []:
			updateFeeds()
			articlesListUnread = executeQuery("SELECT Title, Summary, articleDate, URL FROM articles WHERE read ='false';")
			if articlesListUnread == []:
				pass
			else:
				tableListArticles(articlesListUnread)
			break
		else:
			tableListArticles(articlesListUnread)
			break