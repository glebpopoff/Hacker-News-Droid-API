#
# Main Library to parse Hacker News homepage, rss, newest, and best content
#

from UserString import MutableString
import re
import logging
import Formatter
from xml.dom import minidom
from xml.sax.saxutils import escape
import urllib
import AppConfig
from google.appengine.api import urlfetch
import DataCache
from BeautifulSoup import BeautifulSoup

def removeHtmlTags(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)

def removeNonAscii(s): return "" . join(filter(lambda x: ord(x)<128, s))

#get cached content
def getCache(pageId,format):
	logging.debug('getCache: %s' % pageId)
	dbData = DataCache.getData(pageId,format)
	if (dbData):
		if (DataCache.hasExpired(dbData)):
			#data has expired, remove it
			dbData[0].delete()
			return None
		else:
			logging.debug('getCache: got cached data for id %s' % id)
			return dbData[0].rec_xml	

#parse HN's submissions by user
def getHackerNewsSubmittedContent(user, format='json', url='', referer='', remote_addr=''):
	#only cache homepage data
	apiURL = "%s/submitted?id=%s" % (AppConfig.hackerNewsURL, user)
	id = '/submitted/%s' % (user)
	cachedData = getCache(id,format)
	if (cachedData):
		return cachedData
	else:
		hnData = parsePageContent(apiURL, '/submitted', None,format)
		if (hnData):
			logging.debug('getHackerNewsSubmittedContent: storing cached value for id %s' % id)
			DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
			return hnData
		else:
			logging.warning('getHackerNewsSubmittedContent: unable to retrieve data for id %s' % id)
			return ''

#parse HN's comments by story id
def getHackerNewsComments(articleId, format='json', url='', referer='', remote_addr=''):
	#only cache homepage data
	apiURL = "%s/item?id=%s" % (AppConfig.hackerNewsURL, articleId)
	id = '/comments/%s' % (articleId)
	cachedData = getCache(id,format)
	if (cachedData):
		return cachedData
	else:
		hnData = parseCommentsContent(apiURL, '/comments', None,format)
		if (hnData):
			logging.debug('getHackerNewsComments: storing cached value for id %s' % id)
			DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
			return hnData
		else:
			logging.warning('getHackerNewsComments: unable to retrieve data for id %s' % id)
			return ''	

#parse HN's comments by story id
def getHackerNewsNestedComments(articleId, format='json', url='', referer='', remote_addr=''):
	#only cache homepage data
	apiURL = "%s/item?id=%s" % (AppConfig.hackerNewsURL, articleId)
	id = '/comments/%s' % (articleId)
	cachedData = getCache(id,format)
	if (cachedData):
		return cachedData
	else:
		hnData = parseCommentsContent(apiURL, '/comments', None,format)
		if (hnData):
			logging.debug('getHackerNewsComments: storing cached value for id %s' % id)
			DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
			return hnData
		else:
			logging.warning('getHackerNewsComments: unable to retrieve data for id %s' % id)
			return ''	

#parse HN's ask content
def getHackerNewsAskContent(page='', format='json', url='', referer='', remote_addr=''):
	#only cache homepage data
	if (page):
		return parsePageContent(AppConfig.hackerNewsAskURL, '/ask', page,format)
	else:
		id = '/ask/'
		cachedData = getCache(id,format)
		if (cachedData):
			return cachedData
		else:
			hnData = parsePageContent(AppConfig.hackerNewsAskURL, '/ask', page,format)
			if (hnData):
				logging.debug('getCache: storing cached value for id %s' % id)
				DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
				return hnData
			else:
				logging.warning('getCache: unable to retrieve data for id %s' % id)
				return ''

#parse HN's best content
def getHackerNewsBestContent(page='', format='json', url='', referer='', remote_addr=''):
	#only cache homepage data
	if (page):
		return parsePageContent(AppConfig.hackerNewsBestURL, '/best', page,format)
	else:
		id = '/best/'
		cachedData = getCache(id,format)
		if (cachedData):
			return cachedData
		else:
			hnData = parsePageContent(AppConfig.hackerNewsBestURL, '/best', page,format)
			if (hnData):
				logging.debug('getCache: storing cached value for id %s' % id)
				DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
				return hnData
			else:
				logging.warning('getCache: unable to retrieve data for id %s' % id)
				return ''

