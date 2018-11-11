# Google
import requests
import json


# query = 'Bloomberg'


def search_news(query):
# query = 'Bloomberg'
    date_commence = '2018-10-13'
    return_list = []

    url = ('https://newsapi.org/v2/everything?q=' + query
           + '&from=' + date_commence + '&sortBy=publishedAt&apiKey=70a3c3dd20b04b019739578c4ad22c14')

    response = requests.get(url)
    # content = response.json()['articles']
    content = response.json()['articles']
    # print(content)
    # print(type(content))

    print('Check point 2')

    # content is the list of articles

    if len(content) > 0:
        to_keep_keys = ['title', 'description', 'url', 'publishedAt', 'content']
        unwanted = set(content[0].keys()) - set(to_keep_keys)
        # print(unwanted)
        for i in range(len(content)):
            for unwanted_key in unwanted:
                del content[i][unwanted_key]
            # print(content[i])

            for k, v in content[i].items():
                # print(k, v)
                if v is not None and query in v:
                    del content[i]['content']
                    # print('Here')

                    return_list.append(content[i])

                    break

        print('Check point 3')
        # print(return_list)

        if len(return_list) > 0:
            return [1, return_list]
        else:
            return [0, 'No articles found over past month.']

    else:
        return [0, 'No articles found over past month.']
