=========================
AMPLab Big Data Benchmark
=========================

このディレクトリには下記のサイトで公開されているベンチマークプログラムを実行するためのファイル群を格納しています。

AMPLab Big Data Benchmark ウェブサイト
    https://amplab.cs.berkeley.edu/benchmark/

.. contents::

内容
====

このディレクトリには下記のファイルが含まれます。

README.rst
    この文書
hiveql
    ベンチマーク用のHiveクエリを格納するディレクトリ
run.sh
    ベンチマーク実行用のスクリプト
warc2table.py
    documents用にデータを変換するスクリプト(利用方法については後述します)
udf/url_count.py
    Query4用から呼ばれるスクリプト

実行手順
========

実行手順について以下に記します。

入力データセットの準備
----------------------

AMPLab Big Data Benchmarkが入力利用するデータセットについて詳細を記します。

入力データセットの形式
~~~~~~~~~~~~~~~~~~~~~~

以下の3つのテーブルが必要です。

1. rankings
2. uservisits
3. documents

各テーブルのフォーマットは下記の通りです。

rankings

============== =================
 フィールド名   型
============== =================
pageurl         string
pagerank        int
avgduration     int
============== =================

uservisits

============== ==========
 フィールド名   型
============== ==========
 sourceip       string
 desturl        string
 visitdate      string
 adrevenue      double
 useragent      string
 countrycode    string
 languagecode   string
 searchword     string
 duration       int
============== ==========

documents

============== ==========
 フィールド名   型
============== ==========
 line           string
============== ==========

documentsはAMPLab Big Data Benchmarkのページからは「Unstructured HTML documents」という情報以外見つけることができませんでした。
そのため、フィールドとして文字列のものを1つ用意して、入力データの1行が1レコードとなるようにデータを登録することとします。

rankingsとuservisitsの作成方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

「rankings」と 「uservisits」はHiBenchに含まれるデータ生成ツールを使って入力データを作成します。
HiBenchは下記の方法で入手します。

    $ git clone https://github.com/intel-hadoop/HiBench.git

「bin/hibench-config.sh」を実行環境にあわせて変更する必要があります。
詳しくは下記のHiBenchのREAMEを参照下さい。

- https://github.com/intel-hadoop/HiBench/blob/master/README.md

参考までに、我々が実行した際に変更を行った変数について下記に記します。

====================== ============== =====================================================================
 変数名                 初期値         設定した値
====================== ============== =====================================================================
 JAVA_HOME              空             /usr/java/default
 HADOOP_HOME            空             /usr/lib/hadoop
 HADOOP_EXECUTABLE      空             /usr/bin/hadoop
 HADOOP_CONF_DIR        空             /etc/hadoop/conf
 HADOOP_EXAMPLES_JAR    空             /usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar
 MAPRED_EXECUTABLE      空             /usr/bin/mapred
 HADOOP_MAPRED_HOME     $HADOOP_HOME   変数定義をコメントアウト
 DATA_HDFS              /HiBench       /user/<username>/HiBench (<username>には実際のユーザ名が入りいます)
====================== ============== =====================================================================

HiBenchの設定を行った後に、「rankings」と「uservisits」用のデータを生成するために「hivebench/bin/prepare.sh」を実行します。::

    $ ./hivebench/bin/prepare.sh

生成するデータ量は hivebench/conf/configure.sh の以下の変数で指定可能です。::

    USERVISITS
    PAGES

デフォルト値は下記の通りです。::

    USERVISITS=100000000
    PAGES=12000000

