import APIUtils
import DataCache
import logging
import AppConfig


#get cached content
def getCache(pageId, format):
    logging.debug('getCache: %s' % pageId)
    try:
        dbData = DataCache.getData(pageId, format)
        if (dbData):
            if (DataCache.hasExpired(dbData)):
                #data has expired, remove it
                try:
                    dbData[0].delete()
                    return None
                except:
                    logging.error('getCache: unable to remove cache')
                    return None
            else:
                logging.debug('getCache: got cached data for id %s' % id)
                return dbData[0].rec_xml
    except:
        logging.error('getCache: unable to get/retrieve cache')
        return None

#get post by id
def getHackerNewsPost(articleId, format='json', url='', referer='', remote_addr=''):
    #only cache homepage data
    apiURL = "%s/item?id=%s" % (AppConfig.hackerNewsURL, articleId)
    apiURLBackup = "%s/item?id=%s" % (AppConfig.hackerNewsURLBackup, articleId)
    id = '/post/%s' % (articleId)
    cachedData = getCache(id,format)
    if (cachedData):
        return cachedData
    else:
        hnData = APIUtils.parsePostContent(apiURL, apiURLBackup, '/post', None,format)
        if (hnData):
            logging.debug('getHackerNewsPost: storing cached value for id %s' % id)
            DataCache.putData(id, format,APIUtils.removeNonAscii(hnData), url, referer, remote_addr)
            return hnData
        else:
            logging.warning('getHackerNewsPost: unable to retrieve data for id %s' % id)
            return ''

#parse HN's submissions by user
def getHackerNewsSubmittedContent(user, format='json', url='', referer='', remote_addr=''):
    #only cache homepage data
    apiURL = "%s/submitted?id=%s" % (AppConfig.hackerNewsURL, user)
    apiURLBackup = "%s/submitted?id=%s" % (AppConfig.hackerNewsURLBackup, user)
    id = '/submitted/%s' % (user)
    cachedData = None
    cachedData = getCache(id, format)
    if (cachedData):
        return cachedData
    else:
        hnData = APIUtils.parsePageContent(apiURL, apiURLBackup, '/submitted', None, format)
        if (hnData):
            logging.debug('getHackerNewsSubmittedContent: storing cached value for id %s' % id)
            DataCache.putData(id, format, APIUtils.removeNonAscii(hnData), url, referer, remote_addr)
            return hnData
        else:
            logging.warning('getHackerNewsSubmittedContent: unable to retrieve data for id %s' % id)
            return ''


#parse HN's comments by story id
def getHackerNewsComments(articleId, format='json', url='', referer='', remote_addr=''):
    #only cache homepage data
    apiURL = "%s/item?id=%s" % (AppConfig.hackerNewsURL, articleId)
    apiURLBackup = "%s/item?id=%s" % (AppConfig.hackerNewsURLBackup, articleId)
    id = '/comments/%s' % (articleId)
    cachedData = getCache(id, format)
    if (cachedData):
        return cachedData
    else:
        hnData = APIUtils.parseCommentsContent(apiURL, apiURLBackup, '/comments', None, format)
        if (hnData):
            logging.debug('getHackerNewsComments: storing cached value for id %s' % id)
            DataCache.putData(id, format, APIUtils.removeNonAscii(hnData), url, referer, remote_addr)
            return hnData
        else:
            logging.warning('getHackerNewsComments: unable to retrieve data for id %s' % id)
            return ''


