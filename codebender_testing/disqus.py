#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codebender_testing.config import get_path
import disqusapi
import requests
import simplejson
import base64
import hashlib
import hmac
import time
import random
import os
import re


FORUM = 'codebender-cc'
AUTHOR_NAME = 'codebender'
AUTHOR_URL = 'https://codebender.cc/user/codebender'
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
        self.disqus = disqusapi.DisqusAPI(api_secret=self.DISQUS_API_SECRET, public_key=self.DISQUS_API_PUBLIC, remote_auth=self.SSO_KEY)
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

    def update_comment(self, sketch, results, current_date, log_entry, openFailFlag, counter, total_sketches):
        # Comment examples
        if not openFailFlag:
            log_entry = self.handle_example_comment(sketch, results, current_date, log_entry)

        # Comment libraries when finished with the examples
        library_match = re.match(r'.+\/example\/(.+)\/.+', sketch)
        library = None
        if library_match:
            library = library_match.group(1)
        if not self.last_library:
            self.last_library = library
        if library and library != self.last_library and (library not in self.examples_without_library or counter >= total_sketches-1):
            log_entry = self.handle_library_comment(library, current_date, log_entry)
            last_library = library

        return log_entry

    def handle_library_comment(self, library, current_date, log):
        url = '/library/' + library
        identifier = 'ident:' + url
        paginator = disqusapi.Paginator(self.disqus.api.threads.list, forum=FORUM, thread=identifier, method='GET')
        if paginator:
            for page in paginator:
                post_id, existing_message = self.get_posts(page['id'])
                if post_id and existing_message:
                    new_message = self.messages['library'].replace('TEST_DATE', current_date)
                    if url not in log:
                        log[url] = {}
                    log[url]['comment'] = self.update_post(post_id, new_message)
        else:
            log[url][comment] = False
        return log

    def handle_example_comment(self, url, results, current_date, log):
        identifier = url.replace('https://codebender.cc', '')
        identifier = 'ident:' + identifier
        paginator = disqusapi.Paginator(self.disqus.api.threads.list, forum=FORUM, thread=identifier, method='GET')
        if paginator:
            for page in paginator:
                post_id, existing_message = self.get_posts(page['id'])
                if post_id and existing_message:
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
                    log[url]['comment'] = self.update_post(post_id, new_message)
                    break
        else:
            log[url]['comment'] = False
        return log

    def get_posts(self, thread_id):
        post_found = False
        post_id = None
        raw_message = None
        paginator = disqusapi.Paginator(self.disqus.api.posts.list, forum=FORUM, thread=thread_id, order='asc', method='GET')
        if paginator:
            for result in paginator:
                if result['author']['name'] == AUTHOR_NAME and result['author']['url'] == AUTHOR_URL:
                    post_id = result['id']
                    raw_message = result['raw_message']
                    break
        return post_id, raw_message

    def update_post(self, post_id, message):
        if not self.last_post:
            self.last_post = message
        elif re.match(r'^.+\.$', self.last_post):
            message = message[:-1]
        self.last_post = message
        try:
            response = self.disqus.posts.update(api_secret=self.DISQUS_API_SECRET, api_key=self.DISQUS_API_PUBLIC, remote_auth=self.SSO_KEY, access_token=self.DISQUS_ACCESS_TOKEN, post=post_id, message=message, method='POST')
            if response['raw_message'] == message:
                return True
            return False
        except Exception as error:
            print 'Error:', error
            return False
