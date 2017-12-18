#!/bin/sh
CONTENTS_ID_MP4="$1"
CONTENTS_JSONFILE="$2"

APT_UPDATE=0
if dpkg --get-selections | grep -q "wget" > /dev/null; then
        echo "wget is checked..."
else
        if [ $APT_UPDATE -eq 0 ]; then
                echo "apt update..."
                apt-get -qq update
                APT_UPDATE=1
        fi
        echo "Install wget..."
        apt-get -qq install wget
fi

if ls | grep ffmpeg > /dev/null; then
    echo "ffmpeg is checked..."
else
    echo "download ffmpeg..."
    wget -q -O tmp.html https://www.johnvansickle.com/ffmpeg/
    RELEASE_URL=`cat tmp.html | grep -Eo '(http|https)[^<>]*?tar.xz' | grep -m 1 release-64bit`
    NEW_FFMPEG_VER=`cat tmp.html | grep -Eo 'release: [0-9.]*[0-9]' | grep -Eo '[0-9.]*[0-9]'`
    rm tmp.html

    wget -qq $RELEASE_URL
    tar -xf ffmpeg-release-64bit-static.tar.xz
    rm ffmpeg-release-64bit-static.tar.xz
fi

if ls | grep clips > /dev/null; then
    echo "clips dir is checked..."
else
    echo "make clips dir..."
    mkdir clips
fi

python3 make_video_clip.py ffmpeg-*/ffmpeg $CONTENTS_ID_MP4 $CONTENTS_JSONFILE
