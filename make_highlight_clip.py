%pyspark
import os
import sys
import json
import datetime
import subprocess
from pyspark.sql import SparkSession

# initialize spark session
spark = SparkSession \
    .builder \
    .appName("Python Spark SQL basic example") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()

def make_clips_to_dict(clip_list):
    '''
    Make clips from clip rankings
    highlight number = clip_number
    highlight duration = 1 minute
    '''
    clips = {"clip_number": 3, "clips": []}
    for clip in clip_list[:clips["clip_number"]]:
        clip_start_time = "%02d:%02d:%02d" % (clip[0], clip[1], 0)
        clip_end_time = "%02d:%02d:%02d" % (clip[0], clip[1]+1, 0)
        clips["clips"].append({"start_time":clip_start_time, "end_time":clip_end_time})

    return clips

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python3 get_highlight_json.py [Date] [Content number]')
        sys.exit()
    elif len(sys.argv) < 3:
        content_number = 1
    else:
        content_number = int(sys.argv[2])

    # read and create bookmark table
    bookmark_path = "/data/pooq-ods/"+sys.argv[1]+"/"+sys.argv[1]+"_*_bookmark.csv"
    bookmark = spark.read.csv(bookmark_path)
    #bookmark = spark.read.csv("/data/pooq-ods/20170101/20170101_*_bookmark.csv")
    bookmark.createOrReplaceTempView("bookmark")
    #bookmark.show()

    # read and create live table
    live_content = spark.read.csv('/data/pooq-ods/content/live.csv')
    live_content.createOrReplaceTempView("content")
    #live_content.show()

    # read and create movie table
    movie_content = spark.read.csv('/data/pooq-ods/content/movie.csv')
    movie_content.createOrReplaceTempView('movie')
    #movie_content.show()

    # read and create vod table
    vod_content = spark.read.csv('/data/pooq-ods/content/vod.csv')
    vod_content.createOrReplaceTempView('vod')
    #vod_content.show()

    # read and create member table
    member = spark.read.csv('/data/pooq-ods/member/member.csv')
    member.createOrReplaceTempView('member')
    #member.show()

    # Get Program contentID
    sql = spark.sql("SELECT first_value(vod._c1) AS ContentId FROM bookmark, vod WHERE bookmark._c5 LIKE 'V' AND bookmark._c7=vod._c1 GROUP BY vod._c3 ORDER BY COUNT(DISTINCT bookmark._c4) DESC")
    result = sql.collect()
    contents = []

    # Pick up just top1 content's id
    for content in result[:content_number]:
        contents.append(content[0])
    # print(len(contents))

    # save to json file(top 1 contents viewers : {uno:mediatime} )
    for content_id in contents:
        query = "SELECT bookmark._c4 AS user, bookmark._c9 AS mediaTime FROM bookmark WHERE bookmark._c5 LIKE 'V' AND bookmark._c7 LIKE " + "'" + content_id + "'"
        bookmarks = spark.sql(query)
        bookmarks.createOrReplaceTempView('contentbookmarks')
        #bookmarks.show()

        # Choose highlight by count of logs.
        # highlight dutation is 1 minute.
        query = "SELECT hour(mediaTime) AS start_time_hour,FLOOR(minute(mediaTime)/1) AS start_time_minute, COUNT(*) AS count FROM contentbookmarks GROUP BY hour(mediaTime), FLOOR(minute(mediaTime)/1) ORDER BY count DESC"
        clip_list = spark.sql(query)
        clips = clip_list.collect()

        json_path = './json/'+content_id+'.json'
        with open(json_path, 'w') as fp:
            json.dump(make_clips_to_dict(clips), fp)
        #sql.write.format('json').save('/data/pooq-ods/output/'+content_id)

        # call shell script file to make cilp video
        cmd = 'sh ./make_video_clip.sh ./videos/' + content_id + '.mp4 ' + json_path
        subprocess.call([cmd])
