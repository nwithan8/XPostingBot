#!/usr/bin/python

import praw
import re
from prawcore import NotFound

mention = "u/XPostingBot"

reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='XPostingBot (by u/grtgbln)',
                     username='XPostingBot',
                     password='')
if reddit.read_only == False:
    print("Connected and running.")

def reply(workedsubs,failedsubs,where):
    fail = ""
    done = ""
    if workedsubs:
        done = "Okay, I crossposted this in "
        for donesub in workedsubs:
            done = done + str(donesub) + " and "
        if done == "":
            done = ""
        else:
            done = done[:-5] + "."
    if failedsubs:
        fail = "Sorry, seems like "
        for failsub in failedsubs:
            fail = fail + str(workingsub) + " and "
        if fail == "":
            fail = ""
        else:
            fail = fail[:-4]
            if len(failedsubs) > 1:
                fail = fail + "do not exist."
            else:
                fail = fail + "does not exist."
    if done and fail:
        where.reply(str(done) + "\n" + str(fail))


def xpost(subs, where):
    originalpost = where.submission
    newtitle = "(X-Post r/" + str(originalpost.subreddit.display_name) + ") " + originalpost.title
    #print("New post: " + str(newtitle))
    link = "https://www.reddit.com" + str(originalpost.permalink)
    workedsubs = []
    failedsubs = []
    wasError = False
    for workingsub in subs:
        exists = True
        try:
            reddit.subreddits.search_by_name(workingsub[2:], exact=True)
        except NotFound:
            exists = False
        if exists == True:
            subreddit = reddit.subreddit(workingsub[2:])
            try:
                subreddit.submit(newtitle, url=link, resubmit=True, send_replies=False)
                workedsubs.append(str(workingsub))
                print("Posting: " + str(newtitle) + " to " + str(workingsub))
            except praw.exceptions.APIException:
                wasError = True
                break
        else:
            failedsubs.append(str(workingsub))
    if not wasError:
        reply(workedsubs,failedsubs,where)
    else:
        response = ""
        if workedsubs:
            response = "I was able to crosspost in "
            for i in workedsubs:
                response = response + str(i) + " and "
            response = response[:-5] + ", but I was rate-limited on the others."
            print(response)
        else:
            response = "Sorry, I was rate-limited, and I couldn't post."
            print(response)
        where.reply(str(response) + " Make sure to give me karma to prevent that in the future.")

def process(text, where):
    subs = re.findall(r'\br/\w+', text)
    if subs:
        xpost(subs, where)

def main():
    for item in reddit.inbox.unread():
        if mention in item.body:
            text = item.body
            print(text)
            process(text, item)
        item.mark_read()

while True:
    main()
