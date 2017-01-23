RYTDL (Reddit YouTube Downloader)
=================================

Download all YouTube links in a subreddit as MP3s for listening.

Set Up
------

RYTDL uses the Reddit API so you will need a Reddit account and you will need to set up a developer app (to get a client id and client secret), then run:
> python rytdl.py -s


How To Use
----------
Run from CLI specifying a subreddit. For example, to download all YouTube videos from /r/house:
> python rytdl.py house

To specify the Genre tag in the output MP3s:
> python rytdl.py -g House house

To specify number of submissions to retrieve:
> python rytdl.py -s 30 house

Please note that only submissions from YouTube will be downloaded. So specifying 30 submissions might download less than 30 MP3s.


To Do
-----
- re-write in bash (for skillz)
- port to python3 (wtf why am i using python2)


Known Issues
------------
- Possible bug where Tagpy hates on the mp3, possibly because of unicode filename. Not sure. Will keep an eye out.