#parse HN's newest content
def getHackerNewsNewestContent(page='', format='json', url='', referer='', remote_addr=''):
	#only cache homepage data
	if (page):
		return parsePageContent(AppConfig.hackerNewsNewestURL, '/newest', page,format)
	else:
		id = '/newest/'
		cachedData = getCache(id,format)
		if (cachedData):
			return cachedData
		else:
			hnData = parsePageContent(AppConfig.hackerNewsNewestURL, '/newest', page,format)
			if (hnData):
				logging.debug('getCache: storing cached value for id %s' % id)
				DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
				return hnData
			else:
				logging.warning('getCache: unable to retrieve data for id %s' % id)
				return ''


#get homepage second page stories
def getHackerNewsSecondPageContent(page='', format='json', url='', referer='', remote_addr=''):
	#only cache homepage data
	if (page):
		return parsePageContent(AppConfig.hackerNewsPage2URL, '/news', page,format)
	else:
		id = '/news2'
		cachedData = getCache(id,format)
		if (cachedData):
			return cachedData
		else:
			hnData = parsePageContent(AppConfig.hackerNewsPage2URL, '/news', page,format)
			if (hnData):
				logging.debug('getCache: storing cached value for id %s' % id)
				DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
				return hnData
			else:
				logging.warning('getCache: unable to retrieve data for id %s' % id)
				return ''
								
#get latest homepage stories
def getHackerNewsLatestContent(page='', format='json', url='', referer='', remote_addr='', limit=1):
	#only cache homepage data
	limit = int(limit)
	if (page):
		return parsePageContent(AppConfig.hackerNewsURL, '/latest', page,format,limit)
	else:
		id = '/latest/%s' % limit
		cachedData = getCache(id,format)
		if (cachedData):
			return cachedData
		else:
			hnData = parsePageContent(AppConfig.hackerNewsURL, '/latest', page,format,limit)
			if (hnData):
				logging.debug('getCache: storing cached value for id %s' % id)
				DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
				return hnData
			else:
				logging.warning('getCache: unable to retrieve data for id %s' % id)
				return ''

#parse HN's homepage
def getHackerNewsPageContent(page='', format='json', url='', referer='', remote_addr=''):
	#only cache homepage data
	if (page):
		return parsePageContent(AppConfig.hackerNewsURL, '/news', page,format)
	else:
		id = '/news/'
		cachedData = getCache(id,format)
		if (cachedData):
			return cachedData
		else:
			hnData = parsePageContent(AppConfig.hackerNewsURL, '/news', page,format)
			if (hnData):
				logging.debug('getCache: storing cached value for id %s' % id)
				DataCache.putData(id, format,removeNonAscii(hnData), url, referer, remote_addr)
				return hnData
			else:
				logging.warning('getCache: unable to retrieve data for id %s' % id)
				return ''

#call remote server to get data. If failed (timeout), try again
def getRemoteData(urlStr):
	try:	
		logging.debug('getRemoteData: Attempt #1: %s' % urlStr)
		result = urlfetch.fetch(url=urlStr, deadline=30)
		if result.status_code == 200:
			return result
		else:
			logging.error('getRemoteData: unable to get remote data...Attempt #1')
			return None
	except:
		#lets try to resubmit the request
		try:
			logging.debug('getRemoteData: First attempt failed... Attempt #2: %s' % urlStr)
			result = urlfetch.fetch(url=urlStr, deadline=30)
			if result.status_code == 200:
				return result
			else:
				logging.error('getRemoteData: unable to get remote data...Attempt #2')
				return None
		except:
			logging.error('getRemoteData: unable to get remote data...Attempt #2')
			return None
	return jsonData