#parse HN's comments by story id
def getHackerNewsNestedComments(articleId, format='json', url='', referer='', remote_addr=''):
    #only cache homepage data
    apiURL = "%s/item?id=%s" % (AppConfig.hackerNewsURL, articleId)
    apiURLBackup = "%s/item?id=%s" % (AppConfig.hackerNewsURLBackup, articleId)
    id = '/nestedcomments/%s' % (articleId)
    #cache data
    cachedData = getCache(id, format)
    if (cachedData):
        return cachedData
    else:
        try:
            hnData = APIUtils.parseNestedCommentsContent(apiURL, apiURLBackup, '/nestedcomments', None, format)
            if (hnData):
                logging.debug('getHackerNewsComments: storing cached value for id %s' % id)
                DataCache.putData(id, format, APIUtils.removeNonAscii(hnData), url, referer, remote_addr)
                return hnData
            else:
                logging.warning('getHackerNewsComments: unable to retrieve data for id %s' % id)
                return ''
        except:
            logging.warning('getHackerNewsComments: error(s) getting comments %s' % id)
            return ''


def getHackerNewsSimpleContent(fetcherURL, fetcherBackupURL, id, page='', format='json', url='', referer='', remote_addr=''):
    #don't cache paginated content
    if (page):
        return APIUtils.parsePageContent(fetcherURL, fetcherBackupURL, id, page, format)
    else:
        cachedData = getCache(id, format)
        if (cachedData):
            return cachedData
        else:
            hnData = APIUtils.parsePageContent(fetcherURL, fetcherBackupURL, id, page, format)
            if (hnData):
                logging.debug('getHackerNewsSimpleContent: storing cached value for id %s' % id)
                DataCache.putData(id, format, APIUtils.removeNonAscii(hnData), url, referer, remote_addr)
                return hnData
            else:
                logging.warning('getHackerNewsSimpleContent: unable to retrieve data for id %s' % id)
                return ''


#parse HN's ask content
def getHackerNewsAskContent(page='', format='json', url='', referer='', remote_addr=''):
    return getHackerNewsSimpleContent(AppConfig.hackerNewsAskURL, AppConfig.hackerNewsAskURLBackup, '/ask', page, format, url, referer, remote_addr)


#parse HN's best content
def getHackerNewsBestContent(page='', format='json', url='', referer='', remote_addr=''):
    return getHackerNewsSimpleContent(AppConfig.hackerNewsBestURL, AppConfig.hackerNewsBestURLBackup, '/best', page, format, url, referer, remote_addr)


#parse HN's newest content
def getHackerNewsNewestContent(page='', format='json', url='', referer='', remote_addr=''):
    return getHackerNewsSimpleContent(AppConfig.hackerNewsNewestURL, AppConfig.hackerNewsNewestURLBackup, '/newest', page, format, url, referer, remote_addr)


#get homepage second page stories
def getHackerNewsSecondPageContent(page='', format='json', url='', referer='', remote_addr=''):
    return getHackerNewsSimpleContent(AppConfig.hackerNewsPage2URL, AppConfig.hackerNewsPage2URLBackup, '/news2', page, format, url, referer, remote_addr)


#get homepage first page stories
def getHackerNewsPageContent(page='', format='json', url='', referer='', remote_addr=''):
    return getHackerNewsSimpleContent(AppConfig.hackerNewsURL, AppConfig.hackerNewsURLBackup, '/news', page, format, url, referer, remote_addr)


#get latest homepage stories
def getHackerNewsLatestContent(page='', format='json', url='', referer='', remote_addr='', limit=1):
    #only cache homepage data
    limit = int(limit)
    if (page):
        return APIUtils.parsePageContent(AppConfig.hackerNewsURL, AppConfig.hackerNewsURLBackup, '/latest', page, format, limit)
    else:
        id = '/latest/%s' % limit
        cachedData = getCache(id, format)
        if (cachedData):
            return cachedData
        else:
            hnData = APIUtils.parsePageContent(AppConfig.hackerNewsURL, AppConfig.hackerNewsURLBackup,  '/latest', page, format, limit)
            if (hnData):
                logging.debug('getHackerNewsLatestContent: storing cached value for id %s' % id)
                DataCache.putData(id, format, APIUtils.removeNonAscii(hnData), url, referer, remote_addr)
                return hnData
            else:
                logging.warning('getHackerNewsLatestContent: unable to retrieve data for id %s' % id)
                return ''
