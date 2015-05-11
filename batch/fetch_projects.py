#!/usr/bin/env python3
"""A script to downloads all projects for a particular user."""

# This is necessary in order to run the script; otherwise the script needs to
# be run as a python module (which is inconvenient).
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.join(path.dirname(path.abspath(__file__)), '..'))


from urllib.request import urlopen
from urllib.request import urlretrieve
import argparse
import os

from codebender_testing.config import LIVE_SITE_URL

from lxml import html


def download_projects(url, user, path):
    connection = urlopen('/'.join([url, 'user', user]))
    dom = html.fromstring(connection.read().decode('utf8'))
    os.chdir(path)
    for link in dom.xpath('//table[@id="user_projects"]//a'):
        project_name = link.xpath('text()')[0]
        sketch_num = link.xpath('@href')[0].split(':')[-1]
        print("Downloading %s (sketch %s)" % (project_name, sketch_num))
        urlretrieve('%s/utilities/download/%s' % (url, sketch_num),
            os.path.join(path, '%s.zip' % project_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("user", help="the user whose projects we want to download")
    parser.add_argument("-u", "--url", help="url of the codebender site to use",
                        default=LIVE_SITE_URL)
    parser.add_argument("-d", "--directory", help="output directory of the downloaded projects",
                        default=".")
    args = parser.parse_args()
    download_projects(args.url, args.user, args.directory)
