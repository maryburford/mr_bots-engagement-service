import tweepy
import psycopg2
import collections
import random
import time
import json
from time import sleep
import datetime
import argparse
from pprint import pprint

tweet_texts = []
def clean_tweets(new_tweets):
	for i in new_tweets:
		keys = i.keys()
		if 'extended_entities' in keys:
			text = str(i['text'].encode("utf-8")).replace('&amp;','&')
			tweet_text = text.split('http')[0]
			tweet_texts.append(tweet_text)
			oldest = i['id']
		else:
			tweet_text = str(i['text'].encode("utf-8")).replace('&amp;','&')
			tweet_texts.append(tweet_text)
			oldest = i['id']
	return oldest

def build_corpus(consumer_key, consumer_secret, target, access_key, access_secret):
	# this builds a corpus of at least the most recent 100 tweets
	# we will have a sql query here to get campaign inputs from db, testing now just passing params
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

	
	#make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = target,count=200,exclude_replies=True,include_rts=False)
	oldest = clean_tweets(new_tweets)

	while len(tweet_texts) < 101:
		new_tweets = api.user_timeline(screen_name = target ,count=200,max_id=oldest,exclude_replies=True,include_rts=False)
		oldest = clean_tweets(new_tweets)



if __name__  == "__main__":
	parser = argparse.ArgumentParser(description="Twitter engagement service.")
	parser.add_argument("--consumer_key")
	parser.add_argument("--consumer_secret")
	parser.add_argument("--target")
	parser.add_argument("--access_key")
	parser.add_argument("--access_secret")
	#parser.add_argument("--pg_user")
#	parser.add_argument("--pg_password")
#	parser.add_argument("--pg_db")
#	parser.add_argument("--pg_host")

	args = parser.parse_args()
	
	# if args.consumer_key and args.consumer_secret and args.pg_user and args.pg_password and args.pg_db:
	#	engage(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)
	if args.consumer_key and args.consumer_secret:
		print 'fucks'
		build_corpus(args.consumer_key, args.consumer_secret, args.target, args.access_key, args.access_secret)
	else:	
		print "Specify all arguments."
  