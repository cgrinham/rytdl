"""
Subreddit YouTube Mp3 Downloader

Some notes:
Setting a filename through youtubedl caused corruption in some files
Move file to output directory after download because I don't want to piss off youtubedl

"""

from __future__ import unicode_literals
import re
import os
import glob
import argparse
import youtube_dl
import praw
import tagpy


def get_tracks(subreddit, genre, outputdir, submissions=40):
    print "Downloading submissions from /r/%s" % subreddit
    # Get previously downloaded IDs
    idlist = []

    with open('idlist.txt', 'r') as idlistfile:
        idlist = [line.strip() for line in idlistfile]

    # Create reddit instance
    reddit = praw.Reddit(client_id='BxvVu9bOc1JaPw',
                         client_secret='',
                         user_agent='python:rytdl:v2017.01.14 (by /u/christophski)')

    # Create lists of links
    ytlist = []
    sclist = []
    otherlist = []

    for submission in reddit.get_subreddit(subreddit).get_hot(limit=submissions):
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
    }

    # Download videos as MP3 and edit ID3 Tags
    for video in ytlist:
        edittags = True
        if video.id not in idlist:
            print "Processing %s" % video.title
            # Get artist and track name from submission title
            matches = re.match(r'(.*) - (.*)', video.title)
            try:
                trackartist = matches.group(1)
                tracktitle = matches.group(2)
                filename = "%s - %s.mp3" % (trackartist, tracktitle)

            except AttributeError:
                print "Improperly formatted title, will attempt other formatting"

                try:
                    matches = re.match(r'(.*)- (.*)', video.title)
                    trackartist = matches.group(1)
                    tracktitle = matches.group(2)
                    filename = "%s - %s.mp3" % (trackartist, tracktitle)

                except AttributeError:
                    # If can't process title, just set filename to submission title
                    print "Improperly formatted title, ID3 tags will not be completed"
                    edittags = False
                    filename = ""
                    with open('errors.log', 'a') as errorlog:
                        errorlog.write("%s\n" % video.title)


            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print "Downloading %s" % video.title
            
                # Actually Ddownload the video
                ydl.download([video.url])

                # Need a better solution because this is hacky af
                # What if something else modifies a file before we access it?
                newest = max(glob.iglob('*.[Mm][Pp]3'), key=os.path.getctime)
                if filename == "":
                    filename = "%s.mp3" % newest[:-16]
                    os.rename(newest, filename)
                else:
                    os.rename(newest, filename)

                # If possible set proper ID3 tags otherwise just set title to title
                if edittags is True:
                    print "Set ID3 tags"
                    # Set artist/track title/genre
                    audiofile = tagpy.FileRef(str(filename))
                    audiofile.tag().artist = trackartist
                    audiofile.tag().album = tracktitle
                    audiofile.tag().title = tracktitle
                    audiofile.tag().genre = genre.title()
                    # Save file
                    audiofile.save()
                else:
                    audiofile = tagpy.FileRef(str(filename))
                    audiofile.tag().title = video.title
                    audiofile.save()

                # move file to output directory
                if not os.path.exists(outputdir):
                    os.makedirs(outputdir)
                # In python3 can do: os.makedirs(path, exist_ok=True)
                os.rename(filename, os.path.join(os.getcwd(), outputdir, filename))

            # Append submission id to file
            with open("idlist.txt", "a") as idlistfile:
                idlistfile.write("\n")
                idlistfile.write(video.id)
            print ""
        else:
            print "Subimssion %s already downloaded, skipping" % video.id

if __name__ == "__main__":

    print "RYTDL"
    print ""

    # Set up CLI arguments
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("subreddit", help="Specify the subreddit to fetch submissions from")
    PARSER.add_argument("-g", "--genre", help="Choose Genre tag to be added to MP3s", default="")
    PARSER.add_argument("-s", "--submissions", type=int,
                        help="Pick number of submissions to fetch (default 40)", default=40)
    PARSER.add_argument("-o", "--outputdir", help="Specify output directory", default="downloads")

    ARGS = PARSER.parse_args()

    try:
        get_tracks(ARGS.subreddit, ARGS.genre, ARGS.outputdir, ARGS.submissions)
    except praw.errors.InvalidSubreddit:
        print "Invalid Subreddit"
        quit()
