from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class TumbleParser(HTMLParser):
	def __init__(self):
		self.tags = list()
		HTMLParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		self.tags.append( {'tag': tag, 'attrs': attrs} )
	def handle_endtag(self, tag):
		return None
	def handle_data(self, data):
		return None

	def getTags(self):
		return self.tags