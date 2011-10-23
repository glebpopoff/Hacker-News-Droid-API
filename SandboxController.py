#!/usr/bin/env python
#
# Hacker News Droid API: returns best articles in JSON or XML using HTML Parser
# Gleb Popov. September 2011
#

import os
import re
import logging
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
from BeautifulSoup import BeautifulSoup
from google.appengine.api import urlfetch

class HackerNewsSandboxHandler(webapp.RequestHandler):
	def get(self):
		try:
			result = urlfetch.fetch(url=AppConfig.hackerNewsURL, deadline=30)
			self.response.out.write(result.status_code)
			self.response.out.write(result.content)
		except:
			self.response.out.write('unable to get data')