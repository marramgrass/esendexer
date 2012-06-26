import urllib, urllib2
import re
import xml.dom.minidom
import base64

class Esendex(object):
	"""
		Interface to the eSendex SMS sending API
	"""
	
	messagedispatcher_url = "https://api.esendex.com/v1.0/messagedispatcher"
	
	def __init__(self, u=None, p=None, ac=None):
		self.recipients = []
		self.from_label = "eSendex"
		self.username = u
		self.password = p
		self.accountref = ac
		self.content = None
	
	def from_string(self, f=None):
		"""
			Set the from identifier for the SMS.
			
			Limited to 11 characters (will be truncated), or a phone number.
		"""
		if f:
			if not re.match('^[0-9]+$', f):
				self.from_label = f[0:11] # non-numeric 'from' data must be 11 characters or less
			else:
				self.from_label = f
		return self
	
	def to(self, receipts=None):
		"""
			One, or a list of, phone numbers.
		"""
		if not isinstance(receipts, list) and not isinstance(receipts, basestring):
			raise NoRecipientsError()
		
		if isinstance(receipts, basestring):
			self.recipients = [receipts]
		else:
			self.recipients = receipts
		return self
	
	def message(self, m=None):
		"""
			Content for the SMS.
		"""
		if m:
			self.content = str(m)[0:160]
		return self
	
	def send(self):
		"""
			Send it!
		"""
		if not self.content:
			raise NoContentError()
		
		document = self.build_dom()
		xml = document.toxml("utf-8")
		
		req = urllib2.Request(self.messagedispatcher_url)
		req.add_header("Authorization", "Basic " + base64.standard_b64encode("%s:%s" % (self.username, self.password)))
		req.add_data(xml)
		
		try:
			resp = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			raise EsendexAPIRequestError(e.read())
		except urllib2.URLError, e:
			raise EsendexAPIRequestError(e.reason)
	
	def build_dom(self):
		document = xml.dom.minidom.Document()
		messages_el = document.createElement("messages")
		document.appendChild(messages_el)
		
		account_el = document.createElement("accountreference")
		account_txt = document.createTextNode(self.accountref)
		account_el.appendChild(account_txt)
		messages_el.appendChild(account_el)
		
		from_label_el = document.createElement("from")
		from_label_txt = document.createTextNode(self.from_label)
		from_label_el.appendChild(from_label_txt)
		messages_el.appendChild(from_label_el)
		
		message_el = document.createElement("message")
		to_el = document.createElement("to")
		to_txt = document.createTextNode(','.join(self.recipients))
		to_el.appendChild(to_txt)
		message_el.appendChild(to_el)
		
		type_el = document.createElement("type")
		type_txt = document.createTextNode("SMS")
		type_el.appendChild(type_txt)
		message_el.appendChild(type_el)
		
		body_el = document.createElement("body")
		body_txt = document.createTextNode(self.content)
		body_el.appendChild(body_txt)
		message_el.appendChild(body_el)
		
		messages_el.appendChild(message_el)
		
		return document


class NoContentError(Exception):
	pass

class NoRecipientsError(Exception):
	pass

class EsendexAPIRequestError(Exception):
	pass