#parse content using Beautiful Soup
def parsePageContent(hnAPIUrl, apiURL, page='',format='json',limit=0):
	returnData = MutableString()
	returnData = ''
	logging.debug('HN URL: %s' % hnAPIUrl)
	
	#next page content
	if (page):
		hnAPIUrl = '%s/x?fnid=%s' % (AppConfig.hackerNewsURL, page)
	
	#call HN website to get data
	result = getRemoteData(hnAPIUrl)
	if (result):
		htmlData = result.content	
		soup = BeautifulSoup(htmlData)
		urlLinksContent = soup('td', {'class' : 'title'})
		counter = 0
		url_links = {}
		for node in urlLinksContent:
			if (node.a):
				url_links[counter] = [node.a['href'], node.a.string]
				counter = counter + 1
				if (limit > 0 and counter == limit):
					break;
		
		#get comments & the rest
		commentsContent = soup('td', {'class' : 'subtext'})
		counter = 0
		comments_stuff = {}
		for node in commentsContent:
			if (node):
				#parsing this
				#<td class="subtext"><span id="score_3002117">110 points</span> by <a href="user?id=JoelSutherland">JoelSutherland</a> 3 hours ago  | <a href="item?id=3002117">36 comments</a></td>
				nodeString = removeHtmlTags(str(node))
				score = node.first('span', {'id' : re.compile('^score.*')}).string
				user = node.first('a', {'href' : re.compile('^user.*')}).string
				itemId = node.first('a', {'href' : re.compile('^item.*')})["href"]
				comments = node.first('a', {'href' : re.compile('^item.*')}).string
				#since 'XX hours ago' string isn't part of any element we need to simply search and replace other text to get it
				timeAgo = nodeString.replace(str(score), '')
				timeAgo = timeAgo.replace('by %s' % str(user), '')
				timeAgo = timeAgo.replace(str(comments), '')
				timeAgo = timeAgo.replace('|', '')
				comments_stuff[counter] = [score, user, comments, timeAgo.strip(), itemId, nodeString]
				counter = counter + 1
				if (limit > 0 and counter == limit):
					break;
		
		#build up string		
		for key in url_links.keys():
			tupURL = url_links[key]
			if (key in comments_stuff):
				tupComments = comments_stuff[key]
			else:
				tupComments = None
			if (tupURL):
				url = ''
				title = ''
				score = ''
				user = ''
				comments = ''
				timeAgo = ''
				itemId = ''
				itemInfo = ''
				
				#assign vars
				url = tupURL[0]
				title = tupURL[1]
				
				if (tupComments):
					score = tupComments[0]
					user = tupComments[1]
					comments = tupComments[2]
					timeAgo = tupComments[3]
					itemId = tupComments[4]
					itemInfo = tupComments[5]
				else:
					#need this for formatting
					itemInfo = 'n/a '
				
				#last record (either news2 or x?fnid)
				if (title.lower() == 'more' or '/x?fnid' in url):
					title = 'NextId'
					if ('/x?fnid' in url):
						url = '%s/format/%s/page/%s' % (apiURL, format, url.replace('/x?fnid=', ''))
					else:
						url = '/news2'
					itemInfo = 'hn next id %s ' % tupURL[0]
				
				if (format == 'json'):
					startTag = '{'
					endTag = '},'
					
					#cleanup
					if (title):
						title = re.sub("\n", "", title)
						title = re.sub("\"", "\\\"", title)
					
					if (itemInfo):
						itemInfo = re.sub("\"", "\\\"", itemInfo)
						itemInfo = re.sub("\n", "", itemInfo)
						itemInfo = re.sub("\t", " ", itemInfo)
						itemInfo = re.sub("\r", "", itemInfo)

					if (len(itemInfo) > 0):
						itemInfo = Formatter.data(format, 'description', escape(itemInfo))[:-1]
				else:
					startTag = '<record>'
					endTag = '</record>'
					if (len(title) > 0):
						title = escape(removeNonAscii(title))
						
					if (len(url) > 0):
						url = escape(url)
					
					if (len(user) > 0):
						user = escape(user)
						
					if (len(itemInfo) > 0):
						itemInfo = Formatter.data(format, 'description', escape(itemInfo))								

				if (len(title) > 0):
					returnData += startTag + Formatter.data(format, 'title', title)

				if (len(url) > 0):
					returnData += Formatter.data(format, 'url', url) 

				if (len(score) > 0):
					returnData += Formatter.data(format, 'score', score)
					
				if (len(user) > 0):
					returnData += Formatter.data(format, 'user', user)
				
				if (len(comments) > 0):
					returnData += Formatter.data(format, 'comments', comments)

				if (len(timeAgo) > 0):
					returnData += Formatter.data(format, 'time', timeAgo)
					
				if (len(itemId) > 0):
					#cleanup
					if ('item?id=' in itemId):
						itemId = itemId.replace('item?id=', '')
					returnData += Formatter.data(format, 'item_id', itemId)

				if (len(itemInfo) > 0 ):
					returnData += itemInfo + endTag
	else:
		returnData = None
	
	return returnData

