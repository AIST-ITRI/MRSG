#! /bin/sh

PREFIX=$1
DIR=$2

if [ -z "$PREFIX" ]; then
    echo "prefix is empty." >&2
    exit 1
fi

if [ ! -d "$DIR" ]; then
    echo "$DIR is not directory." >&2
    exit 1
fi

HERE=$(which $0)
HERE=$(dirname ${HERE})

find ${DIR} -name 'job.conf' | sort | while read i
do
    dir=$(dirname $i)
    echo "executes ${dir}"
    ${HERE}/build/file.bin \
        ${PREFIX}.xml \
        ${PREFIX}.deploy.xml \
        ${dir}/job.conf \
        ${dir}/mapcost.txt \
        ${dir}/redcost.txt \
        ${dir}/mapoutput.txt || exit 1
done || exit 1
