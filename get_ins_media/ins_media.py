#coding:utf-8

import requests
import json
from lxml import etree
import flask
from flask import jsonify
from flask import request
from flask import render_template
from furl import furl

header = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'cookie': 'shbid=4419; rur=PRN; mcd=3; mid=W1E7cAALAAES6GY5Dyuvmzfbywic; csrftoken=uVspLzRYlxjToqSoTlf09JVaA9thPkD0; urlgen="{\"time\": 1532050288\054 \"2001:da8:e000:1618:e4b8:8a3d:8932:2621\": 23910\054 \"2001:da8:e000:1618:6c15:ccda:34b8:5dc8\": 23910}:1fgVTv:SfLAhpEZmvEcJn0037FXFMLJr0Y"',
    'referer': 'https://www.instagram.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}


class Media:
    def __init__(self, url, media_type):
        self.url=url
        self.type=media_type

server = flask.Flask(__name__)
@server.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@server.route('/getInsMedia', methods=['post'])
def getInsMedia():
    url = request.form['url']

    if url:
        try:
            media_list = main(url)
        except:
            return render_template('index.html',tip="tip: incorrect url or network error")
        else:
            return render_template('index.html',media_list=media_list)
    else:
        return render_template('index.html',tip="tip: please enter url")

def main(url):
    media_list = []
    
    r = requests.get(url, headers = header)
    selector = etree.HTML(r.content)

    #获取页面脚本并转成json格式，分析页面资源情况
    script = selector.xpath('/html/body/script[1]')[0]
    scr_json = json.loads(script.text[21:-1])

    #判断网页中资源类型
    media_info = scr_json['entry_data']["PostPage"][0]["graphql"]["shortcode_media"]

    if media_info["__typename"] == "GraphImage":
        for_single_pic(media_info, media_list)

    elif media_info["__typename"] == "GraphSidecar":
        for_multi_media(media_info, media_list)

    elif media_info["__typename"] == "GraphVideo":
        for_single_video(media_info, media_list)
    
    return media_list


def for_single_pic(media_info, media_list):
    
    url = media_info['display_url'].strip()
    
    media_list.append(Media(url,"image"))


def for_multi_media(media_info, media_list):

    urls = media_info['edge_sidecar_to_children']['edges']

    for i in range(len(urls)):

        node = urls[i]['node']

        if node['__typename'] == 'GraphImage':

            url = node['display_url'].strip()

            media_list.append(Media(url,"image"+str(i)))


        elif node['__typename'] == 'GraphVideo':

            url = node['video_url'].strip()

            media_list.append(Media(url,"video"+str(i)))

        else:
            pass


def for_single_video(media_info, media_list):    

    url = media_info['video_url'].strip()

    media_list.append(Media(url,"video"))


if __name__ == '__main__':
    server.run(debug=True, port=2333, host='0.0.0.0')
