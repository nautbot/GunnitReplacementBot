#!/usr/bin/env python
import datetime
import json
import re
import string
import os

import praw
import prawcore
import prawcore.exceptions


loggingEnabled = True
username = os.environ['USERNAME']
prefix = str(os.environ['PREFIX']).strip().lower()
processed = []


# Console reporting commands
def getTimeStamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def logAppEvent(message, e=None):
    if loggingEnabled:
        if e is None:
            print("{} - {}".format(getTimeStamp(), message))
        else:
            print("{} - {}: {}".format(getTimeStamp(), message, e))


r = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    redirect=os.environ['REDIRECT'],
    username=os.environ['USERNAME'],
    password=os.environ['PASSWORD'],
    user_agent=os.environ['USER_AGENT']
)
logAppEvent('Logged in to reddit as: ' + os.environ['USERNAME'])


def hasReply(comment):
    for reply in comment.replies:
        if reply.author.name.lower() == username.lower():
            return True
    return False


def getCommands(r):
    try:
        sub = r.subreddit(os.environ['CONFIG_SUB'])
        wiki = sub.wiki[os.environ['CONFIG_WIKI_PAGE']]
        wikiLines = str(wiki.content_md).split('\r\n')
        commands = {}
        for line in wikiLines:
            if line == '': continue
            values = line.split(';')
            keys = values[0].split(',')
            for key in keys:
                commands[key] = str(values[1]).strip(' \t\n\r')
        return commands
    except Exception as e:
        logAppEvent('getCommands', e)
        pass


def respond(comment, r):
    try:
        comment.refresh()
        responses = []
        for key,value in getCommands(r).items():
            regex = re.compile(r'\b' + key.lower() + r'\b')
            found = re.findall(regex, comment.body.lower())
            if len(found) != 0:
                responses.append(value)
        if len(responses) != 0 and not hasReply(comment):
            comment.reply('\n\n'.join(responses))
    except Exception as e:
        logAppEvent('respond', e)
        pass


def scanComments():
    global processed
    try:
        commentLimit = int(os.environ['COMMENT_LIMIT'])
        subreddits = os.environ['SUBREDDITS']
        for comment in r.subreddit(subreddits).comments(limit=commentLimit):
            if (
                    comment in processed
                    or comment.author is None
                    or hasReply(comment)
                ):
                continue
            if prefix in comment.body.lower():
                respond(comment, r)
            processed.append(comment)
            if len(processed) > commentLimit:
                processed = processed[(len(processed) - commentLimit):]
    except Exception as e:
        logAppEvent('scanComments', e)
        pass


while True:
    try:
        scanComments()
    except Exception as e:
        logAppEvent('main', e)
        pass