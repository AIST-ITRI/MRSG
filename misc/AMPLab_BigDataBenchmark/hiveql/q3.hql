set mapred.reduce.tasks = 150;
DROP TABLE IF EXISTS result;
CREATE TABLE result AS 
    SELECT b.value.col2 as sourceIP, b.value.col1 as totalRevenue, b.value.col3 as pageRank FROM  (
        SELECT
            max(struct(a.totalRevenue, a.sourceIP, a.pageRank)) AS value
        FROM (
            SELECT 
                NUV.sourceIP, 
                sum(NUV.adRevenue) as totalRevenue, 
                avg(R.pageRank) as pageRank 
            FROM rankings R JOIN (
                SELECT 
                   sourceIP, 
                   destURL, 
                   adRevenue 
                FROM uservisits UV WHERE UV.visitDate > "1980-01-01" AND UV.visitDate < ${LASTDAY}
            ) NUV ON (R.pageURL = NUV.destURL) GROUP BY sourceIP
        ) a
    ) b;
