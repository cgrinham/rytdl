RYTDL (Reddit YouTube Downloader)
=================================

Download all YouTube links in a subreddit as MP3s for listening.

Set Up
------

RYTDL uses the Reddit API so you will need a Reddit account and you will need to set up a developer app (to get a client id and client secret), then run:
> python rytdl.py --setup

RYTDL is written in Python 3 and has a few dependencies. You can install this with pip by running
> sudo pip3 install praw mutagen youtube_dl
> sudo apt-get install python3-yaml

How To Use
----------
Run from CLI specifying a subreddit. For example, to download all YouTube videos from /r/house:
> python rytdl.py -s house


Options
-------

By default the genre tag is set to the subreddit title. 
To specify the Genre tag in the output MP3s:
> python rytdl.py -s house -g House

To specify number of submissions to retrieve:
> python rytdl.py -s house -g House -n 30 house

Please note that only submissions from YouTube will be downloaded. So specifying 30 submissions might download less than 30 MP3s.

Submissions are sorted by "hot" by default.
To sort submissions by top all time:
> python rytdl.py -s house -g House -t

Sort submissions by top past month:
> python rytdl.py -s house -g House -m


To Do
-----
- Download only tracks with more than x upvotes
- GUI?
- Support other youtube links i.e. youtu.be
