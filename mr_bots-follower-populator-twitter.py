import tweepy
import psycopg2
import collections
import random
import time
from time import sleep
import datetime
import argparse


# connect to mr_bots mr_database
def get_followers(consumer_key, consumer_secret, pg_user, pg_password, pg_db, pg_host): 
	conn = psycopg2.connect("dbname='" + pg_db + "' user='" + pg_user + "' password='" + pg_password + "' host='" + pg_host + "'")
	c = conn.cursor()
	# fetch all active users with active mr_campaigns
	c.execute("select a.token, a.secret, a.id, a.uid from campaigns c join accounts a on a.id = c.account_id where a.provider ilike 'twitter' and c.active is True")
	results = c.fetchall()
			
	for r in results:
		token, secret, account_id, user_id = r
		# construct authed api agent AAA and see if user is still using MR_BOTS service and/or MR_BOTS app can still auth
		try:
			auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		except Exception as e:
			print "\nError in authing MR_BOTS app\n"
			break
		try:
			auth.set_access_token(token, secret)
			api = tweepy.API(auth)
		except Exception as e:
			print "\Error in Calling Followers for User: "+str(account_id)+"\n"
			continue
		# delete all followers in order to refresh
		c.execute('DELETE FROM followers WHERE account_id = %s', [account_id])
		# get followers, page thru and stuff into array
		follower_ids = []
		for page in tweepy.Cursor(api.followers_ids, user_id=user_id).pages():
			try:
			    follower_ids.extend(page)
			    time.sleep(3)
			except Exception as e:
				print "\Error in Paging Back Followers for User: "+str(account_id)+"\n"
				break
		# iterate through followers and insert into database
		for follower_id in follower_ids:
			c.execute("INSERT INTO followers (follower_id, account_id, provider, updated_at, created_at) VALUES ('{follower_id}', '{account_id}','{provider}', '{created_at}', '{updated_at}')".format(follower_id=follower_id, account_id=account_id, provider='twitter', created_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'), updated_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
			conn.commit()

# probably the most MR part of this entire thing every thing about this right here
def calculate_insert_mr_score(consumer_key, consumer_secret, pg_user, pg_password, pg_db, pg_host):

	query = "with campaign_acquisitions as (select c.account_id, c.id, count(distinct(e.prey_id)) as acquisition_count from campaigns c " \
"join engagements e on c.id = e.campaign_id " \
"join followers f on e.prey_id = f.follower_id and f.account_id = c.account_id " \
"where c.account_id = f.account_id " \
"group by c.account_id, c.id) " \
"select ca.account_id, e.campaign_id, ca.acquisition_count as followers_acquired,count(e.prey_id), (ca.acquisition_count::float / count(e.prey_id)) * 100 as mr_score " \
"from engagements e " \
"join campaign_acquisitions ca " \
"on ca.id = e.campaign_id " \
"group by ca.account_id, e.campaign_id, ca.acquisition_count "
	conn = psycopg2.connect("dbname='" + pg_db + "' user='" + pg_user + "' password='" + pg_password + "' host='" + pg_host + "'")
	c = conn.cursor()
	# fetch all active users with active mr_campaigns
	c.execute(query)
	results = c.fetchall()
	for r in results:
		account_id, campaign_id, followers_acquired, prey_count, mr_score = r
		c.execute("UPDATE campaigns SET (updated_at, mr_score, followers_acquired) = ('{updated_at}', '{mr_score}','{followers_acquired}') WHERE id = '{campaign_id}'".format(updated_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'), mr_score=mr_score, campaign_id=campaign_id, followers_acquired=followers_acquired))
		conn.commit()

def update_engagements(consumer_key, consumer_secret, pg_user, pg_password, pg_db, pg_host):
	query = " select distinct(e.prey_id), c.id " \
 "from campaigns c " \
 "join engagements e on c.id = e.campaign_id  " \
 "join followers f on e.prey_id = f.follower_id and f.account_id = c.account_id  " \
 "join accounts a on c.account_id = a.id " \
 "where c.account_id = f.account_id "
 	conn = psycopg2.connect("dbname='" + pg_db + "' user='" + pg_user + "' password='" + pg_password + "' host='" + pg_host + "'")
	c = conn.cursor()
	c.execute(query)
	results = c.fetchall()
	for r in results:
		prey_id, campaign_id = r
		c.execute("UPDATE engagements e SET (updated_at, isfollowing) = ('{updated_at}', '{isfollowing}') WHERE e.campaign_id = '{campaign_id}' and e.prey_id = '{prey_id}'".format(updated_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'), isfollowing='t', campaign_id=campaign_id, prey_id=prey_id))
		conn.commit()



if __name__  == "__main__":
	parser = argparse.ArgumentParser(description="Twitter follower service.")
	parser.add_argument("--consumer_key")
	parser.add_argument("--consumer_secret")
	parser.add_argument("--pg_user")
	parser.add_argument("--pg_password")
	parser.add_argument("--pg_db")
	parser.add_argument("--pg_host")

	args = parser.parse_args()
	
	if args.consumer_key and args.consumer_secret and args.pg_user and args.pg_password and args.pg_db:
		get_followers(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)
		calculate_insert_mr_score(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)
		update_engagements(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)


	
	else:	
		print "Specify all arguments."