#retrieves multi-paragraph comments
def getParagraphCommentSiblings(node):
	nodeText = MutableString()
	if (node):
		#get first paragraph
		nodeText = str(node.font)
		nextSib = node.nextSibling
		if (nextSib and "<p>" in str(nextSib)):
			while (nextSib and "<p>" in str(nextSib)):
				tmpStr = str(nextSib)
				if (nodeText):
					nodeText += "__BR__%s" % tmpStr
				else:
					nodeText = tmpStr
				nextSib = nextSib.nextSibling
		return nodeText

#parse comments using Beautiful Soup
def parseCommentsContent(hnAPIUrl, apiURL, page='',format='json'):
	returnData = MutableString()
	returnData = ''
	logging.debug('HN URL: %s' % hnAPIUrl)

	result = getRemoteData(hnAPIUrl)
	if (result):
		htmlData = result.content	
		soup = BeautifulSoup(htmlData)
		urlLinksContent = soup('table')
		counter = 0
		comment_container = {}
		for node in urlLinksContent:
			commentTd = node.first('td', {'class' : 'default'})
			if (commentTd):
				authorSpan = commentTd.first('span', {'class' : 'comhead'})
				#multi-paragraph comments are a bit tricky, parser wont' retrieve them using "span class:comment" selector
				commentSpan = getParagraphCommentSiblings(commentTd.first('span', {'class' : 'comment'}))
				replyLink = commentTd.first('a', {'href' : re.compile('^reply.*')})['href']
				if (replyLink and "reply?id=" in replyLink):
					replyLink = replyLink.replace('reply?id=', '')
				if (authorSpan and commentSpan):
					#author span: <span class="comhead"><a href="user?id=dendory">dendory</a> 1 day ago  | <a href="item?id=3015166">link</a></span>
					commentId = authorSpan.first('a', {'href' : re.compile('^item.*')})
					user = authorSpan.first('a', {'href' : re.compile('^user.*')})
					#get time posted...lame but works. for some reason authorSpan.string returns NULL
					timePosted = str(authorSpan).replace('<span class="comhead">', '').replace('</span>', '')
					#now replace commentId and user blocks
					timePosted = timePosted.replace(str(user), '').replace('| ', '').replace(str(commentId), '')
					if (commentId['href'] and "item?id=" in commentId['href']):
						commentId = commentId['href'].replace('item?id=', '')
					#cleanup
					commentString = removeHtmlTags(str(commentSpan))
					if ('__BR__reply' in commentString):
						commentString = commentString.replace('__BR__reply', '')
					comment_container[counter] = [commentId, user.string, timePosted.strip(), commentString, replyLink]
					counter = counter + 1
			
		#build up string	
		commentKeyContainer = {}	
		for key in comment_container.keys():
			listCommentData = comment_container[key]
			if (listCommentData and not commentKeyContainer.has_key(listCommentData[0])):
				commentId = listCommentData[0]
				if (commentId):
					commentKeyContainer[commentId] = 1
				userName = listCommentData[1]
				whenPosted = listCommentData[2]
				commentsString = listCommentData[3]
				replyId = listCommentData[4]
				
				if (format == 'json'):
					startTag = '{'
					endTag = '},'

					#cleanup
					if (commentsString):
						commentsString = re.sub("\"", "\\\"", commentsString)
						commentsString = re.sub("\n", "", commentsString)
						commentsString = re.sub("\t", " ", commentsString)
						commentsString = re.sub("\r", "", commentsString)

					if (len(commentsString) > 0):
						commentsString = Formatter.data(format, 'comment', escape(removeNonAscii(commentsString)))[:-1]
					else:
						commentsString = "n/a "
				else:
					startTag = '<record>'
					endTag = '</record>'
					if (len(userName) > 0):
						userName = escape(removeNonAscii(userName))

					if (len(whenPosted) > 0):
						whenPosted = escape(whenPosted)

					if (len(commentsString) > 0):
						commentsString = Formatter.data(format, 'comment', escape(removeNonAscii(commentsString)))								

				if (commentId and userName and whenPosted and replyId and commentsString):
					if (len(commentId) > 0):
						returnData += startTag + Formatter.data(format, 'id', commentId)
							
					if (len(userName) > 0):
						returnData += Formatter.data(format, 'username', userName)

					if (len(whenPosted) > 0):
						returnData += Formatter.data(format, 'time', whenPosted)

					if (len(replyId) > 0):
						returnData += Formatter.data(format, 'reply_id', escape(replyId))

					if (len(commentsString) > 0 ):
						returnData += commentsString + endTag
	else:
		returnData = None

	return returnData

