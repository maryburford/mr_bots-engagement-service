import tweepy
import sqlite3
import collections
import random

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
		new_engagement[p] = [token, secret, account_id]
		engagements_for_campaign.append(new_engagement)
	engagements[c] = engagements_for_campaign

# shuffle engagement queue so it is randomized
for engagme in engagements:
	engagements_for_campaign = en
	print to_engage
	print
#	auth = tweepy.OAuthHandler('tdGB5bGdjqlM3hRVIA3VYY0n9', 'vaAejiob0uko8YPu81tTxB585cvA4G1WmKmwGLGESpMOw5MXxr')
#	auth.set_access_token(token, secret)
#	tweets = get_tweets(to_engage['account_to_fav'])
#	fav_tweet(to_fav['account_id'], tweets[0])
#	sleep(90 secs)
