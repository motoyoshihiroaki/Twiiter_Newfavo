#!/usr/bin/env python
# coding: utf-8

import time
import datetime
import random

import requests
import tweepy
import schedule
import json

import settings

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN = settings.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = settings.ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
API = tweepy.API(auth)

now = datetime.datetime.now()

# slackにエラーを通知する関数
def slack_to_error(error):
    WEB_HOOK_URL = settings.WEB_HOOK_URL
    requests.post(WEB_HOOK_URL, data=json.dumps({
        "text" : str(error),
        "icon_emoji" : ":fire:",
        "username" : "エラー報告"
    }))

# slackに動作報告をする関数
def slack_to_message():
    SLACK_OPERATION_REPORT = settings.SLACK_OPERATION_REPORT
    activate_time = now.strftime('%Y年%m月%d日 %H:%M')
    message = f'Twitter-NewFavo Activate : {activate_time}'
    requests.post(SLACK_OPERATION_REPORT, data=json.dumps({
        "text" : message,
        "icon_emoji" : ":sunny:",
        "username" : "動作報告"
    }))

def favorite_tweet(search_list):

    # いいね件数
    FAB_COUNT = random.choice(range(3, 5))

    try:
        # ツイート上位100件を検索
        tweet_list = API.search(q=search_list, count=100)

        # 現状フォロワーのID取得後リストを作成
        # my_followers_ids = API.followers_ids("ses_web_create")

        user_ids_for_add = []
        for tweet in tweet_list:
            """いいねリスト除外条件

            ・既存フォロワー
            ・ターゲットのフォロワーが200人以下
            """
            user = tweet.user
            user_ids_for_add.append(user.id)

        cnt = 0
        error_list = []
        for tweet in tweet_list:
            user = tweet.user
            if ( user.id in user_ids_for_add ):
                try:
                    API.create_favorite(id=tweet.id)
                    cnt += 1
                    # 待機時間
                    time.sleep(random.randint(50, 110))
                    if ( cnt==FAB_COUNT ):
                        break
                except tweepy.TweepError as tweepy_error:
                    if len(error_list) < 5:
                        error_list.append(tweepy_error)
                        pass
                    else:
                        break

                except Exception as e:
                    if len(error_list) < 5:
                        error_list.append(e)
                        pass
                    else:
                        break
        if error_list :
            slack_to_error(error_list)    
    except Exception as e:
        slack_to_error(e)


def main():
    slack_to_message()

    # 検索をかけるツイート文章
    SEARCH_LIST = ['IT', 'ブログ書', 'AI','初心者', '読書']
    
    for word in SEARCH_LIST:
        tmp_list = [word]
        favorite_tweet(tmp_list)
    return

if __name__=="__main__":
    print("Scheduling ... ")
    for i in range(8, 24, 1):
        schedule.every().day.at("{:02d}:19".format(i)).do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)