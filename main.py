#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""

import webapp2
from google.appengine.api import mail, app_identity


from models import User, WarGame

"""SendReminderEmail handler reminder email is only sent to users that
have incomplete games (or some other logic that makes sense to you)
"""


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()

        users = User.query(User.email != None)

        for user in users:
            games = WarGame.query(WarGame.user == user.key, WarGame.game_over == False)
            if games:
                for game in games:
                    subject = 'This is a War Game reminder!'
                    body = 'Hello {}, try out War Game {}!'.format(user.name,
                                                                   game.name)
                    # This will send test emails,
                    # the arguments to send_mail are:
                    # from, to, subject, body
                    mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                                   user.email,
                                   subject,
                                   body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)
