# pip install praw youtube_dl requests

import os
import sys
import argparse

import praw
import prawcore
import json
from pathlib import Path
import requests

import youtube_dl

config = json.load(open('./config/config.json', 'r'))
reddit = praw.Reddit(client_id=config['clientId'],
                     client_secret=config['clientSecret'],
                     user_agent=config['userAgent'])
max_title_len = 150

# optional
class MyLogger(object):
    def warning(self, msg):
        pass

    def debug(self, msg):
        print(msg)

    def error(self, msg):
        pass


def create_download_folder():
    p = Path(f'./download')
    if not p.exists():
        os.makedirs(f'./download')


def shorten_title(title):
    if len(title) > max_title_len:
        return title[:max_title_len]
    return title


def download_content(time, limit, subreddits):
    create_download_folder()
    time = time
    limit = limit
    subreddits = subreddits
    for s in subreddits:
        sub = reddit.subreddit(s)
        try:
            # you can get hot, best as well
            for submission in sub.top(time, limit=limit):
                title = submission.title
                title = shorten_title(title)
                ydl_opts = {
                    'download_archive': 'downloaded.txt',
                    'outtmpl': f'./download/{sub.display_name}/{title}.%(ext)s',
                    'logger': MyLogger(),
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    try:
                        ydl.download([submission.url])
                    except youtube_dl.utils.DownloadError as download_error:
                        # external media
                        if 'No Media found' in str(download_error):
                            pass
                        else:
                            print('Image Downloading')
                            # creating new subreddit folder
                            p = Path(f'./download/{sub.display_name}')
                            if not p.exists():
                                os.makedirs(f'./download/{sub.display_name}')
                            url = submission.url
                            #print(f'img url : {url}')
                            # modify to retrieve img
                            if 'i.imgur' not in url and 'imgur' in url:
                                url = url.replace('imgur', 'i.imgur')
                                url += '.jpg'
                            file_ext = url.split('.')[-1]
                            # download image and write to file
                            img_req = requests.get(url)
                            #print(file_ext, title)
                            with open(f'./download/{sub.display_name}/{title}.{file_ext}', 'wb') as f:
                                f.write(img_req.content)

        except prawcore.exceptions.Redirect:
            print(f'Skipping r/{sub} as it does not exist')
        except:
            print('Oops, something went wrong, help')
            print(sys.exc_info()[0])


def getArguments():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-s",  "--sub", nargs='+',
                           help="The Name of subreddits needed to download separated by spaces", type=str, required=True)
    argParser.add_argument(
        "-l", "--limit", help="Entering the limit of the top comments like enter '25' for top 25 comments", type=int, required=True)
    argParser.add_argument(
        "-t", "--time", help="Entering the time of the top comments like 'all, week, day, time, month'", type=str, required=True)
    args = vars(argParser.parse_args())

    return {"time": args['time'], "subReddit": args['sub'], "limit": args['limit']}


if __name__ == '__main__':
    args = getArguments()
    download_content(args['time'], args['limit'], args['subReddit'])
    print('Done')
