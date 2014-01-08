import configs
from twython import Twython
import pytumblr
import urllib2
from datetime import date, timedelta
import parser
import sys
from wand.exceptions import MissingDelegateError
from wand.drawing import Drawing
from wand.image import Image, HistogramDict
from wand.color import Color
from wand.font import Font

months = 10

# Authenticate via OAuth
client = pytumblr.TumblrRestClient(
  configs.tumblr_consumer_key,
  configs.tumblr_consumer_secret,
  configs.tumblr_access_key,
  configs.tumblr_access_secret
)

i = 0
found = list()
images = list()

for d in range(0,months):
	daysAgo = (months - d) * 100
	timestamp = date.today() - timedelta(daysAgo)
	timestamp = int(timestamp.strftime("%s"))
	posts = client.tagged("ninja", before=timestamp)
	print timestamp
	for post in posts:
		#if post['type'] == 'photo':
		print '---------------------'
		if 'photos' in post:
			for photo in post['photos']:
				imageurl = photo['original_size']['url']

				if not imageurl in found:
					imageFormat = imageurl.split('.')[-1]
					print 'a',imageFormat,'at',imageurl
					try:
						image = urllib2.urlopen(imageurl).read()
						images.append((image,imageFormat))
						found.append(imageurl)
					except urllib2.HTTPError as e:
						print "Error:",str(e)
					except:
						print "Unexpected error: " + str(sys.exc_info()[0])
					
		elif 'body' in post:
			newParser = parser.TumbleParser()
			newParser.feed(post['body'])
			tags = newParser.getTags()
			for tag in tags:
				if tag['tag'] == "img":
					for tup in tag['attrs']:
						if tup[0] == 'src':
							imageurl = tup[1]

							if not imageurl in found:
								imageFormat = imageurl.split('.')[-1]
								print 'a',imageFormat,'at',imageurl
								try:
									image = urllib2.urlopen(imageurl).read()
									images.append((image,imageFormat))
									found.append(imageurl)
								except urllib2.HTTPError as e:
									print "Error:",str(e)
								except:
									print "Unexpected error: " + str(sys.exc_info()[0])
								

i = 0
for image in images:
	if image[1] != 'gif':
		try:
			im = Image(blob=image[0])
		except MissingDelegateError as e:
			print str(e)
			f = open('images/fail/img_'+str(i)+'.'+image[1], 'wb')
			f.write(image[0])
			f.close()
			i+=1
			continue
		except:
			print "Unexpected error at Wand: " + str(sys.exc_info()[0])
			f = open('images/fail/img_'+str(i)+'.'+image[1], 'wb')
			f.write(image[0])
			f.close()
			i+=1
			continue

		im_clone = im.clone()
		im_clone.resize(1,1)


	fontColor = 'white'
	font = Font('./Gotham-Bold.otf', size=30, color=Color('white'))

	for row in im_clone:
		for col in row:
			assert isinstance(col, Color)
			if (col.red + col.green + col.blue) / 3.0 >= 0.5:
				fontColor = 'black'
				font = Font('./Gotham-Bold.otf', size=30, color=Color('black'))

	if fontColor == 'white':
		font = Font('./Gotham-Bold.otf', size=30, color=Color('black'))
		im.caption("This is a text string", left=7, top=7, width=im.width-10, height=im.height-10, font=font)
		font = Font('./Gotham-Bold.otf', size=30, color=Color('white'))
		im.caption("This is a text string", left=5, top=5, width=im.width-10, height=im.height-10, font=font)
	else:
		font = Font('./Gotham-Bold.otf', size=30, color=Color('white'))
		im.caption("This is a text string", left=7, top=7, width=im.width-10, height=im.height-10, font=font)
		font = Font('./Gotham-Bold.otf', size=30, color=Color('black'))
		im.caption("This is a text string", left=5, top=5, width=im.width-10, height=im.height-10, font=font)

	im.format = 'jpeg'
	im.save(filename='images/image_'+str(i)+'.'+str(image[1]))
	i+=1
