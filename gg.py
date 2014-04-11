#!/usr/bin/env python
import hashlib
import requests
import gdal
from gdalconst import *
import lxml.etree
import jinja2

hostname='127.0.0.1'
port='8080'
gnuser='admin'
gnpass='admin'
gsuser='admin'
gspass='geoserver'
ws='ncku'
sw=1024.

fileroot = "/srv/geo/web/images"
webroot = 'http://'+hostname+':'+port+'/images'

wmsurl = 'http://'+hostname+':'+port+'/geoserver/ncku/wms'

images = ['*.sid', '*.jpg', '*.jpeg', '*.tif', '*.tiff']
s_srs97tm2 = "+proj=tmerc +ellps=aust_SA +lon_0=121 +k=0.9999 +x_0=250000"
s_srs67tm2 = "+proj=tmerc +ellps=aust_SA +lon_0=121 +k=0.9999 +x_0=250000 +towgs84=-764.558,-361.229,-178.374,-.0000011698,.0000018398,.0000009822,.00002329"
s_srs97 = "+proj=latlong +ellps=aust_SA"
s_srs67 = "+proj=latlong +ellps=aust_SA +towgs84=-764.558,-361.229,-178.374,-.0000011698,.0000018398,.0000009822,.00002329"
t_srs = "+proj=latlong +datum=WGS84"

def getimgbc(file):
    dataset = gdal.Open(file, GA_ReadOnly )
    if dataset is None:
        return -1
    else:
        return dataset.RasterCount

def getimgw(file):
    dataset = gdal.Open(file, GA_ReadOnly )
    if dataset is None:
        return -1
    else:
        return dataset.RasterXSize

def md5sum(file):
    m = hashlib.md5(file)
    fp = open(file)

    for chunk in iter(lambda: fp.read(128), ''):
        m.update(chunk)
    return m.hexdigest()k
    