#parse comments using Beautiful Soup
def parseNestedCommentsContent(hnAPIUrl, apiURL, page='',format='json'):
	returnData = MutableString()
	returnData = ''
	logging.debug('HN URL: %s' % hnAPIUrl)

	result = getRemoteData(hnAPIUrl)
	if (result):
		htmlData = result.content	
		soup = BeautifulSoup(htmlData)
		urlLinksContent = soup('table')
		counter = 0
		comment_container = {}
		for node in urlLinksContent:
			commentTd = node.first('td', {'class' : 'default'})
			if (commentTd):
				authorSpan = commentTd.first('span', {'class' : 'comhead'})
				#multi-paragraph comments are a bit tricky, parser wont' retrieve them using "span class:comment" selector
				commentSpan = getParagraphCommentSiblings(commentTd.first('span', {'class' : 'comment'}))
				replyLink = commentTd.first('a', {'href' : re.compile('^reply.*')})['href']
				if (replyLink and "reply?id=" in replyLink):
					replyLink = replyLink.replace('reply?id=', '')
				if (authorSpan and commentSpan):
					#author span: <span class="comhead"><a href="user?id=dendory">dendory</a> 1 day ago  | <a href="item?id=3015166">link</a></span>
					commentId = authorSpan.first('a', {'href' : re.compile('^item.*')})
					user = authorSpan.first('a', {'href' : re.compile('^user.*')})
					#get time posted...lame but works. for some reason authorSpan.string returns NULL
					timePosted = str(authorSpan).replace('<span class="comhead">', '').replace('</span>', '')
					#now replace commentId and user blocks
					timePosted = timePosted.replace(str(user), '').replace('| ', '').replace(str(commentId), '')
					if (commentId['href'] and "item?id=" in commentId['href']):
						commentId = commentId['href'].replace('item?id=', '')
					#cleanup
					commentString = removeHtmlTags(str(commentSpan))
					if ('__BR__reply' in commentString):
						commentString = commentString.replace('__BR__reply', '')
					comment_container[counter] = [commentId, user.string, timePosted.strip(), commentString, replyLink]
					counter = counter + 1
			
		#build up string	
		commentKeyContainer = {}	
		for key in comment_container.keys():
			listCommentData = comment_container[key]
			if (listCommentData and not commentKeyContainer.has_key(listCommentData[0])):
				commentId = listCommentData[0]
				if (commentId):
					commentKeyContainer[commentId] = 1
				userName = listCommentData[1]
				whenPosted = listCommentData[2]
				commentsString = listCommentData[3]
				replyId = listCommentData[4]
				
				if (format == 'json'):
					startTag = '{'
					endTag = '},'

					#cleanup
					if (commentsString):
						commentsString = re.sub("\"", "\\\"", commentsString)
						commentsString = re.sub("\n", "", commentsString)
						commentsString = re.sub("\t", " ", commentsString)
						commentsString = re.sub("\r", "", commentsString)

					if (len(commentsString) > 0):
						commentsString = Formatter.data(format, 'comment', escape(removeNonAscii(commentsString)))[:-1]
					else:
						commentsString = "n/a "
				else:
					startTag = '<record>'
					endTag = '</record>'
					if (len(userName) > 0):
						userName = escape(removeNonAscii(userName))

					if (len(whenPosted) > 0):
						whenPosted = escape(whenPosted)

					if (len(commentsString) > 0):
						commentsString = Formatter.data(format, 'comment', escape(removeNonAscii(commentsString)))								

				if (commentId and userName and whenPosted and replyId and commentsString):
					if (len(commentId) > 0):
						returnData += startTag + Formatter.data(format, 'id', commentId)
							
					if (len(userName) > 0):
						returnData += Formatter.data(format, 'username', userName)

					if (len(whenPosted) > 0):
						returnData += Formatter.data(format, 'time', whenPosted)

					if (len(replyId) > 0):
						returnData += Formatter.data(format, 'reply_id', escape(replyId))

					if (len(commentsString) > 0 ):
						returnData += commentsString + endTag
	else:
		returnData = None

	return returnData

