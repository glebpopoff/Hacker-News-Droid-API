import os
import re
import logging
import time
from UserString import MutableString
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
import AppConfig
from UserString import MutableString
from xml.sax.saxutils import escape
import random

def trackGARequests(path,remoteAddr, referer = ''):
	logging.debug('trackRSSRequests: calling GA GIF service')
	
	var_utmac = AppConfig.googleAnalyticsKey #enter the new urchin code
	var_utmhn = 'hndroidapi.appspot.com' #enter your domain
	var_utmn = str(random.randint(1000000000, 9999999999))#random request number
	var_cookie = str(random.randint(10000000, 99999999))#random cookie number
	var_random = str(random.randint(1000000000, 2147483647)) #number under 2147483647
	var_today = str(int(time.time())) #today
	var_referer = referer #referer url
	var_uservar = '-' #enter your own user defined variable
	var_utmp = '%s/%s' % (path, remoteAddr) #this example adds a fake page request to the (fake) rss directory (the viewer IP to check for absolute unique RSS readers)
	#build URL
	urchinUrl = MutableString()
	urchinUrl = 'http://www.google-analytics.com/__utm.gif?utmwv=1&utmn=' +  var_utmn + '&utmsr=-&utmsc=-&utmul=-&utmje=0&utmfl=-&utmdt=-&utmhn=' + var_utmhn + '&utmr=' + var_referer + '&utmp=' + var_utmp + '&utmac=' + var_utmac + '&utmcc=__utma%3D' + var_cookie + '.' + var_random + '.' + var_today + '.' + var_today + '.' + var_today + '.2%3B%2B__utmb%3D' + var_cookie + '%3B%2B__utmc%3D' + var_cookie + '%3B%2B__utmz%3D' + var_cookie + '.' + var_today + '.2.2.utmccn%3D(direct)%7Cutmcsr%3D(direct)%7Cutmcmd%3D(none)%3B%2B__utmv%3D' + var_cookie + '.' + var_uservar + '%3B';
	
	#async request to GA's GIF service
	rpcGA = None
	try:
		rpcGA = urlfetch.create_rpc()
		urlfetch.make_fetch_call(rpcGA, urchinUrl)
	except Exception,exT:
		logging.error('trackRSSRequests: Errors calling GA GIF service : %s' % exT)
	
	#validate request
	if (rpcGA):
		try:
	 		result = rpcGA.get_result()
			if (result and result.status_code == 200):
				logging.debug('trackRSSRequests: GA logged successfully')
		except Exception,ex:
			logging.error('trackRSSRequests: Errors : %s' % ex)