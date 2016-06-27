import tweepy
import json
import random
from utils import generateTweets, get_tweets

# TODO: reading from static file, should read from mr_bots db
with open('./mr_accounts.json') as data:
    accounts = json.load(data)

class Engager(object):

    def __init__(self, account):
        self.account = account
        creds = account['creds']
        self.auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
        self.auth.set_access_token(creds['access_token_key'], creds['access_token_secret'])
        self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())
        self.tweet_corpus = []

    def follow_user(self):
        # TODO: this needs paging implemented
        following = self.api.friends_ids(id = self.account['id_str'])['ids']

        possible_follows = []
        for acct in accounts:
            # tweepy seems to return id_strs, but as ints ??? *swaggy p face*
            acct_id = int(acct['id_str'])
            if acct_id not in following:
                possible_follows.append(acct)

        if len(possible_follows) == 0:
            return False

        new_follow = random.sample(possible_follows, 1)[0]
        self.api.create_friendship(id = new_follow['id_str'])

        # print 'created friendship with ' +  str(new_follow['screen_name']) + ' from ' + self.account['screen_name']
        return True


    def get_timeline(self, filter_engaged = True, filter_self = True):
        # TODO: this needs paging implemented
        timeline = self.api.home_timeline(count = 200)

        def not_engaged(tweet):
            return tweet['favorited'] == False and tweet['retweeted'] == False

        def not_self(tweet):
            return tweet['user']['id_str'] != self.account['id_str']

        if filter_engaged:
            timeline = filter(not_engaged, timeline)
        if filter_self:
            timeline = filter(not_self, timeline)

        return timeline

    def fav_tweet(self):
        timeline = self.get_timeline()

        if len(timeline) == 0:
            return False

        rand_tweet = random.sample(timeline, 1)[0]
        self.api.create_favorite(rand_tweet['id_str'])

        # print 'faved tweet ' +  rand_tweet['text'] + ' from ' + rand_tweet['user']['screen_name']
        return True

    def rt_tweet(self):
        timeline = self.get_timeline()

        if len(timeline) == 0:
            return False

        rand_tweet = random.sample(timeline, 1)[0]
        self.api.retweet(rand_tweet['id_str'])

        # print 'retweeted tweet ' +  rand_tweet['text'] + ' from ' + rand_tweet['user']['screen_name']
        return True

    def reply_to_random_tweet(self):
        timeline = self.get_timeline(filter_engaged = False)

        if len(timeline) == 0:
            return False

        rand_tweet = random.sample(timeline, 1)[0]
        rand_user_id = rand_tweet['user']['id_str']
        rand_user_name = rand_tweet['user']['screen_name']
        tweets = get_tweets(self.api, self.account['id_str'])
        tweeters_tweets = get_tweets(self.api, rand_user_id, len(tweets))
        all_tweets = tweets + tweeters_tweets

        response = generateTweets(all_tweets)
        response = '@' + rand_user_name + ' ' +  response
        self.api.update_status(status = response, in_reply_to_status_id = rand_user_id)

        # print 'replied to tweet ' +  rand_tweet['text'] + ' from ' + rand_tweet['user']['screen_name'] + ' with ' + response
        return True


    def reply_to_mention(self):
        mentions = self.api.mentions_timeline(count = 200, since_id = 1)
        if len(mentions) == 0:
            print 'no mentions to respond to'
            return False

        def is_reply(t):
            return t.get('in_reply_to_status_id_str', False)

        tweets = get_tweets(self.api, self.account['id_str'])
        # filter tweets by reply id_strs
        replies = map(is_reply, filter(is_reply, tweets))
        # assume the worst
        replied = False

        for m in mentions:
            if m['id_str'] not in replies:
                # use equal amount of mentioners tweets
                mentioner_tweets = get_tweets(self.api, m['user']['id_str'], len(tweets))
                all_tweets = tweets + mentioner_tweets
                # generate tweet with entire corpus
                response = generateTweets(all_tweets)
                response = '@' + m['user']['screen_name'] + ' ' +  response
                self.api.update_status(status = response, in_reply_to_status_id = m['id_str'])
                replied = True

        return replied


    def engage(self):
        possible_actions = [
                'follow_user',
                'reply_to_mention',
                'fav_tweet',
                'rt_tweet',
                'reply_to_random_tweet'
                ]
        rand_action = random.sample(possible_actions, 1)[0]

        action = getattr(self, rand_action)
        engagement = action()

        if engagement:
            print 'did ' + rand_action + ' successfully'
        else:
            print rand_action + ' done fucked up :('


if __name__ == "__main__":
    rand_acct = random.sample(accounts, 1)
    # 55 the test account im using lol
    mr_bots_engager = Engager(accounts[55])
    mr_bots_engager.engage()
