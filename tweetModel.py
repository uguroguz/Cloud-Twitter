from google.appengine.ext import ndb

class TweetModel(ndb.Model):
    username = ndb.StringProperty()
    text = ndb.StringProperty()
    image = ndb.BlobKeyProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
   