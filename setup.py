from common import executeQuery, directlyError

if __name__ == "__main__":
	directlyError()

def init_db():
    count = 0
    if executeQuery("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='feeds';")[0][0] == 0:
        executeQuery("CREATE TABLE 'feeds' ( 'ID' INTEGER UNIQUE, 'Title' TEXT UNIQUE, 'URL' TEXT NOT NULL UNIQUE, 'LastUpdated' TEXT DEFAULT '1970-01-01 00:00:00.000', 'Type' INTEGER, 'Category_id' INTEGER, PRIMARY KEY('ID' AUTOINCREMENT) )")
        count += 1
    elif executeQuery("SELECT count(*) FROM feeds;")[0][0] == 0:
        count += 1

    if executeQuery("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='categories';")[0][0] == 0:
        executeQuery("CREATE TABLE 'categories' ( 'ID' INTEGER, 'Name' TEXT, PRIMARY KEY('ID' AUTOINCREMENT) )")
        count += 1
    elif executeQuery("SELECT count(*) FROM categories;")[0][0] == 0:
        count += 1

    if executeQuery("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='articles';")[0][0] == 0:
        executeQuery("CREATE TABLE 'articles' ( 'ID' INTEGER, 'Summary' TEXT, 'Title' TEXT, 'feed_id' INTEGER, 'URL' TEXT UNIQUE, 'read' TEXT, 'addedDate' TEXT, 'articleDate' TEXT, PRIMARY KEY('ID' AUTOINCREMENT) )")
        count += 1

    return count