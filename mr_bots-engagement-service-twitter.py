import tweepy
import psycopg2
import collections
import random
import time
from time import sleep
import datetime
import urllib3
import os
import argparse
import math


# from the campaign target's results, pick random prey
def random_prey(prey, n):
	prey = prey
	if len(prey) <= n:
		return prey
	selected_prey = []
	while len(selected_prey) < n:
		p = random.choice(prey)
		if p not in selected_prey:
			selected_prey.append(p)
	return selected_prey



# connect to mr_bots mr_database
def engage(consumer_key, consumer_secret, pg_user, pg_password, pg_db, pg_host): 
	conn = psycopg2.connect("dbname='" + pg_db + "' user='" + pg_user + "' password='" + pg_password + "' host='" + pg_host + "'")
	c = conn.cursor()
	# fetch all active mr_campaigns (will need to change to get all active campaigns)
	c.execute('select c.id, c.target, c.engagements_per_prey, c.engagements_per_day, a.token, a.secret, a.id from campaigns c left join accounts a on c.account_id = a.id where c.active = True')
	print "\nActive Campaigns:\n"

	campaigns = c.fetchall()
	for r in campaigns:
		print r

	# iterate through mr_campaigns and create the mr_engagement_queue
	engagements = dict()
	for camp in campaigns:
		print camp
		engagements_for_campaign = collections.deque()
		campaign_id, campaign_target, engagements_per_prey, engagements_per_day, token, secret, account_id = camp
		auth = tweepy.OAuthHandler('tdGB5bGdjqlM3hRVIA3VYY0n9', 'vaAejiob0uko8YPu81tTxB585cvA4G1WmKmwGLGESpMOw5MXxr')
		auth.set_access_token(token, secret)
		api = tweepy.API(auth)
		prey = api.followers_ids(campaign_target)
		r_prey = random_prey(prey, math.floor(engagements_per_day/engagements_per_prey))
		for p in r_prey:
			for _ in xrange(engagements_per_prey):
				new_engagement = dict()
				new_engagement['prey_id'] = p
				new_engagement['campaign_id'] = campaign_id
				new_engagement['token'] = token
				new_engagement['secret'] = secret
				new_engagement['account_id'] = account_id
				engagements_for_campaign.append(new_engagement)
		print len(engagements_for_campaign)
		engagements[campaign_id] = engagements_for_campaign

	print "\nEngagements Planned:\n"
	print engagements
	

	print "\nEngaging...:\n"
	

	# iterate through the the actions queued for each campaign, 
	# until all actions for all campaigns have been completed
	engaged_tweets = []
	not_done = True
	rnd = 0
	while not_done:
		print "ROUND: " + str(rnd)
		not_done = False
		for engagement_queue in engagements.values():
			if len(engagement_queue) == 0:
				break
			# perform this engagement and remove from queue
			engagement = engagement_queue.popleft()
			# construct api connection
			auth = tweepy.OAuthHandler('tdGB5bGdjqlM3hRVIA3VYY0n9', 'vaAejiob0uko8YPu81tTxB585cvA4G1WmKmwGLGESpMOw5MXxr')
			auth.set_access_token(engagement["token"], engagement["secret"])
			api = tweepy.API(auth)
			# get tweets
			tweets = api.user_timeline(engagement["prey_id"])
			# print tweets
			# iterate through tweets
			for t in tweets:
				json_object = t._json
				user_name = json_object['user']['screen_name']
				tweet_id = t.id
				tweet_lookup = str(engagement["campaign_id"]) + ' ' + str(tweet_id)
				# check to see if prey has already been engaged
				if tweet_lookup in engaged_tweets:
					pass
				# engage if prey needs engagement and log 	
				else:
					try:
						api.create_favorite(tweet_id)
					except Exception as e:
						print "Error faving: " + e
					print 'Engagement: Campaign ' + str(engagement['campaign_id']) + ' > Fav Prey > ' + str(engagement['prey_id'])
					engaged_tweets.append(tweet_lookup)
					c.execute("INSERT INTO engagements (campaign_id, prey_id, created_at, updated_at) VALUES ('{campaign_id}', '{prey_id}', '{created_at}', '{updated_at}')".format(campaign_id=engagement["campaign_id"], prey_id=engagement["prey_id"], created_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'), updated_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
					conn.commit()
					# found suitable tweet, stop checking tweets
					break
			if len(engagement_queue) > 0:
				not_done = True
		rnd = rnd + 1
		sleep(90)


if __name__  == "__main__":
	parser = argparse.ArgumentParser(description="Twitter engagement service.")
	parser.add_argument("--consumer_key")
	parser.add_argument("--consumer_secret")
	parser.add_argument("--pg_user")
	parser.add_argument("--pg_password")
	parser.add_argument("--pg_db")
	parser.add_argument("--pg_host")

	args = parser.parse_args()
	
	if args.consumer_key and args.consumer_secret and args.pg_user and args.pg_password and args.pg_db:
		engage(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)
	else:	
		print "Specify all arguments."
  

