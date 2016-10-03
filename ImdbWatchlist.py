#!/usr/bin/env python
#
# IMDb watchlist feed script for NZBGet
#
# Copyright (C) 2015 Andrey Prygunkov <hugbug@users.sourceforge.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#


##############################################################################
### NZBGET FEED SCRIPT                                                     ###

# Filters rss feed and keeps only items which are in your IMDb watchlist.
#
# The watchlist must be public, since the script fetches it without
# authorization on imdb.com.
#
# Info about pp-script:
# Author: Andrey Prygunkov (nzbget@gmail.com).
# License: GPLv3 (http://www.gnu.org/licenses/gpl.html).
# PP-Script Version: 1.1.
#
# NOTE: This script requires Python to be installed on your system.

##############################################################################
### OPTIONS                                                                ###

# IMDb user id.
#
# On www.imbd.com open your watchlist, the user id is in the URL. Put the ID
# here (only digits).
#ImdbUserId=

# Print more logging messages (yes, no).
#
# For debugging or if you need to report a bug.
#Verbose=no

### NZBGET FEED SCRIPT                                                     ###
##############################################################################

import sys
from os.path import dirname
sys.path.append(dirname(__file__) + '/lib')
import os
import re
import urllib2
import traceback

# Exit codes used by NZBGet
FEEDSCRIPT_SUCCESS=93
FEEDSCRIPT_ERROR=94

# Check if all required script config options are present in config file
required_options = ('NZBPO_ImdbUserId', 'NZBPO_Verbose')
for optname in required_options:
    if (not optname.upper() in os.environ):
        print('[ERROR] Option %s is missing in configuration file. Please check script settings' % optname[6:])
        sys.exit()

# Init script config options
imdbid=int(os.environ['NZBPO_IMDBUSERID'])
verbose=os.environ['NZBPO_VERBOSE'] == 'yes'

# Init script context
rssfeed_file=os.environ['NZBFP_FILENAME']
# env var "NZBPO_WATCHLISTFILE" for development purposes (to avoid imdb request on each test)
watchlist_file=os.environ.get('NZBPO_WATCHLISTFILE')
out_file=os.environ.get('NZBPO_FEEDOUTFILE')

errors = False

def fetch_watchlist():
    """ fetch watchlist from imdb.com """
    url = 'http://rss.imdb.com/user/ur%s/watchlist' % (imdbid)
    if verbose:
        print('Fetching watchlist from imdb.com...')
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    data = response.read()
    if watchlist_file:
        open(watchlist_file, 'w').write(data)
    if verbose:
        print('Fetching watchlist from imdb.com...done')
    return data

def load_watchlist():
    """ load watchlist either from cache or from imdb.com """
    if watchlist_file and os.path.isfile(watchlist_file):
        watchlist = open(watchlist_file).read()
    else:
        watchlist = fetch_watchlist()
    return watchlist

def collect_imdbids(watchlist):
    """ parse watchlist and collect all imdbids """
    ID_SIGNATURE_START = '            <guid>http://www.imdb.com/title/tt'
    ID_SIGNATURE_END = '/</guid>'
    imdbids = []
    for line in watchlist.splitlines():
        if line.startswith(ID_SIGNATURE_START):
            id = line[len(ID_SIGNATURE_START):len(line)-len(ID_SIGNATURE_END)]
            imdbids.append(id)
    return imdbids

def load_rssfeed(rssfeed_file):
    """ load rss-feed from file """
    data = open(rssfeed_file).read()
    return data

def save_rssfeed(rssfeed_file, data):
    """ save rss-feed back into file """
    open(rssfeed_file, 'w').write(data)

def filter_feed(feed, imdbids):
    """ build new rss feed containing only items with imdb-id from watchlist """
    if verbose:
        print('Filtering')
    new_feed = ''
    in_item = False
    item_content = ''
    item_id = None
    for line in feed.splitlines():
        if in_item:
            if line.find('</item>') > -1:
                in_item = False
                if item_id and (item_id in imdbids):
                    if verbose:
                        print('[DETAIL] Keeping imdbid %s' % item_id)
                    new_feed += item_content + line + "\n"
                else:
                    if verbose:
                        print('[DETAIL] Discarding imdbid %s' % item_id)
            else:
                if line.find(':attr') > -1 and line.find('imdb') > -1:
                    pe = line.rfind('"')
                    ps = line.rfind('"', 0, pe-1)
                    item_id = line[ps+1:pe]
                item_content += line + "\n"
        else:
            if line.find('<item>') > -1:
                in_item = True
                item_id = None
                item_content = line + "\n"
            else:
                new_feed += line + "\n"
    return new_feed

try:
    watchlist = load_watchlist()
    if verbose:
        print(watchlist)

    imdbids = collect_imdbids(watchlist)
    if verbose:
        print('IMDb-ID List: %s' % imdbids)

    feed = load_rssfeed(rssfeed_file)
    filtered_feed = filter_feed(feed, imdbids)
    save_rssfeed(rssfeed_file if not out_file else out_file, filtered_feed)

except Exception as e:
    errors = True
    # deleting the feed-xml-file to avoid enqueueing of non-filtered feed
    os.remove(rssfeed_file)
    print('[ERROR] %s' % e)
    traceback.print_exc()

if errors:
    sys.exit(FEEDSCRIPT_ERROR)
else:
    sys.exit(FEEDSCRIPT_SUCCESS)
