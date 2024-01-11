# coding=utf-8
import os
import sys
import json
import pygame
from shuttleai import *

# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib3
    from urllib import quote_plus
    from urllib3 import urlopen
    from urllib3 import Request
    from urllib3 import URLError
    from urllib import urlencode

# 替换你的 API_KEY
API_KEY = ''

# 替换你的 SECRET_KEY
SECRET_KEY = ''





TTS_URL = 'http://tsn.baidu.com/text2audio'

"""  TOKEN start """

TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'


"""
    获取token
"""
def get_mes():
    # Define the message you want to send to ShuttleAI.
    question=input('请输入你的问题：')
    if question in ['结束','退出','']:
        exit()
    messages = [{"role": "user", "content": question}]
    # Use the chat_completion method to send the message to ShuttleAI.
    print("####### Waiting for connection... ##########")
    response = shuttle.chat_completion(
        model="gpt-4",
        messages=messages,
        stream=False,
        plain=False,
        image=None,
        citations=False
    )
    # Print the response received from ShuttleAI.
    message = response['choices'][0]['message']['content']
    #print(message)
    return message

def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'audio_tts_post' in result['scope'].split(' '):
            print ('please ensure has check the tts ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()


"""  TOKEN end """

if __name__ == '__main__':
    # Initialize the ShuttleClient with your API key.
    shuttle = ShuttleClient(api_key="your API key")
    print("######  Initialize successfully #######")
    print("等待百度响应......")
    i=1
    while True:
        # 信息内容文本
        token = fetch_token()
        TEXT = get_mes()
        #print(TEXT)
        print("#######等待百度文字转语音#######")

        tex = quote_plus(TEXT)  # 此处TEXT需要两次urlencode

        params = {'tok': token, 'tex': tex, 'cuid': "quickstart",
                  'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

        data = urlencode(params)

        req = Request(TTS_URL, data.encode('utf-8'))
        has_error = False
        try:
            f = urlopen(req)
            result_str = f.read()

            headers = dict((name.lower(), value) for name, value in f.headers.items())

            has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
        except  URLError as err:
            print('http response http code : ' + str(err.code))
            result_str = err.read()
            has_error = True

        save_file = "error.txt" if has_error else u'tem.mp3'
        save_file=save_file[0:3]+str(i)+save_file[3:]
        with open(save_file, 'wb') as of:
            of.write(result_str)

        if has_error:
            if (IS_PY3):
                result_str = str(result_str, 'utf-8')
            print("tts api  error:" + result_str)

        print("file saved as : " + save_file)
        file='tem'+str(i)+'.mp3'
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        i+=1