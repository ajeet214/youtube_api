import requests
import json
from modules.sentiment import SentimentAnalysis
import time
from modules.base_api import BaseApi
from credentials import creds


class YoutubeApi(BaseApi):

    # key = "AIzaSyCqXymDa4M2vvrtS3v4l7dn7uIODNNAGRU"
    def _get_credentials(self):
        # change url as per credentials reequired
        url = "http://credsnproxy/api/v1/google"
        try:
            req = requests.get(url=url)
            if req.status_code != 200:
                raise ValueError
            return req.json()
        except:
            # return fallback object
            return {
                "email": creds['email'],
                "password": creds['password'],
                "api_key": creds['google_api_key'],
                "proxy_host": "185.193.36.122",
                "proxy_port": "23343"
            }

    def __init__(self):

        self.obj = SentimentAnalysis()
        self.key = self._get_credentials()['api_key']
        self.neg_count = 0
        self.neu_count = 0
        self.pos_count = 0
        self.url = "https://www.googleapis.com/youtube/v3/search?q=%s&key=%s&part=id,snippet&maxResults=40"
        self.social = "youtube"
        BaseApi.__init__(self, social=self.social)
        self.result_list = []

    def data_processor(self, i):
        # print(i)
        new_dict = dict()

        new_dict['polarity'] = i['polarity']
        new_dict['content'] = i['snippet']['description']
        if not new_dict['content']:
            new_dict['content'] = None
        new_dict['title'] = i['snippet']['title']
        new_dict['author_name'] = i['snippet']['channelTitle']
        new_dict['author_userid'] = i['snippet']['channelId']

        new_dict['author_url'] = 'https://www.youtube.com/channel/{}'.format(new_dict['author_userid'])
        new_dict['datetime'] = int(time.mktime(time.strptime(i['snippet']['publishedAt'][:-5].replace('T', ' '),
                                                              '%Y-%m-%d %H:%M:%S'))) - time.timezone
        new_dict['thumbnail'] = i['snippet']['thumbnails']['high']['url']

        try:
            new_dict['postid'] = i['id']['videoId']
            new_dict['url'] = 'https://www.youtube.com/watch?v={}'.format(new_dict['postid'])
            new_dict['type'] = 'video'
        except:
            new_dict['postid'] = None
            new_dict['url'] = None
            new_dict['type'] = 'page'

        self.result_list.append(new_dict)

        # new_dict['polarity'] = i['polarity']
        # try:
        #     new_dict['post_id'] = i['id']['videoId']
        #     new_dict['post_url'] = 'https://www.youtube.com/watch?v={}'.format(new_dict['post_id'])
        #
        # except:
        #     pass
        # new_dict['post_content'] = i['snippet']['description']
        # new_dict['post_title'] = i['snippet']['title']
        # new_dict['profile_name'] = i['snippet']['channelTitle']
        # new_dict['profile_id'] = i['snippet']['channelId']
        # new_dict['profile_url'] = 'https://www.youtube.com/channel/{}'.format(new_dict['profile_id'])
        # new_dict['post_time'] = int(time.mktime(time.strptime(i['snippet']['publishedAt'][:-5].replace('T', ' '),
        #                                                       '%Y-%m-%d %H:%M:%S'))) - time.timezone
        # new_dict['post_image'] = i['snippet']['thumbnails']['high']['url']
        # self.result_list.append(new_dict)

    def searchApi(self, query, stype=None):
        data = self.get_request(url=self.url % (query, self.key))
        # print(data)
        parsed = json.loads(data.decode())
        # print(parsed['items'])
        for item in parsed['items']:
            # print(item['snippet']['description'])
            pol = self.obj.analize_sentiment(item['snippet']['description'])

            item['polarity'] = pol
            if pol == 1:
                item['polarity'] = 'positive'
                self.pos_count += 1
            elif pol == 0:
                item['polarity'] = 'neutral'
                self.neu_count += 1
            else:
                item['polarity'] = 'negative'
                self.neg_count += 1
            self.data_processor(item)

        ps = self.pos_count
        ng = self.neg_count
        nu = self.neu_count
        total = ps + ng + nu

        sentiments = dict()
        sentiments["positive"] = ps
        sentiments["negative"] = ng
        sentiments["neutral"] = nu

        return {'data':
                {
                    'results': self.result_list,
                    'sentiments': sentiments,
                    'total': total
                 }
                }


if __name__ == '__main__':

    youtube = YoutubeApi()
    print(youtube.searchApi('miller'))
