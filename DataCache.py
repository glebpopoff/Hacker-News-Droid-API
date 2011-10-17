import datetime
import time
from google.appengine.ext import db
from models.NewsCache import NewsCacheModel
import AppConfig

#retrieves data by ID
def getData(recordId,format):
	q = NewsCacheModel.all()
	q.filter("rec_id =", recordId)
	q.filter("rec_format =", format)
	q.order("-rec_date")
	results = q.fetch(1)
	return results

#verifies that data hasn't expired
def hasExpired(dataObj):
	if (dataObj):
		dataObjTime = dataObj[0].rec_date
		now = datetime.datetime.now()
		if (dataObjTime + datetime.timedelta(seconds=int(AppConfig.dataExpirationPolicy)) < now):
			return True
		else:
			return False

#stores data	
def putData(recordId, format,data, url, referer, ip):
	d = NewsCacheModel(key_name='%s_%s' % (recordId,format))
	d.rec_id = recordId
	d.rec_xml = data
	d.rec_format = format
	d.rec_url = url
	d.rec_referrer = referer
	d.rec_ip = ip
	d.put()