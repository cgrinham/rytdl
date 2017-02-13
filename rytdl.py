# -*- coding: utf-8 -*-
"""
Subreddit YouTube Mp3 Downloader
Some notes:
Setting a filename through youtubedl caused corruption in some files
Move file to output directory after download because I don't want to piss off youtubedl
"""

from __future__ import unicode_literals
import re
import os
import time
import argparse
import youtube_dl
import praw
import tagpy
import yaml

def logerror(error):
    print error
    with open('errors.log', 'a') as errorlog:
        errorlog.write("%s\n" % error)

def write_settings(data):
    """Write the previous image to settings file"""
    print "Writing settings..."
    with open('settings.yml', 'w') as outfile:
        outfile.write(yaml.dump(data, default_flow_style=True))

def read_settings():
    """ Read settings from YAML file"""
    print "Read settings..."
    try:
        return yaml.load(open("settings.yml"))
    except:
        print "Could not read settings"
        print "Please use the -i flag to run RYTDL setup"
        return None

def extract_song_details(title):
    # Get artist and track name from submission title
    try:
        matches = re.match(r'(.*) - (.*)', title)
        trackartist = matches.group(1)
        tracktitle = matches.group(2)
        filename = "%s - %s.mp3" % (trackartist, tracktitle)
    except AttributeError:
        print "Improperly formatted title, will attempt other formatting"

        try:
            matches = re.match(r'(.*)- (.*)', title)
            trackartist = matches.group(1)
            tracktitle = matches.group(2)
            filename = "%s - %s.mp3" % (trackartist, tracktitle)
        except AttributeError:
            try:
                matches = re.match(r'(.*) – (.*)', title)
                trackartist = matches.group(1)
                tracktitle = matches.group(2)
                filename = "%s - %s.mp3" % (trackartist, tracktitle)
            except AttributeError:
                # If can't process title, just set filename to submission title
                print "Improperly formatted title, ID3 tags will not be completed"
                trackartist = ""
                tracktitle = ""
                filename = ""

                #logerror(title)
    return filename, trackartist, tracktitle

