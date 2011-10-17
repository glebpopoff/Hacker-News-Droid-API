#!/usr/bin/env python
#
# Hacker News Droid API: returns comments for a given post id in JSON or XML using HTML Parser
# Gleb Popov. September 2011
#

import os
import re
import logging
import datetime
import time
from UserString import MutableString
from google.appengine.api import urlfetch
from google.appengine.ext import webapp 
from google.appengine.ext import db
from google.appengine.ext.webapp import util
import Formatter
import AppConfig
import GAHelper
from xml.sax.saxutils import escape
import APIUtils
import GAHelper
from BeautifulSoup import BeautifulSoup

class HackerNewsCommentsHandler(webapp.RequestHandler):
	
	#controller main entry		
	def get(self,format,id):
		#set content-type
		self.response.headers['Content-Type'] = Formatter.contentType(format)
		
		referer = ''
		if ('HTTP_REFERER' in os.environ):
			referer = os.environ['HTTP_REFERER']
		
		returnData = MutableString()
		returnData = APIUtils.getHackerNewsComments(id,format,self.request.url, referer, self.request.remote_addr)
			
		#track this request
		GAHelper.trackGARequests('/comments/%s' % (id), self.request.remote_addr, referer)
		
		if (not returnData):
			returnData = ''
		
		#output to the browser
		self.response.out.write(Formatter.dataWrapper(format, returnData))