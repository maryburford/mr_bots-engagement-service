import tweepy
import sqlite3
import collections
import random
from time import sleep

# from the campaign target's results, pick random prey
def random_prey(prey, max_favs):
	prey = prey
	selected_prey = []
	while len(selected_prey) < max_favs + 1:
		p = random.choice(prey)
		if p not in selected_prey:
			selected_prey.append(p)
	return selected_prey



# connect to mr_bots mr_database
conn = sqlite3.connect('/Users/mary/mr_bots-webapp/db/development.sqlite3') 
c = conn.cursor()
# fetch all active mr_campaigns
c.execute('select c.id, c.target, c.max_favs, a.token, a.secret, a.id from campaigns c join accounts a on c.account_id = a.id where c.active = "t" and a.id = "1"')
campaigns = c.fetchall()

# iterate through mr_campaigns and create the mr_engagement_queue
engagements = dict()
for c in campaigns:
	engagements_for_campaign = collections.deque()
	campaign_id, campaign_target, max_favs, token, secret, account_id = c
	auth = tweepy.OAuthHandler('tdGB5bGdjqlM3hRVIA3VYY0n9', 'vaAejiob0uko8YPu81tTxB585cvA4G1WmKmwGLGESpMOw5MXxr')
	auth.set_access_token(token, secret)
	api = tweepy.API(auth)
	prey = api.followers_ids(campaign_target)
	r_prey = random_prey(prey, max_favs)
	for p in r_prey:
		new_engagement = dict()
		new_engagement[p] = [campaign_id, token, secret, account_id]
		engagements_for_campaign.append(new_engagement)
	engagements[campaign_id] = engagements_for_campaign

# iterate through the the actions queued for each campaign, 
# until all actions for all campaigns have been completed
engaged_tweets = []
not_done = True
while not_done:
	not_done = False
	for engagement_queue in engagements.values():
		if len(engagement_queue) == 0:
			break
		# perform this engagement and remove from queue
		engage = engagement_queue[-1]
		engagement_queue.popleft()
		for gag in engage:
			prey_id = gag
			campaign_id = engage[gag][0]
			token = engage[gag][1]
			secret = engage[gag][2]
			# construct api connection
			auth = tweepy.OAuthHandler('tdGB5bGdjqlM3hRVIA3VYY0n9', 'vaAejiob0uko8YPu81tTxB585cvA4G1WmKmwGLGESpMOw5MXxr')
			auth.set_access_token(token, secret)
			api = tweepy.API(auth)
			# get tweets
			tweets = api.user_timeline(prey_id)
			# iterate through tweets
			for t in tweets:
				print t.id
				json_object = t._json
				user_name = json_object['user']['screen_name']
				tweet_id = t.id
				tweet_lookup = str(campaign_id) + ' ' + str(tweet_id)
				# check to see if prey has already been engaged
				if tweet_lookup in engaged_tweets:
					pass
				# engage if prey needs engagement	
				else:
					api.create_favorite(tweet_id)
					faved_tweets.append(tweet_lookup)
			sleep(90)
		if len(engagement_queue) > 0:
			not_done = True

