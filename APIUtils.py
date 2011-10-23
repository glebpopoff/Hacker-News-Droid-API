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
from BeautifulSoup import BeautifulSoup
from django.utils import simplejson
from structured import list2xml

def removeHtmlTags(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)

def removeNonAscii(s): return "" . join(filter(lambda x: ord(x)<128, s))

#call urlfetch to get remote data
def fetchRemoteData(urlStr, deadline):
	result = urlfetch.fetch(url=urlStr, deadline=deadline)
	if result.status_code == 200:
		return result
	else:
		logging.error('fetchRemoteData: unable to get remote data: %s' % urlStr)
		raise Exception("fetchRemoteData: failed")

#call remote server to get data. If failed (timeout), try again and again and again and again (4 attempts because urlfetch on the GAE f-ing sucks)
def getRemoteData(urlStr, backupUrl):
	#attempt #1
	try:	
		logging.debug('getRemoteData: Attempt #1: %s' % urlStr)
		return fetchRemoteData(urlStr, 30)
	except:
		#attempt #2
		try:
			logging.debug('getRemoteData: First attempt failed... Attempt #2(Backup URL): %s' % backupUrl)
			return fetchRemoteData(backupUrl, 30)
		except:
			#attempt #3
			try:
				logging.debug('getRemoteData: First attempt failed... Attempt #3: %s' % urlStr)
				return fetchRemoteData(urlStr, 30)
			except:
				#attempt #4
				try:
					logging.debug('getRemoteData: First attempt failed... Attempt #4 (Backup URL): %s' % backupUrl)
					return fetchRemoteData(backupUrl, 30)
				except:
					logging.error('getRemoteData: unable to get remote data...Attempt #4. Stack')
					return None
	return None

#parse content using Beautiful Soup
def parsePageContent(hnAPIUrl,hnBackupAPIUrl, apiURL, page='',format='json',limit=0):
	returnData = MutableString()
	returnData = ''
	logging.debug('HN URL: %s' % hnAPIUrl)
	
	#next page content
	if (page):
		hnAPIUrl = '%s/x?fnid=%s' % (AppConfig.hackerNewsURL, page)
	
	#call HN website to get data
	result = getRemoteData(hnAPIUrl,hnBackupAPIUrl)
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
def parseCommentsContent(hnAPIUrl, hnAPIUrlBackup, apiURL, page='',format='json'):
	returnData = MutableString()
	returnData = ''
	logging.debug('HN URL: %s' % hnAPIUrl)

	result = getRemoteData(hnAPIUrl, hnAPIUrlBackup)
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
def parseNestedCommentsContent(hnAPIUrl, hnAPIUrlBackup, apiURL, page='',format='json'):
	returnData = None
	logging.debug('HN URL: %s' % hnAPIUrl)

	result = getRemoteData(hnAPIUrl, hnAPIUrlBackup)
	if (result):
		htmlData = result.content	
		soup = BeautifulSoup(htmlData)
		urlLinksContent = soup('table')
		counter = 0
		comment_container = {}
		for node in urlLinksContent:
			commentTd = node.first('td', {'class' : 'default'})
			if (commentTd):
				previousTds = commentTd.fetchPreviousSiblings('td')
				nestLevel = int(previousTds[-1].first('img')['width'])/40

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
					comment_container[counter] =	[
														commentId,
														user.string,
														timePosted.strip(),
														commentString,
														replyLink,
														nestLevel
													]
					counter = counter + 1
			
		#build up string	
		commentKeyContainer = {}
		nestLevels = []
		comments = []
		for key in comment_container.keys():
			comment = {}
			listCommentData = comment_container[key]
			if (listCommentData and not commentKeyContainer.has_key(listCommentData[0])):
				commentId = listCommentData[0]
				if (commentId):
					commentKeyContainer[commentId] = 1
				userName = listCommentData[1]
				whenPosted = listCommentData[2]
				commentsString = listCommentData[3]
				replyId = listCommentData[4]
				nestLevel = listCommentData[5]
				
				if (format == 'json'):

					#cleanup
					if (commentsString):
						commentsString = re.sub("\"", "\\\"", commentsString)
						commentsString = re.sub("\n", "", commentsString)
						commentsString = re.sub("\t", " ", commentsString)
						commentsString = re.sub("\r", "", commentsString)

					if (len(commentsString) > 0):
						commentsString = escape(removeNonAscii(commentsString))[:-1]
					else:
						commentsString = "n/a "
				else:
					if (len(userName) > 0):
						userName = escape(removeNonAscii(userName))

					if (len(whenPosted) > 0):
						whenPosted = escape(whenPosted)

					if (len(commentsString) > 0):
						commentsString = escape(removeNonAscii(commentsString))

				if (commentId and userName and whenPosted and replyId and commentsString):
					comment['children'] = []

					if (len(commentId) > 0):
						comment['id'] = commentId
							
					if (len(userName) > 0):
						comment['username'] = userName

					if (len(whenPosted) > 0):
						comment['time'] = whenPosted

					if (len(replyId) > 0):
						comment['reply_id'] = escape(replyId)

					if (len(commentsString) > 0 ):
						comment['comment'] = commentsString

					if nestLevel == 0:
						comments.append(comment)
					else:
						nestLevels[nestLevel - 1]['children'].append(comment)
					nestLevels.insert(nestLevel, comment)

	if (format == 'json'):
		returnData = simplejson.dumps(comments)
	else:
		returnData = list2xml(comments, 'root', 'record', listnames = {'children': 'record'})
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
