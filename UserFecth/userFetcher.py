# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     userFetcher
   Description :
   Author :       qiuqiu
   date：          2019/7/21
-------------------------------------------------
"""
import json
import os
import re
import urllib

import requests

HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
}

def get_real_address(url):
    if url.find('v.douyin.com') < 0: return url
    res = requests.get(url, headers=HEADERS, allow_redirects=False)
    return res.headers['Location'] if res.status_code == 302 else None

def get_dytk(url):
    res = requests.get(url, headers=HEADERS)
    if not res: return None
    dytk = re.findall("dytk: '(.*)'", res.content.decode('utf-8'))
    if len(dytk): return dytk[0]
    return None

def download_user_videos(url):
    url = get_real_address(url)
    print("real url:", url)
    number = re.findall(r'share/user/(\d+)', url)
    print('抖音ID',number)
    if not len(number): return
    dytk = get_dytk(url)
    print(dytk)
    download_user_media(number, dytk, url)

def generateSignature(value):
    p = os.popen('node fuck-byted-acrawler.js %s' % value)
    return p.readlines()[0]

def download_user_media(user_id, dytk, url):
    if not user_id:
        print("Number %s does not exist" % user_id)
        return
    hostname = urllib.parse.urlparse(url).hostname
    signature = generateSignature(str(user_id))
    user_video_url = "https://%s/aweme/v1/aweme/post/" % hostname
    user_video_params = {
        'user_id': str(user_id),
        'count': '21',
        'max_cursor': '0',
        'aid': '1128',
        '_signature': signature,
        'dytk': dytk
    }
    max_cursor, video_count = None, 0
    while True:
        if max_cursor:
            user_video_params['max_cursor'] = str(max_cursor)
        res = requests.get(user_video_url, headers=HEADERS, params=user_video_params)
        contentJson = json.loads(res.content.decode('utf-8'))
        print(contentJson)
        aweme_list = contentJson.get('aweme_list', [])
        for aweme in aweme_list:
            video_count += 1
            # self._join_download_queue(aweme, target_folder)
        if contentJson.get('has_more'):
            max_cursor = contentJson.get('max_cursor')
        else:
            break

if __name__ == "__main__":
    url = "http://v.douyin.com/2T4Jhd/"

    download_user_videos(url)
