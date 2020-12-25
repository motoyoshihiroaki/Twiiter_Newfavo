#!/usr/bin/env python
# coding: utf-8

import time
import datetime
import random

import requests
import tweepy
import schedule

import settings

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN = settings.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = settings.ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
API = tweepy.API(auth)

now = datetime.datetime.now()

# LINEに通知する関数
def line_notice(mess):
    url = "https://notify-api.line.me/api/notify"
    token = settings.LINE_TOKEN
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message": type(mess) + "favo" + "\n" + now.strftime("%H時%M分 Error") + "\n"*2 + str(mess)}
    requests.post(url ,headers = headers ,params=payload)


# 検索をかけるツイート文章
SEARCH_LIST = ['プログラミング', 'ブログ書', 'Webデザイン', '今日の積み上げ', 'ブログ初心者', '読書']
# いいね件数
FAB_COUNT = random.choice(range(3, 5))

def favorite_tweet(api, search_list):
    # ツイート上位100件を検索
    tweet_list = api.search(q=search_list, count=100)

    # 現状フォロワーのID取得後リストを作成
    my_followers_ids = api.followers_ids("ses_web_create")

    user_ids_for_add = []

    # 条件に合うユーザーを除外
    for tweet in tweet_list:
        user = tweet.user
        # print(user.id)
        if ( user.id in my_followers_ids ):
            print("x {} (@{}) は現在フォロワーなので、リスト追加対象外としました。".format(user.name, user.screen_name))
        elif ( (user.followers_count is None) or (user.followers_count <= 200) ):
            print("× {}（@{}）はフォロワーが200人以下なので、リスト追加対象外としました。".format(user.name, user.screen_name))
        elif ( user.id in user_ids_for_add ):
            print("× {}（@{}）は既にリスト追加対象です".format(user.name, user.screen_name))
        else:
            user_ids_for_add.append(user.id)
            print('◯ {}（@{}）をリスト追加対象としました。'.format(user.name, user.screen_name))

    # Favorite
    print("")

    cnt = 0
    for tweet in tweet_list:
        user = tweet.user
        if ( user.id in user_ids_for_add ):
            try:
                status = api.create_favorite(id=tweet.id)
                cnt += 1
                print("\n-------------\n")
                print('「{}」というツイートをいいねしました！'.format(tweet.text))
                # 待機時間
                STOP_TIME = random.randint(50, 110)
                print( STOP_TIME )
                time.sleep( STOP_TIME )
                if ( cnt==FAB_COUNT ):
                    break
            except tweepy.TweepError:
                pass
            except Exception as e:
                pass
                line_notice(e)

    print("")
    return


def main():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    for word in SEARCH_LIST:
        print("[Word: {}]".format(word))
        tmp_list = [word]
        favorite_tweet(api, tmp_list)
    print("favo .. ")
    return


if __name__=="__main__":
    print("Scheduling ... ")
    for i in range(8, 24, 1):
        schedule.every().day.at("{:02d}:19".format(i)).do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)