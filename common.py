from sqlite3 import connect
from html.parser import HTMLParser
from validators import url as validators_url
from feedparser import parse as feedparser
from tabulate import tabulate
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from sys import version_info
from categories import chooseCategory
from config import configValues
from env_secrets import secretValues
from bs4 import BeautifulSoup

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
		conn = connect(configValues.db)
		with conn:
			cur = conn.cursor()
			if params is None:
				cur.execute(DbQuery)
			else:
				cur.execute(DbQuery, params)
			return cur.fetchall()
	finally:
		conn.close()

def discoverFeed(content):
	soup = BeautifulSoup(content, 'html.parser')
	rss_link = soup.find('link', {'type': 'application/rss+xml'})
	atom_link = soup.find('link', {'type': 'application/atom+xml'})
	if rss_link:
		return rss_link['href']
	elif atom_link:
		return atom_link['href']
	else:
		return None

def validateURL(unsafeInput, urlWasDiscovered=None):
	unsafeInput = unsafeInput.replace(" ", "")
	if validators_url(unsafeInput):
		try:
			feed_data = urlopen(Request(unsafeInput, headers={'User-Agent': secretValues.http_custom_user_agent}), timeout=3)
		except HTTPError as e:
			errorMsg = 'Opening ' + unsafeInput + ' has failed with the httpd code ' + str(e.code)
			return False,errorMsg
		except URLError:
			errorMsg = unsafeInput + ' could not be resolved or an unknown error occurred'
			return False,errorMsg
		except TimeoutError:
			errorMsg = unsafeInput + ' timed out'
			return False,errorMsg
		try:
			content = feed_data.read().decode('utf-8')
			result = feedparser(content)
			if (len(result['entries'])) > 0:
				return unsafeInput, result.feed.title, result.version
			elif urlWasDiscovered is None:
				discoveredURL = discoverFeed(content)
				return 'Discovered',discoveredURL
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
	print("py-feed-manager v" + configValues.version + "\nPython v" + str(version_info[0]) + "." + str(version_info[1])+ "." + str(version_info[2]))

def addFeed(feedURL, feedTitle, feedVersion):
	uniqueCheck = executeQuery("SELECT * FROM feeds WHERE Title = ?", (feedTitle,))
	if not uniqueCheck:
		feedCategoryID = chooseCategory()
		executeQuery("INSERT OR IGNORE INTO feeds (URL, Title, Type, Category_ID) VALUES (?,?,?,?);", (feedURL,feedTitle,feedVersion,feedCategoryID[0][0]))
		print(feedTitle + ' added, after the next refresh the articles will be visible')
	else:
		print(feedTitle + ' already exists.')

def addFeedFromOPML(feedURL, feedTitle, feedVersion,feedCategoryID):
	uniqueCheck = executeQuery("SELECT * FROM feeds WHERE Title = ?", (feedTitle,))
	if not uniqueCheck:
		executeQuery("INSERT OR IGNORE INTO feeds (URL, Title, Type, Category_ID) VALUES (?,?,?,?);", (feedURL,feedTitle,feedVersion,feedCategoryID))
	else:
		print(feedTitle + ' already exists.')