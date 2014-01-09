import configs
import pytumblr
import urllib2
import parser
import sys
import random
import logging
import re
import time
import xml.etree.ElementTree as ET
from twython import Twython
from datetime import date, datetime, timedelta
from wand.exceptions import MissingDelegateError
from wand.drawing import Drawing
from wand.image import Image, HistogramDict
from wand.color import Color
from wand.font import Font
from CustomExceptions import BotError

logging.basicConfig(filename='logs.log',level=logging.INFO)

class CareerNinja:
	def __init__(self):
		logging.info(str(datetime.now()) + ': Starting a new CareerNinja Bot')

		#User Defined Vars
		self.job_title = "ninja"
		self.pushInterval = 60 * 60 #One Hour
		self.pushFailureInterval = 60 * 10 #Ten Minutes
		self.refreshInterval = 60 * 60 * 24 #One Day

		#Initilization of vars
		self.currentImageIndex = 0
		self.currentPostingIndex = 0
		self.nextPushTime = 0
		self.nextRefreshTime = 0
		
		#Authenticate with APIs
		try:
			self.tumblrClient = self.run_until_timeout_or_return(3, self.authenticateTumblr)
		except TypeError as e:
			logging.error(str(datetime.now()) + ': Error authenticating with tumblr. Exiting appliction: ' + str(e))
			sys.exit(0)
		except:
			logging.error(str(datetime.now()) + ': Error authenticating with tumblr. Exiting appliction: ' + str(sys.exc_info()[0]))
			sys.exit(0)

		try:
			self.twitter_client = self.run_until_timeout_or_return(3, self.authenticateTwitter)
		except:
			logging.error(str(datetime.now()) + ': Error authenticating with twitter. Exiting appliction: ' + str(sys.exc_info()[0]))
			sys.exit(0)

		logging.info(str(datetime.now()) + ': APIs Authenticated')

		#Create data cache
		try:
			self.refresh_data()
		except BotError as e:
			logging.error(str(datetime.now()) + ': BotError refreshing Data [no data exists, exiting]: ' + str(e))
			sys.exit(0)
		except NameError as e:
			logging.error(str(datetime.now()) + ': NameError refreshing Data [no data exists, exiting]: ' + str(e))
			sys.exit(0)
		except TypeError as e:
			logging.error(str(datetime.now()) + ': TypeError refreshing Data [no data exists, exiting]: ' + str(e))
			sys.exit(0)
		except:
			logging.error(str(datetime.now()) + ': Error refreshing Data [no data exists, exiting]: ' + str(sys.exc_info()[0]))
			sys.exit(0)

		logging.info(str(datetime.now()) + ': Data caches created')

		#Start Main Timed Loop
		self.run_main_loop()

	def run_main_loop(self):
		logging.info(str(datetime.now()) + ': Starting main loop')
		while True:
			#Refresh Data Cache
			if time.time() >= self.nextRefreshTime:
				try:
					self.refresh_data()
				except BotError as e:
					logging.error(str(datetime.now()) + ': Error refreshing Data: ' + str(e))
					self.nextRefreshTime = time.time() + self.refreshInterval
				except:
					logging.error(str(datetime.now()) + ': Error refreshing Data: ' + str(sys.exc_info()[0]))
					self.nextRefreshTime = time.time() + self.refreshInterval

			#Reshuffle Image URL List
			if self.currentImageIndex >= len(self.image_urls):
				self.currentImageIndex = 0
				random.shuffle(image_urls)

			#Reshuffle Job Posting List
			if self.currentPostingIndex >= len(self.job_postings):
				self.currentPostingIndex = 0
				random.shuffle(self.job_postings)

			#Make Post
			if time.time() >= self.nextPushTime:
				logging.info(str(datetime.now()) + ': Selecting Job Posting')
				#Get the job posting
				job_posting = self.job_postings[self.currentPostingIndex]
				self.currentPostingIndex += 1

				logging.info(str(datetime.now()) + ': Selecting Image URL')
				#Get the image URL
				image_url = self.image_urls[self.currentImageIndex]
				self.currentImageIndex += 1

				job_string = "Help Wanted: %s at %s" % (job_posting[1], job_posting[0])
				image_format = image_url.split('.')[-1]

				#Download the image
				logging.info(str(datetime.now()) + ': Downloading image from tumblr')
				try:
					image = urllib2.urlopen(image_url).read()
				except urllib2.HTTPError as e:
					logging.error(str(datetime.now()) + ": Error downloading image:" + str(e))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				except NameError as e:
					logging.error(str(datetime.now()) + ": Name Error downloading image:" + str(e))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				except:
					logging.error(str(datetime.now()) + ": Unexpected error downloading image: " + str(sys.exc_info()[0]))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue

				#Composite the image and text
				try:
					image_to_post = self.make_image_to_post(job_string, image, image_format)
				except MissingDelegateError as e:
					logging.error(str(datetime.now()) + ": Missing Delegate error creating the image: " + str(e))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				except:
					logging.error(str(datetime.now()) + ": Unexpected error creating the image: " + str(sys.exc_info()[0]))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue

				#Post the tweet
				try:
					self.post_tweet(image_to_post)
					self.nextPushTime = time.time() + self.pushInterval
				except NameError as e:
					logging.error("Name Error posting tweet: " + str(e))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				except AttributeError as e:
					logging.error("Attribute Error posting tweet: " + str(e))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				except TypeError as e:
					logging.error("TypeError posting tweet: " + str(e))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				except UnicodeDecodeError as e:
					logging.error("UnicodeDecodeError posting tweet: " + str(e))
					logging.error("UnicodeDecodeError Encoding: " + str(e.encoding))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				except ValueError as e:
					logging.error("ValueError posting tweet: " + str(e))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				except:
					logging.error(str(datetime.now()) + ": Unexpected error posting tweet: " + str(sys.exc_info()[0]))
					self.nextPushTime = time.time() + self.pushFailureInterval
					continue
				
				logging.info(str(datetime.now()) + ': Tweet Posted')

	def authenticateTumblr(self):
		try:
			tumblr_client = pytumblr.TumblrRestClient(
			  configs.tumblr_consumer_key,
			  configs.tumblr_consumer_secret,
			  configs.tumblr_access_key,
			  configs.tumblr_access_secret
			)
			return tumblr_client
		except:
			raise

	def authenticateTwitter(self):
		try:
			twitter = Twython(
				configs.consumer_key,
				configs.consumer_secret,
				configs.access_token_key,
				configs.access_token_secret)

			return twitter
		except AttributeError as e:
			raise
		except TypeError as e:
			raise
		except:
			raise

	def make_image_to_post(self, job_string, image, image_format):
		font_size_to_width_ratio = 0.061
		font_location = './Gotham-Bold.otf'
		fontColors = ['white', 'black']

		logging.info(str(datetime.now()) + ': Begin image compositing.')

		try:
			im = Image(blob=image)
		except MissingDelegateError as e:
			raise
		except:
			raise

		font_size = im.width * font_size_to_width_ratio

		im_clone = im.clone()
		im_clone.resize(1,1)
		
		for row in im_clone:
			for col in row:
				assert isinstance(col, Color)
				if (col.red + col.green + col.blue) / 3.0 >= 0.5:
					fontColors.reverse()

		font = Font(font_location, size=font_size, color=Color(fontColors[1]))
		im.caption(job_string, left=7, top=7, width=im.width-10, height=im.height-10, font=font)
		font = Font(font_location, size=font_size, color=Color(fontColors[0]))
		im.caption(job_string, left=5, top=5, width=im.width-10, height=im.height-10, font=font)

		im.format = image_format
		return im

	def post_tweet(self, image_to_post):
		logging.info(str(datetime.now()) + ': Posting Tweet')
		try:
			image_to_post.save(filename='temp_image.' + str(image_to_post.format))
			imageData = open('temp_image.' + str(image_to_post.format), "rb")
			self.twitter_client.update_status_with_media(status='Yet another feudal hire!', media=imageData)
		except NameError as e:
			raise
		except AttributeError as e:
			raise
		except TypeError as e:
			raise
		except UnicodeDecodeError as e:
			raise
		except ValueError as e:
			raise
		except:
			raise

	def refresh_data(self):
		logging.info(str(datetime.now()) + ': Refreshing Data Cache')
		try:
			self.image_urls = self.refresh_image_urls(search_tags=self.job_title)
		except BotError:
			raise
		
		try:
			self.job_postings = self.refresh_job_postings(job_title=self.job_title)
		except BotError:
			raise
		except:
			raise

		random.shuffle(self.image_urls)
		random.shuffle(self.job_postings)

		self.nextRefreshTime = time.time() + self.refreshInterval
		self.pushInterval = max((23.0 / len(self.job_postings)) * 60 * 60, 60*60)

		logging.info(str(datetime.now()) + ': Data Cache Refreshed. ' + str(len(self.image_urls)) + " image urls. " + str(len(self.job_postings)) + " job postings. Push Interval: " + str(self.pushInterval))


	def refresh_image_urls(self, search_tags="Ninja", periods_back=3):
		logging.info(str(datetime.now()) + ": Refreshing image urls")
		urls = list()
		period_length_days = 100

		for p in range(0,periods_back):
			daysAgo = (periods_back - p) * period_length_days
			timestamp = int( ( date.today() - timedelta( daysAgo ) ).strftime("%s") )
			
			#Call Tumblr
			posts = self.run_until_timeout_or_return(3, self.search_tumblr, search_tags, timestamp)
			
			if posts == None:
				raise BotError('Error getting posts from tumblr')
			
			logging.info(str(datetime.now()) + ": " + str(timestamp))
			
			for post in posts:
				logging.info(str(datetime.now()) + ": ---------------------")
				if 'photos' in post:
					for photo in post['photos']:
						imageurl = photo['original_size']['url']

						if not imageurl in urls:
							imageFormat = imageurl.split('.')[-1]

							if imageFormat != 'gif':
								logging.info(str(datetime.now()) + ': found a ' + str(imageFormat) + ' at ' + str(imageurl))
								urls.append(imageurl)

				elif 'body' in post:
					newHtmlParser = parser.TumbleParser()
					newHtmlParser.feed(post['body'])
					tags = newHtmlParser.getTags()

					for tag in tags:
						if tag['tag'] == "img":
							for tup in tag['attrs']:
								if tup[0] == 'src':
									imageurl = tup[1]
									if not imageurl in urls:
										imageFormat = imageurl.split('.')[-1]
										
										if imageFormat != 'gif':
											logging.info(str(datetime.now()) + ': found a ' + str(imageFormat) + ' at ' + str(imageurl))
											urls.append(imageurl)

		if len(urls) > 0:
			return urls
		else:
			raise BotError("No images found for tag.")

	def refresh_job_postings(self, job_title="Ninja"):
		postings = list()

		logging.info(str(datetime.now()) + ': Refreshing Job Postings')
		cb_url = 'http://api.careerbuilder.com/v1/jobsearch?DeveloperKey=' + configs.career_builder_key + "&JobTitle=" + job_title
		logging.info(str(datetime.now()) + ": searching careerbuilder: " + cb_url)
		try:
			response = urllib2.urlopen(cb_url)
			root = ET.fromstring(response.read())
		except:
			logging.error(str(datetime.now()) + ": Unexpected error in careerbuilder search: " + str(sys.exc_info()[0]))
			raise

		for res in root.iter("JobSearchResult"):
			if res.find('Company') != None and res.find('Company').text != None and res.find('JobTitle') != None:
				company = res.find('Company').text
				title = res.find('JobTitle').text
				reg_title = re.search('([a-zA-Z][a-zA-Z -]+)?(' + job_title + ')([a-zA-Z -]+[a-zA-Z])?', title, re.I)
				if reg_title != None and reg_title.group(0) != None:
					title = reg_title.group(0)
					postings.append((str(company), str(title)))

		if len(postings) > 0:
			return postings
		else:
			raise BotError('No valid postings found.')

	def search_tumblr(self, tags, before):
		logging.info(str(datetime.now()) + ': Searching tumblr for ' + str(tags))
		try:
			return self.tumblrClient.tagged("ninja", before=before)
		except:
			raise


	def run_until_timeout_or_return(self, timeout, func, *args):
		i = 0
		while i < timeout:
			try:
				return func (*args)
			except AttributeError as e:
				logging.error(str(datetime.now()) + ": Unexpected AttributeError error in " + str(func) + ": " + str(e))
				i+=1
			except TypeError as e:
				logging.error(str(datetime.now()) + ": Unexpected TypeError error in " + str(func) + ": " + str(e))
				i+=1
			except NameError as e:
				logging.error(str(datetime.now()) + ": Unexpected NameError error in " + str(func) + ": " + str(e))
				i+=1
			except:
				logging.error(str(datetime.now()) + ": Unexpected error in " + str(func) + ": " + str(sys.exc_info()[0]))
				i+=1

		raise BotError("Timed out running " + str(func))

if __name__ == "__main__":
	bot = CareerNinja()
	
