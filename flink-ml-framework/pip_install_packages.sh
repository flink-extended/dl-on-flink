#!/usr/bin/env bash


#mapfile array <user.properties

array=()
for line in `cat ../user.properties`
do
    array+=("$line")
done

len=${#array[*]}
PACKAGES=""
for i in $(seq 2 1 ${len})
do
    PACKAGES="$PACKAGES ${array[i]}"
done

pip_version=${array[1]}
OLD_IFS="$IFS"
IFS="="
pip_array=($pip_version)
IFS="$OLD_IFS"
pipV=${pip_array[1]}

${pipV} install --user ${PACKAGES}