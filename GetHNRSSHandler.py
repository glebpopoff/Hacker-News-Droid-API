#!/usr/bin/env python
#
# Hacker News Droid API: returns RSS feed from the HN website in JSON or XML
# Gleb Popov. September 2011
#

import re
import os
import logging
from google.appengine.api import urlfetch
from django.utils import simplejson
from google.appengine.ext import webapp 
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from UserString import MutableString
import AppConfig
import Formatter
import GAHelper
from xml.sax.saxutils import escape
import APIUtils

class HackerNewsRSSHandler(webapp.RequestHandler):
	#controller main entry		
	def get(self,format='json'):
		#set content-type
		self.response.headers['Content-Type'] = Formatter.contentType(format)
		
		returnData = MutableString()
		returnData = APIUtils.getHackerNewsRSS(format)
		
		referer = ''
		if ('HTTP_REFERER' in os.environ):
			referer = os.environ['HTTP_REFERER']
		
		#track this request
		GAHelper.trackGARequests('/rss', self.request.remote_addr, referer)
					
		#output to the browser
		self.response.out.write(Formatter.dataWrapper(format, returnData))