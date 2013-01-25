#!/usr/bin/env python
#
# Hacker News Droid API: returns post data by ID
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
import APIContent
import GAHelper
from BeautifulSoup import BeautifulSoup

class HackerNewsPostHandler(webapp.RequestHandler):
	
	#controller main entry		
	def get(self,format,id):
		#set content-type
		self.response.headers['Content-Type'] = Formatter.contentType(format)
		
		#get consumer/client app id
		appid = 'Unknown'
		if (self.request.GET):
			if ('appid' in self.request.GET):
				appid = self.request.GET['appid']
			if ('app' in self.request.GET):
				appid = self.request.GET['app']
		
		referer = ''
		if ('HTTP_REFERER' in os.environ):
			referer = os.environ['HTTP_REFERER']
		
		returnData = APIContent.getHackerNewsPost(id,format,self.request.url, referer, self.request.remote_addr)
			
		#track this request
		GAHelper.trackGARequests('/post/%s' % (id), appid, referer)
		
		if (not returnData):
			returnData = ''
		
		#output to the browser
		self.response.out.write(Formatter.dataWrapper(format, returnData, self.request.get('callback')))
