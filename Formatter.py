

#output the error
def error(format, msg):
    if (format == 'json'):
        return '{"status":"error","message":"%s"}' % msg
    else:
        return '<?xml version="1.0"?><root><status>error</status><message>%s</message></root>' % msg


def dataWrapper(format, returnData, callback):
    if (format == 'json'):
        returnData = '{"items":[%s]}' % returnData.lstrip('[').rstrip('],')
        if (callback):
            return '%s(%s);' % (callback, returnData)
        else:
            return returnData
    else:
        if (not returnData.startswith('<root>')):
            returnData = '<root>' + returnData
        if (not returnData.endswith('</root>')):
            returnData += '</root>'
        return '<?xml version="1.0"?>%s' % returnData


def contentType(format):
    if (format == 'json'):
        return 'application/json; charset=utf-8'
    else:
        return 'application/xml; charset=utf-8'


#output simple string in json|xml format
def data(format, elm, msg):
    if (format == 'json'):
        return '"%s":"%s",' % (elm, msg)
    else:
        return '<%s>%s</%s>' % (elm, msg, elm)


#output complex types in json|xml format
def dataComplex(format, elm, msg):
    if (format == 'json'):
        return '{"%s":[%s]},' % (elm, msg)
    else:
        return '<%s>%s</%s>' % (elm, msg, elm)
