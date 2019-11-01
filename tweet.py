import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb

from google.appengine.ext.webapp import blobstore_handlers

from userModel import UserModel
from tweetModel import TweetModel


JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True
)


class AddTweet(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        text = self.request.get('tweet_text') 
        
        if len(text) > 280 :
            message="length is restricted to 280 chars your char length is "+len(text)
            self.redirect('/')
        
        else:
            user = users.get_current_user()
            myuser_key = ndb.Key('UserModel', user.user_id())
            myuser = myuser_key.get()
            
            image = None
            typeList = ["jpg","png","jpeg"]
            if self.get_uploads():
                upload = self.get_uploads()[0] 
                blobinfo = blobstore.BlobInfo(upload.key())

                filetype = blobinfo.content_type
                filetype = filetype.split('/')
                
                if filetype[1] in typeList:                
                    image = upload.key()   
                    
                else:
                    self.redirect('/')
            
            new_tweet = TweetModel(username = myuser.username, text = text, image = image)
            myuser.tweets.append(new_tweet)
            myuser.put()
            
            message = "Shared Tweet"
            template_values = {            
                'message' : message,
                'myuser': myuser
            }
            template = JINJA_ENVIRONMENT.get_template('main.html')
            self.redirect('/',message)
            
class EditTweet(webapp2.RequestHandler):
    def get(self, param):

        self.response.headers['Content-Type'] = 'text/html'

        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()
        index = -1
        
        for i, tweets in enumerate(myuser.tweets):
            if str(tweets.timestamp) == str(param):
                index = i
                break
        
        if index == -1:
            self.redirect('/')
        else:
            tweet = myuser.tweets[index]

            template_values = {
                'myuser' : myuser,
                'tweet' : tweet,
                'tweet_ind' : index           
            }

            template = JINJA_ENVIRONMENT.get_template('tweetEdit.html')
            self.response.write(template.render(template_values))

    def post(self, param):

        self.response.headers['Content-Type'] = 'text/html'
        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()
        #receive index as parameter
        myuser.tweets[int(param)].text = self.request.get('tweet_text')
        
        myuser.put()

        self.redirect('/profile')


class DeleteTweet(webapp2.RequestHandler):
    def post(self):

        self.response.headers['Content-Type'] = 'text/html'

        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()
        index = -1
        time = self.request.get('timestamp')
        for i, tweets in enumerate(myuser.tweets):
            if str(tweets.timestamp) == str(time):
                index = i
                break
        
        if index == -1:
            self.redirect('/')
        else:
            del myuser.tweets[index]
            myuser.put()
            self.redirect('/profile')
        