その上で、下記のHiveQLのクエリを実行して、このベンチマーク用のデータベースとテーブルを作成します。::

    CREATE DATABASE IF NOT EXISTS benchmark;
    USE benchmark;

    CREATE EXTERNAL TABLE rankings(
        pageURL STRING,
        pageRank INT,
        avgDuration INT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS SEQUENCEFILE LOCATION '/HiBench/Hive/Input-comp/rankings';

    CREATE EXTERNAL TABLE uservisits (
        sourceIP STRING,
        destURL STRING,
        visitDate STRING,
        adRevenue DOUBLE,
        userAgent STRING,
        countryCode STRING,
        languageCode STRING,
        searchWord STRING,
        duration INT ) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS SEQUENCEFILE LOCATION '/HiBench/Hive/Input-comp/uservisits';

ここではbenchmarkという名称のデータベースを、このベンチマーク用に利用しています。

注意
    CREATE TABLEクエリのLOCATIONで指定するパスは「bin/hibench-config.sh」の変数DATA_HDFSのよって変わります。
    以下に指定する値を記します。

    ============== =================================================
     テーブル名     LOCATIONに指定する値
    ============== =================================================
     rankings       <変数DATA_HDFSの値>/Hive/Input-comp/rankings
     uservisits     <変数DATA_HDFSの値>/Hive/Input-comp/uservisits
    ============== =================================================

documentsの作成方法
~~~~~~~~~~~~~~~~~~~

documentsのデータはCommon CrawlのデータをサンプリングしたものとAMPLab Big Data Benchmarkのドキュメントに記述がありました。
Common Crawlのサイトを下記に記します。

- http://commoncrawl.org/

ここからデータを取得するにはまずパスのリストを取得します。
下記のページに、2014年12月に収集したデータのパスのリストへのリンクがあります。

- http://blog.commoncrawl.org/2015/01/december-2014-crawl-archive-available/

Common Crawlでは下記の3つのフォーマットでデータが提供されます。

- WARC
- WAT
- WET

この中のWARC形式のデータをdocumentsに格納します。そのため、WARCファイルのパスのリストを取得します。

このファイルの先頭の数行を下記に記します。::

  common-crawl/crawl-data/CC-MAIN-2014-52/segments/1418802764752.1/warc/CC-MAIN-20141217075244-00000-ip-10-231-17-201.ec2.internal.warc.gz
  common-crawl/crawl-data/CC-MAIN-2014-52/segments/1418802764752.1/warc/CC-MAIN-20141217075244-00001-ip-10-231-17-201.ec2.internal.warc.gz
  common-crawl/crawl-data/CC-MAIN-2014-52/segments/1418802764752.1/warc/CC-MAIN-20141217075244-00002-ip-10-231-17-201.ec2.internal.warc.gz
  common-crawl/crawl-data/CC-MAIN-2014-52/segments/1418802764752.1/warc/CC-MAIN-20141217075244-00003-ip-10-231-17-201.ec2.internal.warc.gz
  common-crawl/crawl-data/CC-MAIN-2014-52/segments/1418802764752.1/warc/CC-MAIN-20141217075244-00004-ip-10-231-17-201.ec2.internal.warc.gz

下記のAmazon Public Data SetのURLに、このパスを付与することで実際のデータを取得することができます。

- https://aws-publicdatasets.s3.amazonaws.com/

以下に例を記します。::

    $ wget https://aws-publicdatasets.s3.amazonaws.com/common-crawl/crawl-data/CC-MAIN-2014-52/segments/1418802764752.1/warc/CC-MAIN-20141217075244-00000-ip-10-231-17-201.ec2.internal.warc.gz

このファイルをそのままHiveのテーブルとして登録することはできないため、付属の「warc2table.py」でデータを変換します。::

    $ ./warc2table.py CC-MAIN-20141217075244-00000-ip-10-231-17-201.ec2.internal.warc.gz > documents.txt

ここでは変換後のデータをdocuments.txtという名称のファイルに格納しています。
変換後に以下のHivQLでテーブルに登録します。。::

        USE benchmark;
        CREATE TABLE documents(line STRING) STORED AS TEXTFILE;
        LOAD DATA LOCAL INPATH 'documents.txt' INTO TABLE documents;

複数のファイルを登録する場合には以下の処理をファイル毎に繰り返し行います。

- ファイルの取得
- warc2table.pyによる変換
- hiveへのLOAD DATAクエリでの登録


注意
    documentsテーブルの構築方法についてはAMPLab Big Data Benchmarkのサイトにある下記2点の情報とQuery4の処理内容から推測したものです。

     - 「Unstructured HTML documents」である
     - Common Crawlのデータをサンプリングしたものである。

    そのため、オリジナルのものとはことなる可能性があります。

実行方法
--------

run.shを実行することで、ベンチマークを実行することができます。::

    $ ./run.sh

変更点
======

Query 3については最大値を持つ行を取得するのにソートとLIMITを組み合わせているため、処理が1つのReducerに集中する問題がありました。
そのため、ソードではなくmax UDAFを利用して最大値を求めるように変更しています。

変更後のQueryを下記に記します。::

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
                    FROM uservisits UV WHERE UV.visitDate > "1980-01-01" AND UV.visitDate < `X'
                ) NUV ON (R.pageURL = NUV.destURL) GROUP BY sourceIP
            ) a
        ) b;

変更前のQueryとの差分を下記に記します。::

    @@ -1,4 +1,8 @@
     CREATE TABLE result AS
    +    SELECT b.value.col2 as sourceIP, b.value.col1 as totalRevenue, b.value.col3 as pageRank FROM  (
    +        SELECT
    +            max(struct(a.totalRevenue, a.sourceIP, a.pageRank)) AS value
    +        FROM (
         SELECT
             NUV.sourceIP,
             sum(NUV.adRevenue) as totalRevenue,
    @@ -10,5 +14,5 @@
                 adRevenue
             FROM uservisits UV WHERE UV.visitDate > "1980-01-01" AND UV.visitDate < `X'
         ) NUV ON (R.pageURL = NUV.destURL) GROUP BY sourceIP
    -            ORDER BY totalRevenue DESC LIMIT 1;
    -
    +        ) a
    +    ) b;

また、細かい点ですが、AMPLab Big Data Benchmarkのサイトに記載されているクエリに対して下記の変更を加えています。

- 「\`X'」の部分についてコマンドライン引数の --hivevar で置き換え可能なように ${変数名} に変更しました。
- Reducerの数を設定しています。
- Query 4についてはスクリプトのパスを変更しました。

以上です。
