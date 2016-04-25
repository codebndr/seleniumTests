#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codebender_testing.config import get_path
import disqusapi
import simplejson
import base64
import hashlib
import hmac
import time
import os
import re


FORUM = os.getenv('DISQUS_FORUM', 'codebender-cc')
AUTHOR_URL = os.getenv('AUTHOR_URL', 'https://codebender.cc/user/codebender')
DISQUS_REQUESTS_PER_HOUR = 1000
DISQUS_WAIT = (DISQUS_REQUESTS_PER_HOUR / 60) / 60
CHANGE_LOG = 'examples_compile_log.json'
DISQUS_COMMENTS = 'disqus_comments.json'
EXAMPLES_WITHOUT_LIBRARY_DB = 'examples_without_library.json'


class DisqusWrapper:
    def __init__(self, log_time):
        self.log_time = log_time
        self.DISQUS_API_SECRET = os.getenv('DISQUS_API_SECRET', None)
        self.DISQUS_API_PUBLIC = os.getenv('DISQUS_API_PUBLIC', None)
        self.DISQUS_ACCESS_TOKEN = os.getenv('DISQUS_ACCESS_TOKEN', None)
        self.user = {
            'id': os.getenv('DISQUS_SSO_ID', None),
            'username': os.getenv('DISQUS_SSO_USERNAME', None),
            'email': os.getenv('DISQUS_SSO_EMAIL', None),
        }
        self.SSO_KEY = self.get_disqus_sso(self.user)
        self.disqus = disqusapi.DisqusAPI(api_secret=self.DISQUS_API_SECRET,
                                        public_key=self.DISQUS_API_PUBLIC,
                                        remote_auth=self.SSO_KEY)
        self.change_log = {}
        self.last_post = None
        self.last_library = None

        with open(get_path('data', DISQUS_COMMENTS)) as f:
            self.messages = simplejson.loads(f.read())

        with open(get_path('data', EXAMPLES_WITHOUT_LIBRARY_DB)) as f:
            self.examples_without_library = simplejson.loads(f.read())

    def get_disqus_sso(self, user):
        # create a JSON packet of our data attributes
        data = simplejson.dumps(user)
        # encode the data to base64
        message = base64.b64encode(data)
        # generate a timestamp for signing the message
        timestamp = int(time.time())
        # generate our hmac signature
        sig = hmac.HMAC(self.DISQUS_API_SECRET, '%s %s' % (message, timestamp), hashlib.sha1).hexdigest()
        return "{0} {1} {2}".format(message, sig, timestamp)

    def update_comment(self, sketch, results, current_date, log_entry, openFailFlag, total_sketches):
        """A comment is added to the library as soon as its first example is compiled.
        `library`: The library in which belongs the currently compiled example.
        `self.last_library`: The library in which belongs the previously compiled example.
        `library_to_comment`: The library in which a comment should be added.
        """
        library_match = re.match(r'.+\/example\/(.+)\/.+', sketch)
        library = None
        library_to_comment = None

        # Set the library in which belongs the currently compiled example.
        if library_match:
            library = library_match.group(1)

        # Check if the currently compiled example belongs to the same library as the previous one.
        # To do so we check if value of library is the same with self.last library value which is updated
        # every time that we log the results of a compiled example.
        if library != self.last_library:
            library_to_comment = library

        # Check if we should add a comment to the library.
        if library_to_comment and library not in self.examples_without_library:
            log_entry = self.handle_library_comment(library_to_comment, current_date, log_entry)

        self.last_library = library
        # Add a comment to the currently compiled library example.
        if not openFailFlag:
            log_entry = self.handle_example_comment(sketch, results, current_date, log_entry)

        return log_entry

    def handle_library_comment(self, library, current_date, log, examples=True):
        url = '/library/' + library
        identifier = 'ident:' + url

        if url not in log:
            log[url] = {}
        try:
            log[url]['comment'] = False

            """ Returns a Paginator object that matches the desired criteria:
            `self.disqus.api.threads.list`: Returns a list containg all urls in which Disqus loaded.
            `forum`: Looks up a forum by short name.
            `thread`: Looks up a thread by ID BUT you may pass us the 'ident' query type instead of
            an ID by including 'forum'. Filters results returned from `self.disqus.api.threads.list`
            and returns only those which match `forum` and `thread`.
            IMPORTANT: If `thread` is not found, all threads are returned!!!
            """
            paginator = disqusapi.Paginator(self.disqus.api.threads.list,
                                            forum=FORUM,
                                            thread=identifier)
            if paginator:
                comment_updated = False

                new_message = self.messages['library'].replace('TEST_DATE', current_date)
                if examples == False:
                    new_message = self.messages['library_no_examples'].replace('TEST_DATE', current_date)

                for thread in paginator:

                    # Check if library has already a comment.
                    post_id, existing_message = self.get_posts(thread['id'])

                    # If library already has a comment, update it.
                    if post_id and existing_message:
                        log[url]['comment'] = self.update_post(post_id, new_message)
                        comment_updated = True
                        break

                # If library doesn't have a comment, create it.
                if not comment_updated:
                    log[url]['comment'] = self.create_post(identifier, new_message)

        except Exception as error:
            print 'Error:', error
            log[url]['comment'] = False

        return log

    def handle_example_comment(self, url, results, current_date, log):
        identifier = re.sub(r'https*://.*codebender.cc', '', url)
        identifier = 'ident:' + identifier
        try:
            log[url]['comment'] = False
            paginator = disqusapi.Paginator(self.disqus.api.threads.list,
                                            forum=FORUM,
                                            thread=identifier, method='GET')
            if paginator:
                comment_updated = False
                boards = []
                unsupportedFlag = False
                for result in results:
                    if result['status'] == 'success':
                        board = result['board']
                        if re.match(r'Arduino Mega.+', board):
                            board = 'Arduino Mega'
                        boards.append(board)
                    elif result['status'] == 'unsupported':
                        unsupportedFlag = True

                new_message = self.messages['example_fail'].replace('TEST_DATE', current_date)
                if len(boards) > 0:
                        new_message = self.messages['example_success'].replace('TEST_DATE', current_date).replace('BOARDS_LIST', ', '.join(boards))
                elif unsupportedFlag:
                    new_message = self.messages['example_unsupported'].replace('TEST_DATE', current_date)

                for page in paginator:
                    post_id, existing_message = self.get_posts(page['id'])
                    if post_id and existing_message:
                        log[url]['comment'] = self.update_post(post_id, new_message)
                        comment_updated = True
                        break

                if not comment_updated:
                    log[url]['comment'] = self.create_post(identifier, new_message)
        except Exception as error:
            print 'Error:', error
            log[url]['comment'] = False

        return log

    def get_posts(self, thread_id):
        post_id = None
        raw_message = None
        try:
            """ Returns a Paginator object that matches the desired criteria:
            `self.disqus.api.posts.list`: Returns a list of posts ordered by the date created.
            `forum`: Looks up a forum by short name.
            `thread`: Looks up a thread by ID. Filters results returned from `self.disqus.api.posts.list`
            and returns only those which match `forum` and `thread`.
            """
            paginator = disqusapi.Paginator(self.disqus.api.posts.list,
                                            forum=FORUM,
                                            thread=thread_id,
                                            order='asc')
            if paginator:
                for post in paginator:
                    if post['author']['name'] == self.user['username'] and post['author']['url'] == AUTHOR_URL:
                        post_id = post['id']
                        raw_message = post['raw_message']
                        break
        except Exception as error:
            print 'Error:', error

        return post_id, raw_message

    def create_post(self, thread_id, message):
        if not self.last_post:
            self.last_post = message
        elif re.match(r'^.+\.$', self.last_post):
            message = message[:-1]

        comment_status = False

        try:
            response = self.disqus.threads.list(api_secret=self.DISQUS_API_SECRET,
                                                forum=FORUM,
                                                thread=thread_id, method='GET')
            response = self.disqus.posts.create(api_secret=self.DISQUS_API_SECRET,
                                                remote_auth=self.SSO_KEY,
                                                thread=response[0]['id'],
                                                message=message, method='POST')
            if response['raw_message'] == message:
                self.last_post = message
                comment_status = True
        except Exception as error:
            print 'Error:', error

        return comment_status

    def update_post(self, post_id, message):
        if not self.last_post:
            self.last_post = message
        elif re.match(r'^.+\.$', self.last_post):
            message = message[:-1]

        comment_status = False

        try:
            response = self.disqus.posts.update(api_secret=self.DISQUS_API_SECRET,
                                                access_token=self.DISQUS_ACCESS_TOKEN,
                                                remote_auth=self.SSO_KEY,
                                                post=post_id,
                                                message=message, method='POST')
            if response['raw_message'] == message:
                self.last_post = message
                comment_status = True
        except Exception as error:
            print 'Error:', error

        return comment_status
