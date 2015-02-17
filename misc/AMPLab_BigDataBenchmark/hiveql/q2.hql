set mapred.reduce.tasks = 150;
DROP TABLE IF EXISTS result;
CREATE TABLE result AS SELECT SUBSTR(sourceIP, 1, ${LENGTH}), SUM(adRevenue) FROM uservisits GROUP BY SUBSTR(sourceIP, 1, ${LENGTH});
