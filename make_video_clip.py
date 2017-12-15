import subprocess
import json
import sys

PATH = {"FFMPEG" : '',
	"INPUT_FILE" : '',
	"OUTPUT_FILE" : '',
	"OUTPUT_FORMAT" : '',
	"JSON_FILE" : ''}


def path_init(ffmpeg_path, input_video, json_file):
    if(ffmpeg_path is None):
        PATH["FFMPEG"] = 'ffmpeg'
    else:
        PATH["FFMPEG"] = ffmpeg_path
    PATH["INPUT_FILE"] = input_video
    PATH["OUTPUT_FILE"] = PATH["INPUT_FILE"].split('.')[0] + '_clip_'
    PATH["OUTPUT_FORMAT"] = '.' + PATH["INPUT_FILE"].split('.')[1]
    PATH["JSON_FILE"] = json_file


def cut_video(clip_index, start_time, end_time):
    command = PATH["FFMPEG"] + ' -i '+PATH["INPUT_FILE"]+' -c copy -ss ' + start_time + ' -to '+end_time+' '+PATH["OUTPUT_FILE"]+clip_index+PATH["OUTPUT_FORMAT"]
    subprocess.call (command, shell=True)


def main():
    with open(PATH["JSON_FILE"]) as data_file:
        json_log_data = json.load(data_file)

    clips = json_log_data['clips']

    for clip_index in range(len(clips)):
        end_time = clips[clip_index]['end_time']
        start_time = clips[clip_index]['start_time']
        cut_video(str(clip_index), start_time, end_time)


if __name__ == '__main__':
    input_val_len = len(sys.argv)

    if(input_val_len is 3):
        path_init(None, sys.argv[1], sys.argv[2])
    elif(input_val_len is 4):
        path_init(sys.argv[1], sys.argv[2], sys.argv[3])

    main()
