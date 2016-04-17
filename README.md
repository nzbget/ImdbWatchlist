# ImdbWatchlist
This is a feed-script for [NZBGet](https://github.com/nzbget/nzbget), which integrates into RSS feed and processes it in a special way.
It fetches your watchlist from imdb.com, then reads the rss feed content and keeps items which are in your watchlist but removes everything else.

## How to use
- create an imdb account if you don't have one yet;
- browse imdb.com and click "add to watchlist" on movies you are interested in;
- configure the watchlist to be public (this is needed because the script fetches watchlist without authorization on imdb.com);
- install the script by putting it into scripts directory of your NZBGet installation;
- put your imdb user id into script settings;
- create new rss feed, put an rss feed URL from your indexer, for example the feed for category "Movies -> HD";
- in the feed setting select the script in option FeedScript;
- save the settings.

If you have troubles following this instructions please see the [detailed installation guide]().

That's all. Now when you see a new interesting movie on IMDb you just add it to your watchlist and it will be monitored by NZBGet.

To test how it works - if you browse the feed content in NZBGet the feed will only contains items from IMDb watchlist. The feed may be empty if no items from watchlist were found in the original feed.

## Quality control
For fine tuning (quality settings, etc.) use the filter field as usual. See [RSS](https://github.com/nzbget/nzbget/wiki/RSS) for details.
