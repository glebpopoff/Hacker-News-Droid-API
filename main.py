#!/usr/bin/env python
#
# Hacker News API for Droid
# Gleb Popov. September 2011
#
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from GetHNRSSHandler import HackerNewsRSSHandler
from GetHNSecondPageHandler import HackerNewsSecondPageHandler
from GetHNPageContentHandler import HackerNewsPageHandler
from GetHNNewestHandler import HackerNewsNewestHandler
from GetHNBestHandler import HackerNewsBestHandler
from GetHNAskHandler import HackerNewsAskHandler
from GetHNSubmittedHandler import HackerNewsSubmittedHandler
from GetHNCommentsHandler import HackerNewsCommentsHandler
from GetHNNestedCommentsHandler import HackerNewsNestedCommentsHandler
from GetHNLatestHandler import HackerNewsLatestPageHandler
from SandboxController import HackerNewsSandboxHandler
from GetHNPostHandler import HackerNewsPostHandler

class MainHandler(webapp.RequestHandler):
    def get(self):
		template_values = {'last_updated': '01/04/12'}
		path = os.path.join(os.path.dirname(__file__), 'templates')
		path = os.path.join(path, 'index.html')
		self.response.out.write(template.render(path, template_values))


def main():
    application = webapp.WSGIApplication([('/', MainHandler),
										 (r'/rss/format/(json|xml)', HackerNewsRSSHandler),
										 ('/rss', HackerNewsRSSHandler),
										 ('/sandbox', HackerNewsSandboxHandler),
										 ('/latest', HackerNewsLatestPageHandler),
										 ('/latest/format/(json|xml)/limit/(.*)', HackerNewsLatestPageHandler),
										 ('/news', HackerNewsPageHandler),
										 ('/news2', HackerNewsSecondPageHandler),
										 ('/news/format/(json|xml)', HackerNewsPageHandler),
										 ('/news2/format/(json|xml)', HackerNewsPageHandler),
										 (r'/news/format/(json|xml)/page/(.*)', HackerNewsPageHandler),
										 (r'/news2/format/(json|xml)/page/(.*)', HackerNewsPageHandler),
										 ('/newest', HackerNewsNewestHandler),
										 ('/newest/format/(json|xml)', HackerNewsNewestHandler),
										 (r'/newest/format/(json|xml)/page/(.*)', HackerNewsNewestHandler),
										 ('/best', HackerNewsBestHandler),
										 ('/best/format/(json|xml)', HackerNewsBestHandler),
										 (r'/best/format/(json|xml)/page/(.*)', HackerNewsBestHandler),
										 ('/ask', HackerNewsAskHandler),
										 ('/ask/format/(json|xml)', HackerNewsAskHandler),
										 (r'/ask/format/(json|xml)/page/(.*)', HackerNewsAskHandler),
										 (r'/submitted/format/(json|xml)/user/(.*)', HackerNewsSubmittedHandler),
										 (r'/comments/format/(json|xml)/id/(.*)', HackerNewsCommentsHandler),
										 (r'/nestedcomments/format/(json|xml)/id/(.*)', HackerNewsNestedCommentsHandler),
										 (r'/post/format/(json|xml)/id/(.*)', HackerNewsPostHandler)
										],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
