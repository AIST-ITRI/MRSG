DROP TABLE IF EXISTS result;
CREATE TABLE result AS SELECT pageURL, pageRank FROM rankings WHERE pageRank > ${THRESHOLD};
