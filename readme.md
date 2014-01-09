#CareerNinja
##A Twitter Bot by Daniel Plemmons

Career Ninja searches career builder for job listings looking for ninjas. It then finds similar images on Tumblr and uses ImageMagick (via Wand) to combine the listing and the image before posting it to twitter.

**Additional Requirements:**
- twython (3.1.2)
- Wand (0.3.5)
- ImageMagick and Delegate Libraries
- A twitter account with an active application attached.
- A CareerBuilder.com developer account.
- A Tumblr developer account
- a config.py with your login credentials for all the APIs

The config.py looks like this:
<pre><code>
	consumer_key='consumer key from twitter' 
	consumer_secret='consumer secret from twitter' 
	access_token_key='access key from twitter'
	access_token_secret='access secret from twitter'
	career_builder_key='access key from career builder'
	tumblr_consumer_key='consumer key from tumblr'
	tumblr_consumer_secret='consumer secret from tumblr'
	tumblr_access_key='access key from tumblr'
	tumblr_access_secret='access secret from tumblr'
</code></pre>

**Running:**
I personally run the bot on a ubuntu virtual box. To start the bot in the background and not let the process get killed upon ending the ssh session I use:

    nohup python careerNinja.py > /dev/null < /dev/null &!