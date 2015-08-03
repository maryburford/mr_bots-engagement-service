import tweepy
import psycopg2
import collections
import random
import time
from time import sleep
import datetime
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
conn = psycopg2.connect("dbname='development' user='mary' host='localhost'")
c = conn.cursor()
print c
# fetch all active mr_campaigns (will need to change to get all active campaigns)
c.execute('select c.id, c.target, c.engagements_per_prey, a.token, a.secret, a.id from campaigns c left join accounts a on c.account_id = a.id')

campaigns = c.fetchall()
for r in campaigns:
	print r
print campaigns

# iterate through mr_campaigns and create the mr_engagement_queue
engagements = dict()
for camp in campaigns:
	engagements_for_campaign = collections.deque()
	campaign_id, campaign_target, max_favs, token, secret, account_id = camp
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
			print 'prey id: '+str(prey_id)
			print 'campaign id: '+str(campaign_id)
			token = engage[gag][1]
			secret = engage[gag][2]
			# construct api connection
			auth = tweepy.OAuthHandler('tdGB5bGdjqlM3hRVIA3VYY0n9', 'vaAejiob0uko8YPu81tTxB585cvA4G1WmKmwGLGESpMOw5MXxr')
			auth.set_access_token(token, secret)
			api = tweepy.API(auth)
			# get tweets
			tweets = api.user_timeline(prey_id)
			# print tweets
			# iterate through tweets
			for t in tweets:
				print t.id
				json_object = t._json
				user_name = json_object['user']['screen_name']
				tweet_id = t.id
				tweet_lookup = str(campaign_id) + ' ' + str(tweet_id)
				print tweet_lookup
				# check to see if prey has already been engaged
				if tweet_lookup in engaged_tweets:
					pass
				# engage if prey needs engagement and log 	
				else:
					api.create_favorite(tweet_id)
					engaged_tweets.append(tweet_lookup)
					print 'prey id: '+str(prey_id)
					print 'campaign id: '+str(campaign_id)
					print c
					c.execute("INSERT INTO engagements (campaign_id, prey_id, created_at, updated_at) VALUES ('{campaign_id}', '{prey_id}', '{created_at}', '{updated_at}')".format(campaign_id=campaign_id, prey_id=prey_id, created_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'), updated_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
					conn.commit()
					sleep(90)
		if len(engagement_queue) > 0:
			not_done = True

