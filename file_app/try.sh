#! /bin/sh

DIR=$1

if [ ! -d "$DIR" ]; then
    echo "$DIR is not directory." >&2
fi

exec ./build/file.bin \
    ../platforms/asgc_hadoop_cluster.xml \
    ../platforms/asgc_hadoop_cluster.deploy.xml \
    ${DIR}/job.conf \
    ${DIR}/mapcost.txt \
    ${DIR}/redcost.txt \
    ${DIR}/mapoutput.txt
