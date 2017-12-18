import subprocess
import json
import sys
import datetime

PATH = {"FFMPEG" : '',
	"INPUT_FILE" : '',
	"OUTPUT_CLIP_FILE" : '',
	"OUTPUT_CLIP_FORMAT" : '',
	"OUTPUT_THUMB_FILE" : '',
	"OUTPUT_THUMB_FORMAT" : '',
	"OUTPUT_GIF_FILE" : '',
	"OUTPUT_GIF_FORMAT" : '',
	"JSON_FILE" : ''}


def path_init(ffmpeg_path, input_video, json_file):
    if(ffmpeg_path is None):
        PATH["FFMPEG"] = 'ffmpeg'
    else:
        PATH["FFMPEG"] = ffmpeg_path
    PATH["INPUT_FILE"] = input_video
    PATH["OUTPUT_CLIP_FILE"] = PATH["INPUT_FILE"].split('.')[0] + '_clip_'
    PATH["OUTPUT_CLIP_FORMAT"] = '.' + PATH["INPUT_FILE"].split('.')[1]
    PATH["OUTPUT_THUMB_FILE"] = PATH["INPUT_FILE"].split('.')[0] + '_thumbnail_'
    PATH["OUTPUT_THUMB_FORMAT"] = '.jpg'
    PATH["OUTPUT_GIF_FILE"] = PATH["INPUT_FILE"].split('.')[0] + '_gif_'
    PATH["OUTPUT_GIF_FORMAT"] = '.gif'
    PATH["JSON_FILE"] = json_file


def calculate_gif_time(start_time):
    time_format = '%H:%M:%S'
    time_length = datetime.datetime.strptime(start_time,time_format) + datetime.timedelta(seconds=10)
    secs = time_length.second
    mins = time_length.minute
    hours = time_length.hour
    return str(hours)+':'+str(mins)+':'+str(secs)


def cut_video(clip_index, start_time, end_time):
    command = PATH["FFMPEG"] + ' -i '+PATH["INPUT_FILE"]+' -c copy -ss ' + start_time + ' -to '+end_time+' '+PATH["OUTPUT_CLIP_FILE"]+clip_index+PATH["OUTPUT_CLIP_FORMAT"]
    subprocess.call (command, shell=True)


def cut_thumbnail(thumbnail_index, thumbnail_time):
    command = PATH["FFMPEG"] + ' -i '+PATH["INPUT_FILE"]+' -ss ' + thumbnail_time + ' -vframes 1 '+PATH["OUTPUT_THUMB_FILE"]+thumbnail_index+PATH["OUTPUT_THUMB_FORMAT"]
    subprocess.call (command, shell=True)


def cut_gif(gif_index, start_time, end_time):
    command = PATH["FFMPEG"] + ' -i '+PATH["INPUT_FILE"]+' -ss ' + start_time + ' -to '+end_time+' -vf fps=1 -pix_fmt rgb32 -r 1 '+PATH["OUTPUT_GIF_FILE"]+gif_index+PATH["OUTPUT_GIF_FORMAT"]
    subprocess.call (command, shell=True)


def main():
    with open(PATH["JSON_FILE"]) as data_file:
        json_log_data = json.load(data_file)

    if 'clips' in json_log_data:
        clips = json_log_data['clips']

        for clip_index in range(len(clips)):
            end_time = clips[clip_index]['end_time']
            start_time = clips[clip_index]['start_time']
            gif_end_time = calculate_gif_time(start_time)

            cut_video(str(clip_index), start_time, end_time)
            cut_thumbnail(str(clip_index), start_time)
            cut_gif(str(clip_index), start_time, gif_end_time)
        

if __name__ == '__main__':
    input_val_len = len(sys.argv)

    if(input_val_len is 3):
        path_init(None, sys.argv[1], sys.argv[2])
    elif(input_val_len is 4):
        path_init(sys.argv[1], sys.argv[2], sys.argv[3])

    main()
