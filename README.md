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
- put downloads in download folder
- re-write in bash (for skillz)
- port to python3 (wtf why am i using python2)
- workaround non-ascii characters in YouTubeDL


Known Issues
------------
- Currently uses most recently modified file to edit ID3 tags which could lead to the wrong file being edited
- YouTubeDL freaks out when it encounters a non-ASCII character and the developer won't fix it