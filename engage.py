"""
This is a refactor that Patrick once attempted at the Whole Foods in Gowanus.
This code is D.R.Y. (Don't Repeat Yourself). 
But the other code in this repo is W.E.T. (Works Every Time).
"""

import ConfigParser

class EngagementQueue(object):
    ''' Queue of engagements (API calls) to be executed by a QueueProcessor '''

class Campaign(object):
    ''' Information about the type of engagements that should be executed.  '''
    
    def __init__(cid, campaign_type, target, engagements_per_day,
	    engagements_per_day, token, secret

class TwitterCampaign(Campaign):

class InstagramCampaign(Campaign):

class QueueGenerator(object):
    ''' Abstract class that generates a queue of valid engagements for a list of
    campaigns.  '''

class TwitterQueueGenerator(QueueGenerator):
    ''' Generates an EngagementQueue of valid Twitter engagements. '''

class InstagramQueueGenerator(QueueGenerator):
    ''' Generates an EngagementQueue of valid Instagram engagements. '''

class QueueProcessor(object):
    ''' Executes an EngagementQueue with rate limiting .'''

class TwitterQueueProcessor(QueueProcessor):
    ''' Executes an EngagementQueue of Twitter actions.'''

class InstagramQueueProcessor(QueueProcessor):
    ''' Executes an EngagementQueue of Instagram actions.'''


def run_mr_bots(postgres, twitter, instagram):
    conn = psycopg2.connect("dbname='" + postgres['database'] + "' user='" +
	    postgres['user'] + "'password='" + postgres['password'] + "' host='"
	    + postgres['host'] + "'") 
    c = conn.cursor()

    # get all active twitter campaigns
    twitter_campaigns = [] c.execute('select c.id, c.target, \
	c.engagements_per_prey, c.engagements_per_day, a.token, a.secret, a.id \
	from campaigns c left join accounts a on c.account_id = a.id where \
	c.active = True') 
    for camp in c.fetchall():
    twitter_campaigns.push(TwitterCampaign(

    	
    # get all active instagram campaigns
    c.execute('select c.id, c.target, c.engagements_per_prey, \
	c.engagements_per_day, a.token, a.secret, a.id from campaigns c left \
	join accounts a on c.account_id = a.id where c.active = True')

if __name__  == "__main__":
    parser = argparse.ArgumentParser(description="Perform and egnagement run \
	    based on config file.")
    parser.add_argument('config',  nargs='?', help='config file to define \
    egagement')

    config = ConfigParser.ConfigParser()
    config.read("mr_bots_prod.cfg")

    postgres = {}
    postgres['user'] = config.get("Postgres","User")
    postgres['password'] = config.get("Postgres","Password")
    postgres['database'] = config.get("Postgres","Database")
    postgres['host'] = config.get("Postgres","Host")

    twitter = {}
    twitter['consumer_key'] = config.get("Twitter","Consumer Key")
    twitter['consumer_secret'] = config.get("Twitter","Consumer Secret")


    instagram = {}
    instagram['consumer_key'] = config.get("Instagram","Consumer Key")
    instagram['consumer_secret'] = config.get("Instagram","Consumer Secret")
    run_mr_bots(postgres, twitter, instagram)
