#!/usr/bin/env python
#
# Hacker News Droid API: returns newest articles in JSON or XML using HTML Parser
# Gleb Popov. September 2011
#

import os
from google.appengine.ext import webapp
import Formatter
import GAHelper
import APIContent


class HackerNewsNewestHandler(webapp.RequestHandler):

    #controller main entry
    def get(self, format='json', page=''):
        #set content-type
        self.response.headers['Content-Type'] = Formatter.contentType(format)

        referer = ''
        if ('HTTP_REFERER' in os.environ):
            referer = os.environ['HTTP_REFERER']

        returnData = APIContent.getHackerNewsNewestContent(page, format, self.request.url, referer, self.request.remote_addr)
        if (not returnData or returnData == None or returnData == '' or returnData == 'None'):
            #call the service again this time without the pageID
            returnData = APIContent.getHackerNewsNewestContent('', format, self.request.url, referer, self.request.remote_addr)

        #track this request
        GAHelper.trackGARequests('/newest', self.request.remote_addr, referer)

        #output to the browser
        self.response.out.write(Formatter.dataWrapper(format, returnData, self.request.get('callback')))
