import redis
import re


r = redis.StrictRedis(host='localhost', port=6379, db=0)

def get_artist_most_weeks_in_first_in_a_row():
    result = r.zrevrange('weeksInFirstPlace', 0, 0, withscores=True)
    artist = result[0][0]
    weeks = result[0][1]

    if ';' in artist:
        artist = re.search(r'.+?(?=;)', artist).group(0)

    print '{} has been in first for {} weeks in a row!'.format(artist, weeks)

def get_list_artists_weeks_on_top_10():
    list = r.zrevrange('weeksOnTop10',0,-1,withscores=True)
    for item in list:
        print '{} has been {} weeks on the top 10 list!'.format(item[0],item[1])
