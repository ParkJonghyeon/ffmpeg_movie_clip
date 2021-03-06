import subprocess
import json
import sys
import datetime


# path for make_video_clip
PATH = {"FFMPEG": '',
        "INPUT_FILE": '',
        "OUTPUT_CLIP_FILE": '',
        "OUTPUT_CLIP_FORMAT": '',
        "OUTPUT_HIGHLIGHT_FILE": '',
        "OUTPUT_HIGHLIGHT_FORMAT": '',
        "OUTPUT_THUMB_FILE": '',
        "OUTPUT_THUMB_FORMAT": '',
        "OUTPUT_GIF_FILE": '',
        "OUTPUT_GIF_FORMAT": '',
        "JSON_FILE": ''}


# path init
def path_init(ffmpeg_path, input_video, json_file):
    if ffmpeg_path is None:
        PATH["FFMPEG"] = 'ffmpeg'
    else:
        PATH["FFMPEG"] = ffmpeg_path
    PATH["INPUT_FILE"] = input_video
    input_token = PATH["INPUT_FILE"].split('/')
    input_file_name = input_token[len(input_token)-1]
    PATH["OUTPUT_CLIP_FILE"] = './clips/' + input_file_name.split('.')[0] + '_clip_'
    PATH["OUTPUT_CLIP_FORMAT"] = '.' + input_file_name.split('.')[1]
    PATH["OUTPUT_HIGHLIGHT_FILE"] = './clips/' + input_file_name.split('.')[0] + '_highlight'
    PATH["OUTPUT_HIGHLIGHT_FORMAT"] = '.' + input_file_name.split('.')[1]
    PATH["OUTPUT_THUMB_FILE"] = './clips/' + input_file_name.split('.')[0] + '_thumbnail_'
    PATH["OUTPUT_THUMB_FORMAT"] = '.jpg'
    PATH["OUTPUT_GIF_FILE"] = './clips/' + input_file_name.split('.')[0] + '_gif_'
    PATH["OUTPUT_GIF_FORMAT"] = '.gif'
    PATH["JSON_FILE"] = json_file


# Calculate gif file's end time
def calculate_gif_time(start_time):
    time_format = '%H:%M:%S'
    time_length = datetime.datetime.strptime(start_time,time_format) + datetime.timedelta(seconds=10)
    sec = time_length.second
    minute = time_length.minute
    hour = time_length.hour
    return str(hour)+':'+str(minute)+':'+str(sec)


# Cut clip from start time until end time
def cut_video(clip_index, start_time, end_time):
    command = PATH["FFMPEG"] + ' -y -i '+PATH["INPUT_FILE"]+' -c copy -ss ' + start_time + ' -to '+end_time+' '+PATH["OUTPUT_CLIP_FILE"]+clip_index+PATH["OUTPUT_CLIP_FORMAT"]
    subprocess.call(command, shell=True)


# Translate .mp4 to .ts file for merge.
def trans_intermediate_clip(clip_index):
    command = PATH["FFMPEG"] + " -y -i " + PATH["OUTPUT_CLIP_FILE"]+str(clip_index)+PATH["OUTPUT_CLIP_FORMAT"]+" -c copy -bsf:v h264_mp4toannexb -f mpegts ./clips/intermediate"+str(clip_index)+".ts"
    subprocess.call(command, shell=True)


# Merging .ts video clips as one highlight. Then remove .ts files
def merge_video(command):
    rm_ts_file_command = "rm clips/intermediate*"
    subprocess.call(command, shell=True)    
    subprocess.call(rm_ts_file_command, shell=True)


# Cut thumbnail from start time
def cut_thumbnail(thumbnail_index, thumbnail_time):
    command = PATH["FFMPEG"] + ' -y -i '+PATH["INPUT_FILE"]+' -ss ' + thumbnail_time + ' -vframes 1 '+PATH["OUTPUT_THUMB_FILE"]+thumbnail_index+PATH["OUTPUT_THUMB_FORMAT"]
    subprocess.call(command, shell=True)


# Cut gif from start time until 10 sec
def cut_gif(gif_index, start_time, end_time):
    command = PATH["FFMPEG"] + ' -y -i '+PATH["INPUT_FILE"]+' -ss ' + start_time + ' -to '+end_time+' -vf fps=1 -pix_fmt rgb32 -r 1 '+PATH["OUTPUT_GIF_FILE"]+gif_index+PATH["OUTPUT_GIF_FORMAT"]
    subprocess.call(command, shell=True)


# main function
# Count clips num, then loop and cut video
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

        merge_list = ""
        for clip_index in range(len(clips)):
            trans_intermediate_clip(clip_index)
            merge_list = merge_list+"./clips/intermediate"+str(clip_index)+".ts|"
        merge_command = PATH["FFMPEG"] + " -y -i \"concat:" + merge_list + "\" -c copy -bsf:a aac_adtstoasc "+PATH["OUTPUT_HIGHLIGHT_FILE"]+PATH["OUTPUT_HIGHLIGHT_FORMAT"]
        merge_video(merge_command)
        


# Calling init func to using apt ffmpeg or static ffmpeg
if __name__ == '__main__':
    input_val_len = len(sys.argv)
    if input_val_len is 3:
        path_init(None, sys.argv[1], sys.argv[2])
    elif input_val_len is 4:
        path_init(sys.argv[1], sys.argv[2], sys.argv[3])
    main()
