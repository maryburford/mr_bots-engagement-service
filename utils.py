import markov
import random
import re

# appropriated from clone_2.py
def check_tweet(tweet, tweet_texts):
    tweet_texts = frozenset(tweet_texts)
    clean_tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*|\@\w+', '',tweet)
    return clean_tweet in tweet_texts


# generic get tweets function with optional lmit
def get_tweets(api, id_str, max_results = 3200):
    kw = {  # args for the Twitter API call
        'id_str': id_str,
        'since_id' : 1,
        'count': 200,
        }

    max_pages = 16
    results = []

    tweets = api.user_timeline(**kw)

    if tweets is None: # 401 (Not Authorized) - Need to bail out on loop entry
        tweets = []

    results += tweets
    page_num = 1

    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry

    while page_num < max_pages and len(tweets) > 0 and len(results) < max_results:
        kw['max_id'] = min([ tweet['id'] for tweet in tweets]) - 1

        tweets = api.user_timeline(**kw)
        results += tweets
        page_num += 1

    return results[:max_results]


# appropriated from clone_2.py
def create_corpus(tweets):
    corpus = []

    for i in tweets:
        keys = i.keys()
        if 'extended_entities' in keys:
            text = str(i['text'].encode("utf-8")).replace('&amp;','&')
            tweet_text = text.split('http')[0]
            corpus.append(re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*|\@\w+', '',tweet_text))
        else:
            tweet_text = str(i['text'].encode("utf-8")).replace('&amp;','&')
            corpus.append(re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*|\@\w+', '',tweet_text))

    return corpus


# this is a copy of the function in clone_2.py, but
# hopefully can refactor that code to use this function too
def generateTweets(tweets):
    order = 2
    corpus = create_corpus(tweets)
    mine = markov.MarkovChainer(order)
    for tweet in corpus:
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
        rando = random.randint(0, 10)
        if rando == 0 or rando == 7:
            newer_tweet = mine.generate_sentence()
            if newer_tweet != None:
                tweet += " " + mine.generate_sentence()
            else:
                tweet = tweet
        elif rando == 1:
            tweet = tweet.upper()

    # checks to see if tweet is not in original corpus
    already_tweeted = check_tweet(tweet, corpus)

    if already_tweeted:
        generateTweets(tweets)
    else:
        return tweet
