#!/bin/bash
set -e
cd "$(dirname "$0")/data"

for src in \
    {basketball,boxes,football,juggle,softball,tennis}/frame1 \
    {coffee_martini,cook_spinach,cut_roasted_beef,flame_salmon_1,flame_steak,sear_steak}/frame1 \
    {discussion,trimming,stepin,vrheadset}/frame1 \
    Robo360/batch1/*/frame1 \
    Robo360/batch2/*/frame1 \
    SiggraphAsia2026VVC/selfcap/{compression,sparse}/test/*/frame1 \
    SiggraphAsia2026VVC/siga/{compression,sparse}/{test,val}/*/frame1
do
    dst="saved_frame1/data/$src"
    archive="saved_frame1/${src}.zip"
    mkdir -p "$(dirname "$dst")" "$(dirname "$archive")"
    rm -rf "$dst"
    cp -a "$src" "$dst"
    rm -f "$archive"
    (cd saved_frame1/data && zip -r -q "../${src}.zip" "$src")
    echo "saved data/$src -> data/$dst"
    echo "packed data/$archive"
done
