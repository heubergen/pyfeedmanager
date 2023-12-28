from sqlite3 import connect
from html.parser import HTMLParser
from validators import url as validators_url
from feedparser import parse as feedparser
from tabulate import tabulate
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from sys import version_info
from categories import chooseCategory

db = 'data.sqlite'
http_custom_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0'
version = '0.1.0'

def directlyError():
    raise SystemError('You must not open this file directly!')

if __name__ == "__main__":
    directlyError()

class HTMLFilter(HTMLParser):
    text = ""
    def handle_data(self, data):
        self.text += data

def unexpectedMatch():
	raise AttributeError('An unknown choice was made, please report this to the author.')

def executeQuery(DbQuery, params=None):
	try:
		conn = connect(db)
		with conn:
			cur = conn.cursor()
			if params is None:
				cur.execute(DbQuery)
			else:
				cur.execute(DbQuery, params)
			return cur.fetchall()
	finally:
		conn.close()

def validateURL(unsafeInput):
	unsafeInput = unsafeInput.replace(" ", "")
	if validators_url(unsafeInput):
		try:
			request = Request(unsafeInput, headers={'User-Agent': http_custom_user_agent})
			feed_data = urlopen(request, timeout=3)
		except HTTPError as e:
			errorMsg = 'Opening ' + unsafeInput + ' has failed with the httpd code ' + str(e.code)
			return False,errorMsg
		except URLError:
			errorMsg = unsafeInput + ' could not be resolved or an unknown error occured'
			return False,errorMsg
		try:
			result = feedparser(feed_data.read().decode('utf-8'))
			if (len(result['entries'])) > 0:
				return unsafeInput, result.feed.title, result.version
			else:
				errorMsg = unsafeInput + ' is not a feed or has no entries'
				return False,errorMsg
		except KeyError:
			errorMsg = 'An unexpected error has occured when parsing ' + unsafeInput + ' , please report this issue to the author.'
			return False,errorMsg
	else:
		errorMsg = unsafeInput + ' is not an URL'
		return False,errorMsg
	
def tableListArticles(articlesListUnread):
	print(tabulate(articlesListUnread, headers=["Title","Summary", "Article Date", "URL"]))
	if input('Please confirm that you want to mark all entries as read [y/n] ').lower() == 'y':
		executeQuery("UPDATE articles SET read = 'true' WHERE read ='false';")

def printVersion():
	print("py-feed-manager v" + version + "\nPython v" + str(version_info[0]) + "." + str(version_info[1])+ "." + str(version_info[2]))

def addFeed(feedURL, feedTitle, feedVersion):
	feedCategoryID = chooseCategory()
	uniqueCheck = executeQuery("SELECT * FROM feeds WHERE URL = ?", (feedURL,))
	if not uniqueCheck:
		executeQuery("INSERT OR IGNORE INTO feeds (URL, Title, Type, Category_ID) VALUES (?,?,?,?);", (feedURL,feedTitle,feedVersion,feedCategoryID[0][0]))
		print(feedTitle + ' added, after the next refresh the articles will be visible')
	else:
		print(feedTitle + ' already exists.')