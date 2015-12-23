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
        account_id, campaign_id, token, secret, target = camp
        print camp
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        except Exception as e:
            print "\nError in authing MR_BOTS app\n"
        #break
        # check user still auths MR_BOTS
        try:
            auth.set_access_token(token, secret)
            api = tweepy.API(auth)
        except Exception as e:
            print "\Error in authing MR_BOTS user: "+str(account_id)+"\n"
        try:
            tweet = generateTweets(consumer_key, consumer_secret, target, token, secret)
            print tweet
            api.update_status(status=tweet)
        except Exception as e:
            print str(e)


# We want to be able to compare words independent of their capitalization.
def fixCaps(word):
    # Ex: "FOO" -> "foo"
    if word.isupper() and word != "I":
        word = word.lower()
        # Ex: "LaTeX" => "Latex"
    elif word [0].isupper():
        word = word.lower().capitalize()
        # Ex: "wOOt" -> "woot"
    else:
        word = word.lower()
    return word

def toHashKey(lst):
	    return tuple(lst)

	# Returns the contents of the file, split into a list of words and
	# (some) punctuation.
def wordlist(tweet_texts):

    wordlist = [fixCaps(w) for w in re.findall(r"[\w']+|[.,!?;]", tweet_texts)]
    return wordlist

# Self-explanatory -- adds "word" to the "tempMapping" dict under "history".
# tempMapping (and mapping) both match each word to a list of possible next
# words.
# Given history = ["the", "rain", "in"] and word = "Spain", we add "Spain" to
# the entries for ["the", "rain", "in"], ["rain", "in"], and ["in"].
def addItemToTempMapping(history, word):
    global tempMapping
    while len(history) > 0:
        first = toHashKey(history)
        if first in tempMapping:
            if word in tempMapping[first]:
                tempMapping[first][word] += 1.0
            else:
                tempMapping[first][word] = 1.0
        else:
            tempMapping[first] = {}
            tempMapping[first][word] = 1.0
        history = history[1:]

# Building and normalizing the mapping.
def buildMapping(wordlist, markovLength):
    global tempMapping
    starts.append(wordlist [0])
    for i in range(1, len(wordlist) - 1):
        if i <= markovLength:
            history = wordlist[: i + 1]
        else:
            history = wordlist[i - markovLength + 1 : i + 1]
        follow = wordlist[i + 1]
        # if the last elt was a period, add the next word to the start list
        if history[-1] == "." and follow not in ".,!?;":
            starts.append(follow)
        addItemToTempMapping(history, follow)
    # Normalize the values in tempMapping, put them into mapping
    for first, followset in tempMapping.iteritems():
        total = sum(followset.values())
        # Normalizing here:
        mapping[first] = dict([(k, v / total) for k, v in followset.iteritems()])

# Returns the next word in the sentence (chosen randomly),
# given the previous ones.
def next(prevList):
    sum = 0.0
    retval = ""
    index = random.random()
    # Shorten prevList until it's in mapping
    while toHashKey(prevList) not in mapping:
    	try:
        	prevList.pop(0)
        except:
        	pass
    # Get a random word from the mapping, given prevList
    for k, v in mapping[toHashKey(prevList)].iteritems():
        sum += v
        if sum >= index and retval == "":
            retval = k
    return retval

def genSentence(markovLength):
    # Start with a random "starting word"
    curr = random.choice(starts)
    sent = curr.capitalize()
    prevList = [curr]
    # Keep adding words until we hit a period or we're at 140 characters
    while (curr not in ".") and (sum([len(i) for i in sent]) <= 140):
        curr = next(prevList)
        prevList.append(curr)
        # if the prevList has gotten too long, trim it
        if len(prevList) > markovLength:
            prevList.pop(0)
        candidate = sent + curr
        if (sum([len(i) for i in candidate]) < 140):
            if (curr not in ".,!?;"):
                sent += " " # Add spaces between words (but not punctuation)
            sent += curr
        else:
            sent = sent
    return sent


def clean_tweets(new_tweets):
    for i in new_tweets:
        keys = i.keys()
        if 'extended_entities' in keys:
            text = str(i['text'].encode("utf-8")).replace('&amp;','&')
            tweet_text = text.split('http')[0]
            tweet_texts.append(re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '',tweet_text))
            oldest = i['id']
        else:
            tweet_text = str(i['text'].encode("utf-8")).replace('&amp;','&')
            tweet_texts.append(re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '',tweet_text))
            oldest = i['id']
    return oldest




def build_corpus(consumer_key, consumer_secret, target, access_key, access_secret):
    # this builds a corpus of at least the most recent 100 tweets
    # we will have a sql query here to get campaign inputs from db, testing now just passing params
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    targets = target.split(',')
    if len(targets) == 0:


    	#make initial request for most recent tweets (200 is the maximum allowed count)
    	new_tweets = api.user_timeline(screen_name = target,count=200,exclude_replies=True,include_rts=False)
    	oldest = clean_tweets(new_tweets)

    	while len(tweet_texts) < 101:
    		new_tweets = api.user_timeline(screen_name = target ,count=200,max_id=oldest,exclude_replies=True,include_rts=False)
    		oldest = clean_tweets(new_tweets)
    else:
        for target in targets:
            new_tweets = api.user_timeline(screen_name = target,count=200,exclude_replies=True,include_rts=False)
            oldest = clean_tweets(new_tweets)


def generateTweets(consumer_key, consumer_secret, target, access_key, access_secret):
    markovLength = 2
    build_corpus(consumer_key, consumer_secret, target, access_key, access_secret)
    words = " ".join(str(x) for x in tweet_texts)
    buildMapping(wordlist(words), markovLength)
    tweet = genSentence(markovLength)
    sent_tokes = tweet.split()
    last_word = sent_tokes[-1]
    last_word = last_word.replace('.','').replace(',','')
    if last_word in articles:
        tweet = ' '.join(sent_tokes[0:-1])
    elif len(last_word) == 1:
        tweet = ' '.join(sent_tokes[0:-1])
    else:
        tweet = tweet
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
    #	engage(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)
    if args.consumer_key and args.consumer_secret:
        tweeting_clone(args.consumer_key, args.consumer_secret, args.pg_user, args.pg_password, args.pg_db, args.pg_host)
    else:
        print "Specify all arguments."