def get_tracks(subreddit, genre, outputdir, sort, submissionslimit=40):
    print "Downloading submissions from /r/%s" % subreddit
    # Get previously downloaded IDs
    idlist = []

    with open('idlist.txt', 'r') as idlistfile:
        idlist = [line.strip() for line in idlistfile]

    settings = read_settings()

    # Create reddit instance
    reddit = praw.Reddit(client_id=settings["client_id"],
                         client_secret=settings["client_secret"],
                         user_agent=settings["user_agent"])

    if sort == "hot":
        print "Sort submissions by 'hot'"
        submissions = reddit.get_subreddit(subreddit).get_hot(limit=submissionslimit)
    elif sort == "alltime":
        print "Sort submissions by 'Top from All Time'"
        submissions = reddit.get_subreddit(subreddit).get_top_from_all(limit=submissionslimit)
    elif sort == "month":
        print "Sort submissions by 'Top from the past Month'"
        submissions = reddit.get_subreddit(subreddit).get_top_from_month(limit=submissionslimit)
    else:
        print "No sort"

    # Create lists of links
    ytlist = []
    sclist = [] # for future soundcloud downloading
    otherlist = []

    for submission in submissions:
        if submission.url.startswith('https://www.youtube.com') is True:
            ytlist.append(submission)
        elif submission.url.startswith('https://soundcloud.com') is True:
            sclist.append(submission)
        else:
            otherlist.append(submission)

    # Set YouTubeDL options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl' : 'tmp.%(ext)s',
    }

    # Download videos as MP3 and edit ID3 Tags
    for video in ytlist:
        if video.id not in idlist:
            print "Processing %s" % video.title
            
            filename, trackartist, tracktitle = extract_song_details(video.title)

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print "Downloading %s" % video.title
            
                # Actually download the video
                try:
                    ydl.download([video.url])

                    currentfile = "tmp.mp3"

                    # If possible set proper ID3 tags otherwise just set title to title
                    if trackartist != "":
                        #print "Set ID3 tags"
                        # Set artist/track title/genre
                        audiofile = tagpy.FileRef(str(currentfile))
                        audiofile.tag().artist = trackartist
                        audiofile.tag().album = tracktitle
                        audiofile.tag().title = tracktitle
                        audiofile.tag().genre = genre.title()
                        audiofile.tag().comment = "RYTDL YouTube Rip"
                        # Save file
                        audiofile.save()
                    else:
                        audiofile = tagpy.FileRef(str(currentfile))
                        audiofile.tag().title = video.title
                        audiofile.save()

                    # Rename the mp3
                    if filename == "":
                        filename = "%s.mp3" % currentfile[:-16]
                    # Replace slashes with underscores to avoid os errors
                    filename = filename.replace('/', '_')

                    print filename
                    # Check for overly long filename and correct
                    if len(filename) > 50:
                        print "Filename too long"
                        filename = "%s.mp3" % filename[:50]
                        print "New filename %s" % filename

                    print os.path.join(os.getcwd(), currentfile)
                    try:
                        os.rename(currentfile, filename)
                    except OSError, e:
                        print e
                        logerror("File not found error, retrying")
                        time.sleep(5)
                        os.rename(os.path.join(os.getcwd(), currentfile), os.path.join(os.getcwd(), filename))

                    # move file to output directory
                    if not os.path.exists(outputdir):
                        os.makedirs(outputdir)
                    # In python3 can do: os.makedirs(path, exist_ok=True)
                    os.rename(filename, os.path.join(os.getcwd(), outputdir, filename))

                    # Append submission id to file
                    with open("idlist.txt", "a") as idlistfile:
                        idlistfile.write("\n")
                        idlistfile.write(video.id)
                    print "Submission successfully downloaded"
                    print ""
                except youtube_dl.utils.DownloadError:
                    print "Video not available"
                    print ""
        else:
            print "Submission %s already downloaded, skipping" % video.id

    # Clean up
    if os.path.exists("tmp.mp3"):
        os.remove("tmp.mp3")

if __name__ == "__main__":

    print "RYTDL"
    print ""

    # Set up CLI arguments
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("-i", "--setup", help="Set up RYTDL with your developer account details",
                        action="store_true")
    PARSER.add_argument("-s", "--subreddit",
                        help="Specify the subreddit to fetch submissions from", default="")
    PARSER.add_argument("-g", "--genre", help="Choose Genre tag to be added to MP3s", default="")
    PARSER.add_argument("-n", "--submissions", type=int,
                        help="Pick number of submissions to fetch (default 40)", default=40)
    PARSER.add_argument("-o", "--outputdir", help="Specify output directory", default="downloads")
    PARSER.add_argument("-t", "--top", help="Get top submissions from all time",
                        action="store_true")
    PARSER.add_argument("-m", "--month", help="Get top submissions from all the past month",
                        action="store_true")


    ARGS = PARSER.parse_args()

    if ARGS.setup is True:
        SETTINGS = {}
        print "Set up"
        print "Enter your Reddit Client ID:"
        SETTINGS["client_id"] = raw_input()
        print "Enter your client secret:"
        SETTINGS["client_secret"] = raw_input()
        SETTINGS["user_agent"] = "python:rytdl:v2017.01.21 (by /u/christophski)"
        write_settings(SETTINGS)
    else:
        if ARGS.subreddit == "":
            print "Please specify a subreddit using the -s (--subreddit) flag"
        else:
            if ARGS.top is True:
                SORTSUB = "alltime"
            elif ARGS.month is True:
                SORTSUB = "month"
            else:
                SORTSUB = "hot"
            try:
                get_tracks(ARGS.subreddit, ARGS.genre, ARGS.outputdir, SORTSUB, ARGS.submissions)
            except praw.errors.InvalidSubreddit:
                print "Invalid Subreddit"
