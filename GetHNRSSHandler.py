#!/usr/bin/env python
#
# Hacker News Droid API: returns RSS feed from the HN website in JSON or XML
# Gleb Popov. September 2011
#

import os
from google.appengine.ext import webapp
from UserString import MutableString
import Formatter
import GAHelper
import APIContent


class HackerNewsRSSHandler(webapp.RequestHandler):
    #controller main entry
    def get(self, format='json'):
        #set content-type
        self.response.headers['Content-Type'] = Formatter.contentType(format)

        returnData = MutableString()
        returnData = APIContent.getHackerNewsRSS(format)

        referer = ''
        if ('HTTP_REFERER' in os.environ):
            referer = os.environ['HTTP_REFERER']

        #track this request
        GAHelper.trackGARequests('/rss', self.request.remote_addr, referer)

        #output to the browser
        self.response.out.write(Formatter.dataWrapper(format, returnData, self.request.get('callback')))