#parse HN's RSS feed
def getHackerNewsRSS(format='json'):
	returnData = MutableString()
	returnData = ''
	dom = minidom.parse(urllib.urlopen(AppConfig.hackerNewsRSSFeed))
	rssTitle = MutableString()
	rssDescription = MutableString()
	rssURL = MutableString()
	for node in dom.getElementsByTagName('item'):
		for item_node in node.childNodes:
			rssTitle = ''
			rssDescription = ''
			rssURL = ''
			#item title
			if (item_node.nodeName == "title"):
				for text_node in item_node.childNodes:
					if (text_node.nodeType == node.TEXT_NODE):
						rssTitle += text_node.nodeValue
			#description
			if (item_node.nodeName == "description"):
				for text_node in item_node.childNodes:
					rssDescription += text_node.nodeValue
			#link to URL
			if (item_node.nodeName == "link"):
				for text_node in item_node.childNodes:
					rssURL += text_node.nodeValue
			
			if (format == 'json'):
				startTag = '{'
				endTag = '},'
				
				#cleanup
				#rssTitle = re.sub("\"", "'", rssTitle)
				rssTitle = re.sub("\n", "", rssTitle)
				rssTitle = re.sub("\"", "\\\"", rssTitle)
				rssDescription = re.sub("\"", "\\\"", rssDescription)
				rssDescription = re.sub("\n", "", rssDescription)
				rssDescription = re.sub("\t", " ", rssDescription)
				rssDescription = re.sub("\r", "", rssDescription)
				
				if (len(rssDescription) > 0):
					rssDescription = Formatter.data(format, 'description', escape(rssDescription))[:-1]
			else:
				startTag = '<record>'
				endTag = '</record>'		
				
				if (len(rssTitle) > 0):
					rssTitle = escape(removeNonAscii(rssTitle))
					
				if (len(rssURL) > 0):
					rssURL = escape(rssURL)
					
				if (len(rssDescription) > 0):
					rssDescription = Formatter.data(format, 'description', escape(rssDescription))								
			
			if (len(rssTitle) > 0):
				returnData += startTag + Formatter.data(format, 'title', rssTitle)
				
			if (len(rssURL) > 0):
				returnData += Formatter.data(format, 'url', rssURL) 
			
			if (len(rssDescription) > 0 ):
				returnData += rssDescription + endTag
	
	return returnData
