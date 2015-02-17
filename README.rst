=========================================
Extended MapReduce Simulator over SimGrid
=========================================

プログラムの概要
================

本プログラムは、フランスINRIAならびにブラジルUFRGSがオープンソースとして開発しているMRSG（MapReduce Simulator over SimGrid）に改良を施すことで、大規模データ処理ワークロードの実用的なシミュレータを実現するものです。改良には、Apache Hadoopの実行トレースファイルを元にシミュレーションを行うための支援機能のほか、Apache Hadoop実装をより忠実にシミュレートするための改善、MRv2をシミュレートするための改善、システム構築ならびにシミュレーション実行を簡便にするための改善も含みます。また、（独）産業技術総合研究所で開発しているHivemall (https://github.com/myui/hivemall) の実行トレースファイルも含まれています。

本プログラムは、（独）産業技術総合研究所で研究開発している「IMPULSE超集中型データ処理のためのアーキテクチャ」を検討する目的に開発されたものです。

ディレクトリ構成
================

patches
    MRSGへの変更

simple_app
    単純なアプリケーション

file_app
    コストやデータ量をファイルから読み込むアプリケーション

platforms
    現状利用している環境を定義したファイル

traces
    実際に実行したMapReduceのトレース結果

tools
    ツール類

misc
    その他

必要要件
========

実行には以下のものが必要である。

- SimGrid
- C/C++ Compiler
- Boost C++ Library
- Python
- lxml(2.3以降)

トレース結果の実行方法
======================

同封のKDDCUP2012track2のトレース結果を実行する手順について記す。
手順の概要は下記の通りである。

1. Extended MapReduce Simulator over SimGrid（カスタム版MRSG）の作成
2. プラットフォームファイルの生成
3. トレース情報を元にシミュレーションを実行するMRSGアプリケーションのビルド
4. 実行

以下に詳細について示す。この手順では実行前のカレントディレクトリは、このREADME.rstファイルのあるディレクトリであるとする。

カスタム版MRSGの作成
----------------------

カスタム版MRSGの作成コマンドは下記の通りである。::

    $ ./waf configure --prefix=$HOME/SimGrid --search-path=$HOME/SimGrid
    $ ./waf build
    $ ./waf install

waf configureの--prefixオプションでインストール先を指定する。
また、--search-pathオプションで必要なライブラリ等の探索パスを追加できる。複数指定する場合には「:」で区切って指定する。

この例ではインストール先として、$HOME/SimGridを指定している。
環境によっては共有ライブラリのパスを通す必要がある。

Linuxの場合には例えば下記のようにLD_LIBRARY_PATHを利用する。::

    $ LD_LIBRARY_PATH=$HOME/SimGrid/lib
    $ export LD_LIBRARY_PATH

プラットフォームファイルの作成
------------------------------

プラットフォームファイルを作成するにはtools以下のgen_cluster.pyを利用する。
実行時には出力ファイル用のプレフィックを引数として与えて実行する。
以下に「my_cluster」を出力ファイル用のプレフィックスとして与えた場合のコマンドを示す。 ::

    $ cd ..
    $ tools/gen_cluster.py my_cluster

このコマンドを実行した場合には下記の3つのファイルが生成される。::

    my_cluster.xml
    my_cluster.deploy.xml
    my_cluster.contents.txt

このツールでは単一のクラスタで構成される環境のみが生成可能である。
また、以下のオプションで生成する環境のパラメータをして可能である。

-w NUMBER_OF_WORKERS, --number-of-workers NUMBER_OF_WORKERS  計算ノードの数。デフォルト値は15ノードである。
-p POWER, --power POWER                                      CPU 1 Core当たりのパワー。デフォルト値は172800000000である。
-c NUMBER_OF_CORES, --number-of-cores NUMBER_OF_CORES        1ノードあたりのCPUコア数。デフォルト値は20である。
-b BAND_WIDTH, --band-width BAND_WIDTH                       ノード間のバンド幅。デフォルト値は200Mbpsである。
-l LATENCY, --latency LATENCY                                ノードとスイッチの間のレイテンシ。デフォルトでは0.0005である。
--read READ                                                  ディスクの読み込み速度。デフォルト値は550MBpsである。

トレース情報を元にシミュレーションを実行するMRSGアプリケーションのビルド
------------------------------------------------------------------------

file_app以下にトレース情報を元にシミュレーションを行うMRSGアプリケーションがある。
ビルドにはwafを利用する。

まず、MRSG等必要なライブラリのパスを--search-path引数で指定して指定してwaf configureを実行する。::

    $ cd file_app
    $ ./waf configure --search-path=$HOME/SimGrid

この例では、インストール先、探索パスの両方に$HOME/SimGridを指定している。
次に、waf buildでビルドを実行する。::

    $ ./waf build

build以下にfile.binという名称で実行ファイルが生成される。::

    $ ls build/file.bin
    build/file.bin

実行
----

traces/kddcup2012track2-2014-12以下にKDDCUP2012track2をHiveMallで処理した際のトレース情報を格納している。

例えば、Logistic Regressionを利用して計算した場合のトレース結果はtraces/kddcup2012track2-2014-12/0002-LogisticRegression以下にある。
このディレクトリ以下にはさらに5つのディレクトリがある。::

    $ ls -1  traces/kddcup2012track2-2014-12/0002-LogisticRegression
    mapreduce-0001
    mapreduce-0002
    mapreduce-0003
    mapreduce-0004
    mapreduce-0005

これはLogistic Regressionの実行が5つのMapReduceの実行を行ったためである。
これを元にシミュレーションを実行する手順を示す。

まず、file_appディレクトリから元のディレクトリに戻る。::

    $ cd ..

先ほど生成したプラットフォーム定義ファイルを利用する。::

    $ ls -1 my_cluster.*
    my_cluster.contents.txt
    my_cluster.deploy.xml
    my_cluster.xml

file_app/run.shにプラットフォーム定義ファイルのプレフィックスとトレースファイルのディレクトリを指定して実行する。::

    $ file_app/run.sh my_cluster traces/kddcup2012track2-2014-12/0002-LogisticRegression/mapreduce-0001

Logistic Regressionで実行されたMapReduceについてすべて実行するには、以下のように上位のディレクトリを指定する。::

    $ file_app/run.sh my_cluster traces/kddcup2012track2-2014-12/0002-LogisticRegression

実行順はファイル名の文字列順となる。
シミュレーションの結果はログの"JOB END"が出力された際の時間となる。::

    [node-0.zone01:master:(1) 121.434192] [msg_test/INFO] JOB END

トレース情報の取得方法
======================

トレース情報の取得はtools/mr_tracer.pyを利用する。
実行時の引数として、ジョブIDと実行マシンのCPUパワーを指定する。以下に例を示す。::

    $ tools/mr_tracer.py job_1421819446678_0315 172800000000

ここではジョブIDにjob_1421819446678_0315を、CPUパワーとして172800000000を指定している。

このスクリプトはHadoopのMapReduce History ServerからREST APIを利用して情報を取得する。
デフォルトではローカルホストのMapReduce History Serverから情報を取得する。
ローカルホスト以外で動作しているMapReduce History Serverから情報を取得する場合には -s オプションでホスト名を指定する。::

    $ tools/mr_tracer.py -s history_server.example.org job_1421819446678_0315 172800000000

取得したトレース結果は「mr_trace_+ ジョブID」という名称のディレクトリに保存される。


patches - MRSGへの変更
======================

オリジナルのMapReduce over SimGrid(以下、MRSGと記す)への変更は patches ディレクトリ以下にパッチとして格納している。以下にオリジナルのMRSGのgitレポジトリからMRSGのソースファイルを取得し、パッチを当てる手順について記す。::

    $ git clone https://github.com/MRSG/MRSG.git
    $ cd MRSG
    $ git am ../patches/*.patch

変更点は下記の通りである。

- ビルドツールとして waf を利用するようにした。
- 共有ライブラリとしてビルドするように変更した。
- Hadoopの実装と同様にReducerがMapperから入力を取得する際の順序をランダムにした。
- SimGridのFile APIを使って、MapTaskの入力データをディスクから読む処理を追加した。(書き込み、及びReducerの入力については現状扱っていない)
- 以下の3つのパラメータを MRSG_main() の conf 引数で渡す設定ファイルで指定可能とした。
    - heartbeat_interval

      NodeManagerのハートビートの間隔を秒単位で指定する。デフォルト値は1(秒)である。
      変更前は計算ノードの数が300までは3秒で、それ以上はノード数に比例して値が大きくなっていた。
      Hadoopではyarn-site.xmlのyarn.resourcemanager.nodemanagers.heartbeat-interval-msで設定を行う。
      Hadoopのデフォルト値は1000(ms)である。

    - reduce_polling_interval

      ReducerがMapperの完了を確認する間隔を秒で指定する。デフォルト値は1(秒)である。
      変更前は5秒間隔であった。

      Hadoop-2.3.0の実装を確認したところ、1秒周期でポーリングしていたため変更した。

    - reduce_slowstart_completed_maps

      Reducerの実行を開始する敷居値である。
      デフォルトでは0.05である(5%のMapperが完了したらReducerの実行を開始する)。

      変更前は0.1であった。

      Hadoopではmapred-site.xmlのmapreduce.job.reduce.slowstart.completedmapsで指定する。
      Hadoopのデフォルト値は0.05である。


不具合
======

- gen_cluster.pyにて生成しているプラットフォーム定義ファイルではディスクの容量が1PB固定である。
- gen_cluster.pyにて生成しているプラットフォーム定義ファイルでは、チャンク用のファイルとして1TBのファイルを定義している。
  したがって、チャンクのサイズが1TBよりも大きい場合には正常に動作しない。

以上
