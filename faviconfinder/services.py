import requests
from requests.adapters import HTTPAdapter
from .models import Favicon
import re
from bs4 import BeautifulSoup
from django.db import transaction
import urllib3
import pdb

def validateFaviconUrl(fav_url):
	# if no valid fav_url, set a placeholder value to show we tried
	if fav_url == None:
		fav_url = Favicon.invalid_url()
	return(fav_url)

def findFaviconUrl(url_param):
	#pdb.set_trace()
	# try the hardcoded url
	fav_url = requestFaviconUrl(url_param+'/favicon.ico')
	if fav_url != None:
		return(fav_url)
	
	# if all else fails ... try the "icon" link
	fav_url = requestIconLinkUrl(url_param)
	return(fav_url)

def makeRequest(url):
	#pdb.set_trace()
	# make the request and return the response
	print("Trying:"+url)
	try:
		sess = requests.Session()
		sess.mount('http://', HTTPAdapter(max_retries=3))
		response = sess.get(url, timeout=0.3)
		response.raise_for_status()
	except requests.exceptions.RequestException as e:
		print("Exception:"+str(e))
		return(None)
	except urllib3.exceptions.Exception as url_e:
		print("Exception:"+str(url_e))
		return(None)
	return response
	
def requestIconLinkUrl(url_param):
	#pdb.set_trace()
	# look for favicon via the url referenced in the icon link
	# of the destination page
	# this takes 2 requests (one to find url, one to check if it works)
	response = makeRequest(url_param)
	if not response:
		return(None)
		
	#check the status of the response
	if response.status_code != requests.codes.ok:
		return(None)
	
	#quick search of html for "icon" link before we waste time parsing more html
	response_text = response.text
	# first look for "icon" tags
	fav_url = parseForFavicon(response_text, "icon", response.url)
	if fav_url == None:
		# finally look for "shortcut icon" tags
		fav_url = parseForFavicon(response_text, "shortcut icon", response.url)
	
	# test the url
	return(requestFaviconUrl(fav_url))
	
def parseForFavicon(response_text, tag, response_url):
	#pdb.set_trace()
	fav_url = None
	if not re.search(tag, response_text, re.IGNORECASE):
		# no hope here, give update
		return None
	# resort to soup
	soup = BeautifulSoup(response_text, 'html.parser')
	
	link = soup.find(rel=tag)
	if link:
		href = link.get('href')
		if href:
			# if it contains http, it's a full url, otherwise we must concatenate
			if href.startswith("http"):
				fav_url = href
			else:
				fav_url = response_url+href
	
	return fav_url
	
def requestFaviconUrl(url_param):
	#pdb.set_trace()
	# look for favicon via shortcut url
	# this takes one request
	if url_param == None:
		return None
	response = makeRequest(url_param)
	if not response:
		return(None)
		
	#check the status of the response
	if response.status_code != requests.codes.ok:
		return(None)
	
	# check the type of the response ... if not an image ..
	# something bad happened
	if not response.headers.get('Content-Type'):
		print("no Content-Type")
	
	elif "image" not in response.headers.get('content-type'):
		return(None)
		
	# use the response url in case of redirects
	fav_url = response.url
	return(fav_url)
	
# return the favicon URL of a source url
# will handle redirects
def getFaviconUrl(url_param):
	#pdb.set_trace()
	fav_url = None
	querySet = Favicon.objects.filter(url=url_param)
	# there should only be one instance
	if len(querySet) > 0:
		instance = querySet[0]
		# if the stored value is not invalid, just use that.
		# otherwise, try to find it.
		if instance.fav_url and instance.fav_url != Favicon.invalid_url():
			fav_url = instance.fav_url
		else:
			fav_url = findFaviconUrl(url_param)
			fav_url = instance.fav_url = validateFaviconUrl(fav_url)
			instance.save()
	else:
		instance = Favicon()
		instance.url = url_param
		fav_url = findFaviconUrl(url_param)
		fav_url = instance.fav_url = validateFaviconUrl(fav_url)
		instance.save()
		
	return(fav_url)
	
