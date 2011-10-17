import logging
from google.appengine.ext import db

class NewsCacheModel(db.Model):
	rec_date = db.DateTimeProperty(auto_now_add=True)
	rec_id = db.StringProperty()
	rec_xml = db.TextProperty()
	rec_url = db.StringProperty()
	rec_referrer = db.StringProperty()
	rec_ip = db.StringProperty()
	rec_format = db.StringProperty()
	