def wsdel(name):
    headers = {'Accpet': 'text/xml'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/'+name+'?recurse=true'
    r = requests.delete(url, headers=headers, auth=(gsuser, gspass))
    #print r
    #print 'text:'
    #print r.text
    if r.status_code == 200:
        return True
    else:
        return False

def wsadd(name):
    headers = {'Content-type': 'text/xml'}
    data = '<workspace><name>'+name+'</name></workspace>'
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces'
    r = requests.post(url, data=data, headers=headers, auth=(gsuser, gspass))
    #print r
    #print 'text:'
    #print r.text
    if r.status_code == 200:
        return True
    else:
        return False

def clist():
    headers = {'Accpet': 'text/xml'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/'+ws+'/coveragestores'
    r = requests.get(url, headers=headers, auth=(gsuser, gspass))
    #print r
    #print 'text:'
    #print r.text
    return r.content

def cget(name):
    headers = {'Accpet': 'text/xml'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/'+ws+'/coveragestores/'+name
    r = requests.get(url, headers=headers, auth=(gsuser, gspass))
    #print r
    #print 'text:'
    #print r.text
    return r.content

def lget(name):
    headers = {'Accpet': 'text/xml'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/'+ws+'/layers/'+name
    r = requests.get(url, headers=headers, auth=(gsuser, gspass))
    #print r
    #print 'text:'
    #print r.text
    return r.content

def cex(name):
    headers = {'Accpet': 'text/xml'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/'+ws+'/coveragestores/'+name
    r = requests.get(url, headers=headers, auth=(gsuser, gspass))
    #print r.status_code
    #print 'text:'
    #print r.text
    if r.status_code == 200:
        return True
    else:
        return False

def cdel(name):
    headers = {'Accpet': 'text/xml'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/'+ws+'/coveragestores/'+name+'?recurse=true'
    r = requests.delete(url, headers=headers, auth=(gsuser, gspass))
    #print r
    #print 'text:'
    #print r.text
    if r.status_code == 200:
        return True
    else:
        return False
  
def cadd(name, path):
    headers = {'Content-type': 'application/xml'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/ncku/coveragestores'
    data = '<coverageStore><name>'+name+'</name><workspace>'+ws+'</workspace><enabled>true</enabled></coverageStore>'
    r = requests.post(url, data=data, headers=headers, auth=(gsuser, gspass))
    #print r.status_code
    #print r.text

    headers = {'Content-type': 'text/xml'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/ncku/coveragestores/'+name+'/coverages'
    #data = '<coverage><name>'+name+'</name><enabled>true</enabled><srs>EPSG:4326</srs><projectionPolicy>FORCE_DECLARED</projectionPolicy><nativeFormat>GeoTIFF</nativeFormat><requestSRS><string>EPSG:4326</string></requestSRS><responseSRS>
    data = '<coverage><name>'+name+'</name><enabled>true</enabled><srs>EPSG:900913</srs><projectionPolicy>FORCE_DECLARED</projectionPolicy><nativeFormat>GeoTIFF</nativeFormat><requestSRS><string>EPSG:4326</string></requestSRS><responseSRS
    r = requests.post(url, data=data, headers=headers, auth=(gsuser, gspass))
    #print r.status_code
    #print r.text

    headers = {'Content-type': 'text/plain'}
    url = 'http://'+hostname+':'+port+'/geoserver/rest/workspaces/ncku/coveragestores/'+name+'/external.geotiff'
    data = 'file:'+path
    params = {'configure': 'first', 'coverageName': name}
    r = requests.put(url, data=data, headers=headers, params=params, auth=(gsuser, gspass))
    #print r.status_code 
    #print 'text:'
    #print r.text
    if r.status_code == 201:
        return True
    else:
        return False

def madd4string(data):
    headers = {'Content-type': 'application/xml'}
    url = 'http://'+hostname+':'+port+'/geonetwork/srv/en/xml.metadata.insert'
    s = requests.Session()
    r = s.post(url, auth=(gnuser, gnpass), headers=headers, allow_redirects=False)
    uri = 'http://'+hostname+':'+port+r.headers['location']
    #print data
    r = s.post(uri, data=data, headers=headers)
    #print r
    #print 'text:'
    #print r.text
    if r.status_code == 200:
        return True
    else:
        return False

def madd(file):
    headers = {'Content-type': 'application/xml'}
    url = 'http://'+hostname+':'+port+'/geonetwork/srv/en/xml.metadata.insert'
    with open(file, 'rb') as fp:
        data = fp.read()
    s = requests.Session()
    r = s.post(url, auth=(gnuser, gnpass), headers=headers, allow_redirects=False)
    uri = 'http://'+hostname+':'+port+r.headers['location']
    r = s.post(uri, data=data, headers=headers)
    #print r
    #print 'text:'
    #print r.text
    if r.status_code == 200:
        return True
    else:
        return False

def mex(md5):
    headers = {'Content-type': 'application/xml'}
    url = 'http://'+hostname+':'+port+'/geonetwork/srv/en/xml.search'
    s = requests.Session()
    r = s.post(url, auth=(gnuser, gnpass), headers=headers, allow_redirects=False)
    uri = 'http://'+hostname+':'+port+r.headers['location']
    data = '<?xml version="1.0" encoding="UTF-8"?> <request><any>' + md5 + '</any></request>'
    r = s.post(uri, data=data, headers=headers)
    root = lxml.etree.fromstring(r.content)
    t = root.find('summary')
    #print t.attrib['count']
    if t.attrib['count'] != '0':
        return True
    else:
        return False

def msearch(md5):
    headers = {'Content-type': 'application/xml'}
    url = 'http://'+hostname+':'+port+'/geonetwork/srv/en/xml.search'
    s = requests.Session()
    r = s.post(url, auth=(gnuser, gnpass), headers=headers, allow_redirects=False)
    uri = 'http://'+hostname+':'+port+r.headers['location']
    data = '<?xml version="1.0" encoding="UTF-8"?> <request><any>' + md5 + '</any></request>'
    r = s.post(uri, data=data, headers=headers)
    #print r
    #print 'text:'
    #print r.content
    #print r.text
    #print r.encoding
    #r.encoding='ISO-8859-1'
    #print r.encoding
    return r.content

def mdel(id):
    headers = {'Content-type': 'application/xml'}
    url = 'http://'+hostname+':'+port+'/geonetwork/srv/en/xml.metadata.delete'
    s = requests.Session()
    r = s.post(url, auth=(gnuser, gnpass), headers=headers, allow_redirects=False)
    uri = 'http://'+hostname+':'+port+r.headers['location']
    data = '<?xml version="1.0" encoding="UTF-8"?> <request><id>' + id + '</id></request>'
    r = s.post(uri, data=data, headers=headers)
    #print r
    #print 'text:'
    #print r.text
    if r.status_code == 200:
        return True
    else:
        return False

def mtemplate(md):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(['./templates']))
    template = env.get_template('template.xml')
    result = template.render(md)
    return result
