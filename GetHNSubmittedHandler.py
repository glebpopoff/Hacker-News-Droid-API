#!/usr/bin/env python
#
# Hacker News Droid API: returns user submitted content by username in JSON or XML using HTML Parser
# Gleb Popov. September 2011
#

import os
import re
import logging
import datetime
import time
from UserString import MutableString
from django.utils import simplejson
from google.appengine.ext import webapp 
from google.appengine.ext import db
from google.appengine.ext.webapp import util
import Formatter
import AppConfig
import GAHelper
from xml.sax.saxutils import escape
import APIUtils
import GAHelper

class HackerNewsSubmittedHandler(webapp.RequestHandler):
	#controller main entry		
	def get(self,format,user):
		#set content-type
		self.response.headers['Content-Type'] = Formatter.contentType(format)
		
		referer = ''
		if ('HTTP_REFERER' in os.environ):
			referer = os.environ['HTTP_REFERER']
		
		returnData = MutableString()
		returnData = APIUtils.getHackerNewsSubmittedContent(user,format,self.request.url, referer, self.request.remote_addr)
			
		#track this request
		GAHelper.trackGARequests('/submitted/%s' % (user), self.request.remote_addr, referer)
		
		if (not returnData):
			returnData = ''
		
		#output to the browser
		self.response.out.write(Formatter.dataWrapper(format, returnData))