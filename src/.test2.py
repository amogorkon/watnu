import requests

query = requests.head("https://github.com/amogorkon/fuzzylogic/blob/master/src/fuzzylogic/functions.py")
# url_time = query.headers['last-modified']
# url_date = parsedate(url_time)
print(query.text)
