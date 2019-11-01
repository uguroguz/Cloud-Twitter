import webapp2
import jinja2
import os

from google.appengine.ext import ndb
from google.appengine.api import users

from userModel import UserModel
from tweetModel import TweetModel

from user import *
from tweet import *

from google.appengine.ext import blobstore
from google.appengine.api import images

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True
)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        url =''
        url_string = ''
        user = users.get_current_user() 
        myuser = None
        
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = 'logout'

            myuser_key = ndb.Key('UserModel', user.user_id())
            myuser = myuser_key.get()

            #if user dnt exst in our db add
            if myuser == None:
                self.redirect('/validation')
            else:

                all_users = UserModel.query().fetch()
        
                followed_user_tweets =[]
                tweets = []
                
                for i in all_users :
                    if i.key.id() in myuser.followed_list:
                        followed_user_tweets +=i.tweets
                
                tweets = sorted(followed_user_tweets, key = lambda x : x.timestamp, reverse = True)
                tweets = tweets[0:50]
                tw_images = []

                for tw in tweets:
                    if tw.image == None:
                        url = None
                    else:
                        url = images.get_serving_url( tw.image, size=150, crop=True, secure_url=True)
                    tw_images.append(url)

                cnt_disp_tweets = len(tweets)
                cnt_tweets = len(myuser.tweets)
                cnt_followed = len(myuser.followed_list)
                cnt_follower = len(myuser.follower_list)
                template_values = {
                    'url' : url,
                    'url_string' : url_string,
                    'tweets' : tweets,
                    'cnt' : cnt_disp_tweets,
                    'images' : tw_images,
                    'myuser' : myuser,
                    'cnt_tweets' : cnt_tweets,
                    'followed' : cnt_followed,
                    'follower' : cnt_follower,
                    'upload_url' : blobstore.create_upload_url('/tweet') 
                }
                
                template = JINJA_ENVIRONMENT.get_template('main.html')
                self.response.write(template.render(template_values))
                
        else:            
            url = users.create_login_url(self.request.uri)
            url_string = 'login'
            self.redirect(url)



class Search(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-,type'] = 'text/html'
        
        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()

        search = self.request.get('search')
        all_users = UserModel.query().fetch()

        
        matched_users = []
        matched_tweets = []
        tw_images = []

        for i in all_users:
            if search in i.username:
                matched_users.append(i.username) 
            for j in i.tweets:
                if search in j.text:
                    matched_tweets.append(j)
                    if j.image == None:
                        url = None
                    else:
                        url = images.get_serving_url( j.image, size=150, crop=True, secure_url=True)
                    tw_images.append(url)
                
        m_tweets =len(matched_tweets)
        template_values = {   
            'myuser' : myuser,
            'searched_users' : matched_users,
            'searched_tweets' : matched_tweets,
            'cnt': m_tweets,
            'images': tw_images
        }

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/validation', UserValidate),
    ('/update', Update),
    ('/profile', Profile),
    ('/follow_unfollow', Follow_UnFollow),
    ('/list', List_Following_Follower),
    ('/search',Search),
    ('/tweet', AddTweet),
    ('/edit/(.*?)', EditTweet),
    ('/tweet/delete', DeleteTweet)  
], debug = True)