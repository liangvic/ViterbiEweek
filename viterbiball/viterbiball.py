
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


DEFAULT_SALESBOOK_NAME = 'default_salesbook'


# We set a parent key on the 'Students' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def salesbook_key(salesbook_name=DEFAULT_SALESBOOK_NAME):
    """Constructs a Datastore key for a Salesbook entity with salesbook_name."""
    return ndb.Key('Salesbook', salesbook_name)


class Student(ndb.Model):
    """Models an individual Salesbook entry with email, name, and date."""
    email = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    uscid = ndb.StringProperty(indexed=False)
    major = ndb.StringProperty(indexed=False)
    year = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)



class MainPage(webapp2.RequestHandler):

    def get(self):
        salesbook_name = self.request.get('salesbook_name',
                                          DEFAULT_SALESBOOK_NAME)
        students_query = Student.query(
            ancestor=salesbook_key(salesbook_name)).order(-Student.date)
        students = students_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'students': students,
            'salesbook_name': urllib.quote_plus(salesbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('frontpage.html')
        self.response.write(template.render(template_values))



class Salesbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Student' to ensure each Student
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        salesbook_name = self.request.get('salesbook_name',
                                          DEFAULT_SALESBOOK_NAME)
        student = Student(parent=salesbook_key(salesbook_name))
			
		#student.email = self.request.get('email')
        student.name = self.request.get('name')
        student.uscid = self.request.get('id')
        student.major = self.request.get('major')
        student.year = self.request.get('year')
        student.put()

        query_params = {'salesbook_name': salesbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register', Salesbook),
], debug=True)
