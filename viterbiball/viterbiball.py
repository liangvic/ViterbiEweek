from google.appengine.api import users #integrate Google account sign in

import webapp2 #web framework for python


class MainPage(webapp2.RequestHandler):

    def get(self):
		user = users.get_current_user()
		if user:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write('2015 E-Week Viterbi Ball\n')
			self.response.write('Welcome, ' + user.nickname() +'\n')
		else:
			#redirect to login page, which will auto redirect back to this page using "self.request.uri"
			self.redirect(users.create_login_url(self.request.uri))


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True) #prints stack traces if exception is caught; should remove from final version