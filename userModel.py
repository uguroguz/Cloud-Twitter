from google.appengine.ext import ndb
from tweetModel import TweetModel
class UserModel(ndb.Model):
    username = ndb.StringProperty()
    name = ndb.StringProperty()
    email_address = ndb.StringProperty()
    description = ndb.StringProperty()
    follower_list = ndb.StringProperty(repeated = True)
    followed_list = ndb.StringProperty(repeated = True)
    tweets = ndb.StructuredProperty(TweetModel, repeated = True)