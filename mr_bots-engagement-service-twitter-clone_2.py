import tweepy
import psycopg2
import collections
import random
import time
import json
import markov
from time import sleep
import datetime
import argparse
from pprint import pprint
import re

tweet_texts = []
tempMapping = {}
articles = ['a','an','the','da']
# (tuple of words) -> {dict: word -> *normalized* number of times the word appears following the tuple}
# Example entry:
#    ('eyes', 'turned') => {'to': 0.66666666, 'from': 0.33333333}
mapping = {}

# Contains the set of words that can start sentences
starts = []

def tweeting_clone(consumer_key, consumer_secret, pg_user, pg_password, pg_db, pg_host):

    conn = psycopg2.connect("dbname='" + pg_db + "' user='" + pg_user + "' password='" + pg_password + "' host='" + pg_host + "'")
    c = conn.cursor()
    c.execute("select a.id, c.id, a.token, a.secret, c.target from campaigns c left join accounts a on c.account_id = a.id where c.active = True and c.engagement_type = 'Clone'")
    campaigns = c.fetchall()
    for camp in campaigns:
        tweeted = False
        while tweeted is False:
            del tweet_texts[:]
            del starts[:]
            tempMapping.clear()
            mapping.clear()
            account_id, campaign_id, token, secret, target = camp
            try:
                auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            except Exception as e:
                print "\nError in authing MR_BOTS app\n"
                break
            # check user still auths MR_BOTS
            try:
                auth.set_access_token(token, secret)
                api = tweepy.API(auth)
            except Exception as e:
                print "\Error in authing MR_BOTS user: "+str(account_id)+"\n"
                break
            try:
                tweet = generateTweets(consumer_key, consumer_secret, target, token, secret)
                api.update_status(status=tweet)
                tweeted = True
                print "\AccountID: "+str(account_id)+" Tweeted  "+str(tweet)+"\n"
                time.sleep(180)
            except Exception as e:
                pass


def clean_tweets(new_tweets):
    for i in new_tweets:
        keys = i.keys()
        if 'extended_entities' in keys:
            text = str(i['text'].encode("utf-8")).replace('&amp;','&')
            tweet_text = text.split('http')[0]
            tweet_texts.append(re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*|\@\w+', '',tweet_text))
            oldest = i['id']
        else:
            tweet_text = str(i['text'].encode("utf-8")).replace('&amp;','&')
            tweet_texts.append(re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*|\@\w+', '',tweet_text))
            oldest = i['id']
    return oldest


def build_corpus(consumer_key, consumer_secret, target, access_key, access_secret):
    # this builds a corpus of at least the most recent 100 tweets
    # we will have a sql query here to get campaign inputs from db, testing now just passing params
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    targets = target.split(',')
    pages = 1
    rate_limit = api.rate_limit_status()
   # print rate_limit['resources']['statuses']['/statuses/user_timeline']
    if len(targets) == 1:
        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = target,count=200,exclude_replies=False,include_rts=False)
        oldest = clean_tweets(new_tweets)
        if len(new_tweets) > 1:
            while pages < 5:
            #    print pages
                new_tweets = api.user_timeline(screen_name = target ,count=200,max_id=oldest,exclude_replies=False,include_rts=False)
                oldest = clean_tweets(new_tweets)
                pages = pages + 1
                rate_limit = api.rate_limit_status()
                #print rate_limit['resources']['statuses']['/statuses/user_timeline']
            return oldest
    else:
        for target in targets:
            new_tweets = api.user_timeline(screen_name = target,count=200,exclude_replies=False,include_rts=False)
            oldest = clean_tweets(new_tweets)

            while len(new_tweets) > 1 or pages < 5:
                new_tweets = api.user_timeline(screen_name = target ,count=200,max_id=oldest,exclude_replies=False,include_rts=False)
                oldest = clean_tweets(new_tweets)
                pages = pages + 1
            return oldest


def check_tweet(tweet,tweet_texts):
    tweet_texts = frozenset(tweet_texts)
    clean_tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*|\@\w+', '',tweet)
    if clean_tweet in tweet_texts:
        already_tweeted = True
    else:
        already_tweeted = False
    return already_tweeted

def generateTweets(consumer_key, consumer_secret, target, access_key, access_secret):
    order = 2
    build_corpus(consumer_key, consumer_secret, target, access_key, access_secret)
    mine = markov.MarkovChainer(order)
    for tweet in tweet_texts:
        if re.search('([\.\!\?\"\']$)', tweet):
            pass
        else:
            tweet+="."
        mine.add_text(tweet)

    for x in range(0,10):
        tweet = mine.generate_sentence()

    if random.randint(0,4) == 0 and re.search(r'(in|to|from|for|with|by|our|of|your|around|under|beyond)\s\w+$', tweet) != None:
       tweet = re.sub(r'\s\w+.$','',tweet)


    #if a tweet is very short, this will randomly add a second sentence to it.
    if tweet != None and len(tweet) < 40:
        rando = random.randint(0,10)
        if rando == 0 or rando == 7:
            newer_tweet = mine.generate_sentence()
            if newer_tweet != None:
                tweet += " " + mine.generate_sentence()
            else:
                tweet = tweet
        elif rando == 1:
            tweet = tweet.upper()

    # checks to see if tweet is not in original corpus
    already_tweeted = check_tweet(tweet,tweet_texts)
    if already_tweeted is True:
        generateTweets(consumer_key, consumer_secret, target, access_key, access_secret)
    else:
        return tweet
if __name__  == "__main__":
    parser = argparse.ArgumentParser(description="Twitter clone service.")
    parser.add_argument("--consumer_key")
    parser.add_argument("--consumer_secret")
    parser.add_argument("--pg_user")
    parser.add_argument("--pg_password")
    parser.add_argument("--pg_db")
    parser.add_argument("--pg_host")

    args = parser.parse_args()

    # if args.consumer_key and args.consumer_secret and args.pg_user and args.pg_password and args.pg_db:
    #   engage(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)
    if args.consumer_key and args.consumer_secret:
        tweeting_clone(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)

    else:
        print "Specify all arguments."
