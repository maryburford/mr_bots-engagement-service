import tweepy
import psycopg2
import collections
import random
import time
from time import sleep
import datetime

# connect to mr_bots mr_database
conn = psycopg2.connect("dbname='development' user='mary' host='localhost'")
c = conn.cursor()
print c
# fetch all active users with active mr_campaigns 
c.execute("select a.token, a.secret, a.id, a.uid from campaigns c join accounts a on a.id = c.account_id where a.provider ilike 'twitter' and c.active is True")
results = c.fetchall()

for r in results:
	token, secret, account_id, user_id = r
	# delete all followers in order to refresh
	c.execute('DELETE FROM followers WHERE account_id = %s', [account_id])
	# construct authed api agent AAA
	auth = tweepy.OAuthHandler('tdGB5bGdjqlM3hRVIA3VYY0n9', 'vaAejiob0uko8YPu81tTxB585cvA4G1WmKmwGLGESpMOw5MXxr')
	auth.set_access_token(token, secret)
	api = tweepy.API(auth)
	follower_ids = []
	for page in tweepy.Cursor(api.followers_ids, user_id=user_id).pages():
	    follower_ids.extend(page)
	    time.sleep(3)
	for follower_id in follower_ids:
		print follower_id
		c.execute("INSERT INTO followers (follower_id, account_id, provider, updated_at, created_at) VALUES ('{follower_id}', '{account_id}','{provider}', '{created_at}', '{updated_at}')".format(follower_id=follower_id, account_id=account_id, provider='twitter', created_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'), updated_at=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
		conn.commit()


