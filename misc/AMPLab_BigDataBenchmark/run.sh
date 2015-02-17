#! /bin/sh

DATABASE=benchmark

OPTS="--database ${DATABASE}"

# Query 1
hive ${OPTS} --hivevar THRESHOLD=1000 -f hiveql/q1.hql || exit 1
hive ${OPTS} --hivevar THRESHOLD=100  -f hiveql/q1.hql || exit 1
hive ${OPTS} --hivevar THRESHOLD=10   -f hiveql/q1.hql || exit 1

# Query 2
hive ${OPTS} --hivevar LENGTH=8  -f hiveql/q2.hql || exit 1
hive ${OPTS} --hivevar LENGTH=10 -f hiveql/q2.hql || exit 1
hive ${OPTS} --hivevar LENGTH=12 -f hiveql/q2.hql || exit 1

# Query 3
hive ${OPTS} --hivevar LASTDAY='"1980-04-01" ' -f hiveql/q3.hql || exit 1
hive ${OPTS} --hivevar LASTDAY='"1983-01-01" ' -f hiveql/q3.hql || exit 1
hive ${OPTS} --hivevar LASTDAY='"2010-01-01" ' -f hiveql/q3.hql || exit 1

# Query 4
hive ${OPTS} -f hiveql/q4.hql || exit 1
