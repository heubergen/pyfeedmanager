from common import validateURL, addFeedFromOPML
from xml.etree.ElementTree import parse as xmlparse, ParseError
from categories import addCategory, getCategoryID

def opmlChildProcess(childsub,feedCategory):
	feedURL = childsub.attrib["xmlUrl"]
	safeInput = validateURL(feedURL)
	if safeInput[0] == False:
		print(safeInput[1])
	else:
		addCategory(feedCategory)
		categoryID = getCategoryID(feedCategory)
		print('Adding ' + safeInput[1] + ' to the database')
		addFeedFromOPML(safeInput[0],safeInput[1],safeInput[2],categoryID)


def opmlImport(opmlFile):
	print('Processing ' + opmlFile)
	try:
		tree = xmlparse(opmlFile)
		root = tree.getroot()
		try:
			root.findall('.*/outline')[0].attrib["xmlUrl"] # If the first outline element is an entry we assume the opml file is flat
		except KeyError:
			for childmain in root.findall('.*/outline'):
				feedCategory = childmain.attrib["title"]
				for childsub in childmain.findall('.*'):
					opmlChildProcess(childsub,feedCategory)
		else:
			feedCategory = input('OPML does not provide the category, please add it now: ')
			for childsub in root.findall('.*/outline'):
					opmlChildProcess(childsub,feedCategory)

	except ParseError:
		raise ParseError(opmlFile + ' is not a valid XML file, please fix it or remove the file')