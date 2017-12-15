import subprocess
import json
import sys

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
            cut_video(str(clip_index), start_time, end_time)

    if 'thumbnails' in json_log_data:
        thumbnails = json_log_data['thumbnails']

        for thumbnail_index in range(len(thumbnails)):
            thumbnail_time = thumbnails[thumbnail_index]['thumbnail_time']
            cut_thumbnail(str(thumbnail_index), thumbnail_time)    

    if 'gifs' in json_log_data:
        gifs = json_log_data['gifs']

        for gif_index in range(len(gifs)):
            end_time = gifs[gif_index]['end_time']
            start_time = gifs[gif_index]['start_time']
            cut_gif(str(gif_index), start_time, end_time)
        


if __name__ == '__main__':
    input_val_len = len(sys.argv)

    if(input_val_len is 3):
        path_init(None, sys.argv[1], sys.argv[2])
    elif(input_val_len is 4):
        path_init(sys.argv[1], sys.argv[2], sys.argv[3])

    main()
