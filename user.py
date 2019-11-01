import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images
from userModel import UserModel

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True
)

class UserValidate(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        user = users.get_current_user()
        
        template_values = {
            'user' : user
        }

        template = JINJA_ENVIRONMENT.get_template('user_confirm.html')
        self.response.write(template.render())
    
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        message = ""
        user = users.get_current_user()

        username =self.request.get('username')
        check_username = UserModel.query(UserModel.username == username).fetch()
        
        if not check_username:
            myuser = UserModel(id = user.user_id(), username = username, email_address = user.email())
            myuser.put()
            message = "Validation Completed"
            template = JINJA_ENVIRONMENT.get_template('main.html')
        else:
            message = "Username already exist please chose new username"
            myuser = ""
            template = JINJA_ENVIRONMENT.get_template('user_confirm.html')

        template_values = {
        'myuser' : myuser,
        'message' : message
        }
        self.response.write(template.render(template_values))

class Update(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()
        cnt_tweets = len(myuser.tweets)

        template_values = {
            'myuser' : myuser,
            'cnt_tweets' : cnt_tweets
        }
        template = JINJA_ENVIRONMENT.get_template('userUpdate.html')
        self.response.write(template.render(template_values))
    
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'

        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()
        #button names are used depending on the input field that
        #post method receives
        if self.request.get('button') == 'update':

            description = self.request.get('content')
            if len(description) > 280:
                message = "description can contain max 280 character"
                self.redirect('/')
                
            else:
                message ="description created"
                myuser.description = description
                myuser.name = self.request.get('name')
                myuser.email_address = self.request.get('email')
                myuser.put()

            self.redirect('/')

        elif self.request.get('button') == 'description':
            description = self.request.get('content')
            if len(description) > 280:
                message = "description can contain max 280 character"
                self.redirect('/')
                
            else:
                message ="description created"
                myuser.description = description
                myuser.put()
                self.redirect('/')
        
        
class Profile(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-,type'] = 'text/html'
        
        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()
        user_tweets = myuser.tweets
        user_tweets = sorted(user_tweets, key = lambda tup : tup.timestamp, reverse = True)
        user_tweets = user_tweets[0:50]
        tw_images = []

        for tw in user_tweets:
            if tw.image == None:
                url = None
            else:
                url = images.get_serving_url( tw.image, size=150, crop=True, secure_url=True)
            tw_images.append(url)

        cnt_tweets = len(user_tweets)
        cnt_followed = len(myuser.followed_list)
        cnt_follower = len(myuser.follower_list)
        
    
        template_values = {
        'myuser' : myuser,
        'visiting': False,
        'tweets' : user_tweets,
        'images' : tw_images,
        'cnt_tweets' : cnt_tweets,
        'followed' : cnt_followed,
        'follower' : cnt_follower,
        'upload_url' : blobstore.create_upload_url('/tweet') 
        }
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(template_values)) 
    #open received username profile
    def post(self):
        self.response.headers['Content-,type'] = 'text/html'
        
        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()
        username = self.request.get('button')

        if myuser.username == username:
           self.redirect('/profile')
        
        user = UserModel.query(UserModel.username == username).fetch()
        user_tweets = user[0].tweets
        user_tweets = sorted(user_tweets, key = lambda tup : tup.timestamp, reverse = True)
        user_tweets = user_tweets[0:50]
        tw_images = []

        for tw in user_tweets:
            if tw.image == None:
                url = None
            else:
                url = images.get_serving_url( tw.image, size=150, crop=True, secure_url=True)
            tw_images.append(url)

        cnt_tweets = len(user_tweets)
        cnt_followed = len(myuser.followed_list)
        cnt_follower = len(myuser.follower_list)

        if myuser_key.id() in user[0].follower_list:
            relation = "UnFollow"
        else:
            relation = "Follow"
        
        #upload_url empty because you are at diffrent persons
        #profile so you cant tweet anything
        template_values = {
        'myuser' : user[0],
        'visiting': True,
        'relation' : relation,
        'tweets' : user_tweets,
        'images' : tw_images,
        'cnt_tweets' : cnt_tweets,
        'followed' : cnt_followed,
        'follower' : cnt_follower,
        'upload_url' : ""
        }
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(template_values))    

#displayes list of the peoples that follow you

#will receive id of the user 
class Follow_UnFollow(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-,type'] = 'text/html'
        
        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()

        relation = self.request.get('relation')
        #same user
        if myuser_key.id() == relation:
            self.redirect('/profile')

        visiting_key = ndb.Key('UserModel', relation)
        visiting = visiting_key.get()

        if relation in myuser.followed_list:
            myuser.followed_list.remove(relation)
            visiting.follower_list.remove(myuser_key.id())
            myuser.put()
            visiting.put()
        else:
            myuser.followed_list.append(relation)
            visiting.follower_list.append(myuser_key.id())
            myuser.put()
            visiting.put()


        self.redirect('/')

#display list of following or followers
class List_Following_Follower(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-,type'] = 'text/html'
        
        user = users.get_current_user()
        myuser_key = ndb.Key('UserModel', user.user_id())
        myuser = myuser_key.get()
        
        if self.request.get('list') == 'follower':
            lister_id = myuser.follower_list

        
       
        template_values = {
        'myuser' : myuser,
        'lister' : lister        
        }
        template = JINJA_ENVIRONMENT.get_template('list.html')
        self.response.write(template.render(template_values))
