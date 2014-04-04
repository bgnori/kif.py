#!/usr/bin/python
# -*- coding=utf8 -*-


ur"""
0.
対応する仕様:
    正式名称 "CSA標準棋譜ファイル形式 V2.2"
    URL http://www.computer-shogi.org/protocol/record_v22.html

方針:
    htmlのタグを取り除いて適宜改行したものに対応づけて方針を記述する

2.1 概要
Specification:
    棋譜ファイルは処理を容易とするため、テキストファイルとする。
    文字コードと改行コードは、使用するOSや環境に依存する。
    コメントと棋譜情報(対局者名等)に日本語を使用してもよい。

方針:
    utf8/LFを仮定する.
    nkf -dw とか

Specification:
    棋譜ファイルは、次のデータから成る。
    (1)バージョン
    (2)棋譜情報
    (3)開始局面(持駒、手番を含む)
    (4)指し手と消費時間
    (5)コメント

    コメント以外は、この順番でデータがなければならない。

    (2)(4)(5)は、省略できる。
    セパレータ("/"だけの行)をはさんで、これらデータを繰り返し、
    複数の棋譜や局面を示すことができる。

方針:
    1~5の塊を本実装では以下Entryと呼ぶ
    ファイルは複数のEntryを含むことができる
    ファイル内でEntry同士は"/"で区切られる

>>> bool(re.match(PAT_SEP, "_"))
False

>>> bool(re.match(PAT_SEP, "/"))
True

    Entryは1つの棋譜を含む
    parse結果はEntryのリストを返す


2.2 バージョン
Specification:
    "V"で始まり、バージョンの数字を記述する。
    現バージョンは、V2.2とする。

方針:
    とりあえず2.2じゃなかったらエラーにする

>>> d = re.match(PAT_VERSION, "V2.2").groupdict()
>>> d["version_major"]
'2'
>>> d["version_minor"]
'2'

2.3 棋譜情報

方針:
    Entry objectのpropertyとして取れる様にする


Specification:
    (1) 対局者名
        "N+"に続き +側(先手、下手)の対局者名を記述する。
        "N-"に続き -側(後手、上手)の対局者名を記述する。
        それぞれ1行とする。
        省略可能とする。
        例:
        N+NAKAHARA
        N-YONENAGA
方針:
    正規表現で拾って終わり. 
    名称はそれぞれwhite/black. 

>>> re.match(PAT_PLAYER_WHITE, "N+NAKAHARA").groupdict()['white']
'NAKAHARA'
>>> re.match(PAT_PLAYER_BLACK, "N-YONENAGA").groupdict()['black']
'YONENAGA'


Specification:
    (2) 各種棋譜情報
        "$"で始め"キーワード"+":"(データ)の形式とする。
        これらの棋譜情報は、省略可能とする。
    (2-1) 棋戦名
        $EVENT:(文字列)
    (2-2) 対局場所
        $SITE:(文字列)
方針:
    正規表現で拾って終わり. 
    名称はそれぞれ event, site

>>> re.match(PAT_EVENT, u"$EVENT:meijin-sen").groupdict()['event']
u'meijin-sen'

>>> re.match(PAT_SITE, u"$SITE:shougi-kaikan").groupdict()['site']
u'shougi-kaikan'

Specification:
    (2-3) 対局開始日時(時刻は省略可)
        $START_TIME:YYYY/MM/DD HH:MM:SS
        "YYYY"は、西暦の年4桁の数字とする。
        次の"MM"は、月2桁の数字とする。
        "DD"は、日2桁の数字とする。
        "HH:MM:SS"は、24時間表現の時間(2桁)、分(2桁)、秒(2桁)とする。
        "HH:MM:SS"は、省略可能とする。
        日付と時刻の間のスペースは1桁とする。
        例:
        $START_TIME:2002/01/01 19:00:00
        $START_TIME:2002/01/01
Specification:
    (2-4) 対局終了日時(時刻は省略可)
        $END_TIME:YYYY/MM/DD HH:MM:SS
        開始日時と同様に、対局終了日時を記述する。

疑問:
    スペースは全角が許されるのだろうか?
    この仕様書を読む人でそんなものを吐くコードを書く人がいるとは思いたくないが.

方針:
    正規表現で拾って終わり. 
    名前はstart_time/end_time

>>> re.match(PAT_START_TIME, u"$START_TIME:1985/10/26").groupdict()['start_time']
u'1985/10/26'

>>> re.match(PAT_START_TIME, u"$START_TIME:1985/10/26 01:20:00").groupdict()['start_time']
u'1985/10/26 01:20:00'

>>> re.match(PAT_END_TIME, u"$END_TIME:1985/10/26 01:21:00").groupdict()['end_time']
u'1985/10/26 01:21:00'

Specification:
    (2-5) 持ち時間(持ち時間と秒読み)
        $TIME_LIMIT:HH:MM+SS
        持ち時間+秒読みとする。
        持ち時間"HH:MM"は、時間(2桁以上の数字)、分(2桁の数字)とする。
        秒読み"SS"は、秒単位の数字(2桁以上)とする。
        切れ負けの場合、秒読みを"00"とする。
        例:
        $TIME_LIMIT:00:25+00 持ち時間:25分、切れ負け
        $TIME_LIMIT:00:30+30 持ち時間:30分、秒読み:30秒
        $TIME_LIMIT:00:00+30 初手から30秒
疑問:
    time controlじゃないんだ...
    http://en.wikipedia.org/wiki/Time_control
方針:
    名前はtc_hour, tc_min, tc_byo_yomi ,  最終的にはすべて秒単位に変換, tupleでもつ

>>> d = re.match(PAT_TIME_CONTROL, u"$TIME_LIMIT:00:15+30").groupdict()
>>> d['tc_hour']
u'00'
>>> d['tc_min']
u'15'
>>> d['tc_byo_yomi']
u'30'

Specification:
    (2-6) 戦型
        $OPENING:(文字列)
方針:
    名称はopening

>>> re.match(PAT_OPENING, u"$OPENING:grab attack").groupdict()['opening']
u'grab attack'


Specification:
    (2-7) 補足
        "$"で始まる各種棋譜情報の表記順は任意でいい。
方針:
    問題ないはず.

2.4 駒と位置

Specification:
    駒名:歩から玉まで:FU,KY,KE,GI,KI,KA,HI,OU
    上の成駒:TO,NY,NK,NG,UM,RY
    位置:1一を"11"、5一を"51"、9九を"99"というふうに、2桁の数字で表す。
    駒台は"00"とする。
    先手(下手)は"+"、後手(上手)は"-"を付ける。
方針:
    各種定数

2.5 開始局面

Specification:
    "P"で始まる文字列(以前に決めたもの)。
    
    (1) 平手初期配置と駒落ち
        平手初期配置は、"PI"とする。駒落ちは、"PI"に続き、
        落とす駒の位置と種類を必要なだけ記述する。
        例:二枚落ちPI82HI22KA

>>> d = re.match(PAT_POSITION_1, u"PI82HI22KA").groupdict()
>>> d['position_initial']
u'I'
>>> d['handicap']
u'82HI22KA'


    (2) 一括表現
        1行の駒を以下のように示す。行番号に続き、先後の区別と駒の種類を記述する。
        先後の区別が"+""-"以外のとき、駒がないとする。
        1枡3文字で9枡分記述しないといけない。
        例:
            P1-KY-KE-GI-KI-OU-KI-GI-KE-KY
            P2 * -HI *  *  *  *  * -KA * 

>>> d = re.match(PAT_POSITION_2, u"P1-KY-KE-GI-KI-OU-KI-GI-KE-KY").groupdict()
>>> d['rank']
u'1'
>>> d['squares']
u'-KY-KE-GI-KI-OU-KI-GI-KE-KY'

>>> d = re.match(PAT_POSITION_2, u"P2 * -HI *  *  *  *  * -KA * ").groupdict()
>>> d['rank']
u'2'
>>> d['squares']
u' * -HI *  *  *  *  * -KA * '


    (3) 駒別単独表現
        一つ一つの駒を示すときは、先後の区別に続き、位置と駒の種類を記述する。
        持駒に限り、駒の種類として"AL"が使用でき、残りの駒すべてを表す。
        駒台は"00"である。
        玉は、駒台へはいかない。
        例:
            P-22KA
            P+99KY89KE
            P+00KIOOFU
            P-00AL

疑問:
    P+00KIOOFU
    は
    P+00KI00FU
    のタイポではないか？


>>> re.match(PAT_POSITION_3, u"P-22KA").groupdict()["koma_location"]
u'-22KA'
     
>>> re.match(PAT_POSITION_3, u"P+00KI00FU").groupdict()["koma_location"]
u'+00KI00FU'

>>> re.match(PAT_POSITION_3, u"P-00AL").groupdict()["koma_location"]
u'-00AL'

Specification:
    (4) 手番
        "+"で+側(先手、下手)を、"-"で-側(後手、上手)の手番を示す。1行とする。
        手番の指定は必要である。

    (5) 補足
        初期状態はすべての駒が駒箱にあり、上記(2)(3)の指定は、駒を駒箱から盤上に
        移動する動作を表現する。したがって、以上の(1)から(3)の指定で位置が決まらないものは、
        駒箱にあるとする。また、盤面の指定が無いときは、盤上に何も無いとする。
        上記(1)と(2)は同時に指定しない。
        "P+00AL"、"P-00AL"は、最後に指定しなければならない。
        手番は、盤面データの後に指定する。

方針:
    これらは正規表現でなくコードで対応する


2.6 指し手と消費時間

Specification:
    1手の指し手を1行とし、次の行にその指し手で消費した時間を示す。
    (1) 通常の指し手
        先後("+"、または"-")の後、移動前、移動後の位置、移動後の駒名、で表す。
        例:
            +3324NG ▲2四銀成

>>> d = re.match(PAT_NMOVE, u"+3324NG").groupdict()
>>> d['move_player']
u'+'
>>> d['move_from']
u'33'
>>> d['move_to']
u'24'
>>> d['move_piece']
u'NG'

    (2) 特殊な指し手、終局状況
        %で始まる。

        %TORYO 投了
        %CHUDAN 中断
        %SENNICHITE 千日手
        %TIME_UP 手番側が時間切れで負け
        %ILLEGAL_MOVE 手番側の反則負け、反則の内容はコメントで記録する
        %+ILLEGAL_ACTION 先手(下手)の反則行為により、後手(上手)の勝ち
        %-ILLEGAL_ACTION 後手(上手)の反則行為により、先手(下手)の勝ち
        %JISHOGI 持将棋
        %KACHI (入玉で)勝ちの宣言
        %HIKIWAKE (入玉で)引き分けの宣言
        %MATTA 待った
        %TSUMI 詰み
        %FUZUMI 不詰
        %ERROR エラー
        ※文字列は、空白を含まない。
        ※%KACHI,%HIKIWAKE は、コンピュータ将棋選手権のルールに対応し、
        第3版で追加。
        ※%+ILLEGAL_ACTION,%-ILLEGAL_ACTIONは、手番側の勝ちを表現できる。

方針:
    正規表現

>>> d = re.match(PAT_IMOVE, u"%TORYO").groupdict()
>>> d['irregular_move']
u'TORYO'


    (3) 消費時間
        "T"に続き、その指し手で消費した時間を秒単位で示す。1秒未満は、切り捨てる。
        消費時間は省略可能とする。
        例:
            T10

方針:
    正規表現だけで手に関連づけるのは辛い
    intに変換のこと

>>> d = re.match(PAT_TIME_COMSUMED, u"T10").groupdict()
>>> d['time_consumed']
u'10'


Specification:
    2.7 コメント
        "'"(アポストロフィー)で始まる行は、ソフトが読み飛ばすコメントとする。
        文の途中からのコメントは、記述できない。
方針:
    「文の途中」は「行の途中」のタイポと見なして実装する


>>> d = re.match(PAT_COMMENT, u"`This is comment.").groupdict()
>>> d['comment']
u'This is comment.'



Specification:
    2.8 マルチステートメント
        ","(カンマ)を用いて、複数の行を1行にまとめることができる。
        
方針:
    なんですと？！ 対応しない方向で. 仕様が曖昧.
    * 出回っているデータで問題を起こしそうなのを集めるのが面倒
    * ",/," とかも可能
    * 名前に","が含まれる場合
    * "`,`"とかどうするのよ
    * 別にデータ長が短くなる訳じゃない.
    * エディタで見る場合, 折り返し処理が重くなる可能性がある


Specification:
    2.9 ファイル名の拡張子("."以降の名前)
        "csa"とする。unixのように大文字小文字の区別がある場合は小文字とする。
方針:
    out of scope.
    

"""
import re
PAT_SEP = ur'^/$'
PAT_VERSION = ur"^V(?P<version_major>\d+)(\.(?P<version_minor>\d+))?$"
PAT_PLAYER_WHITE = ur"^N(\+(?P<white>.*$))"
PAT_PLAYER_BLACK = ur"^N(\-(?P<black>.*$))"
PAT_EVENT = ur"^\$EVENT:(?P<event>.*$)"
PAT_SITE = ur"^\$SITE:(?P<site>.*$)"
PAT_START_TIME = ur"^\$START_TIME:(?P<start_time>.*$)"
PAT_END_TIME = ur"^\$END_TIME:(?P<end_time>.*$)"
import time
STRPTIME_FORMAT = ur"%Y/%m/%d %H:%M:%S"
PAT_TIME_CONTROL = ur"^\$TIME_LIMIT:(?P<tc_hour>\d\d):(?P<tc_min>\d\d)\+(?P<tc_byo_yomi>\d\d)$"
PAT_OPENING = ur"^\$OPENING:(?P<opening>.*$)"
PAT_KOMA = ur"(FU|KY|KE|GI|KI|KA|HI|OU|TO|NY|NK|NG|UM|RY)"

PAT_POSITION_1 = ur"^P(?P<position_initial>I)(?P<handicap>(\d\d\w\w)*)$"
PAT_POSITION_2 = ur"""^P(?P<rank>\d)""" \
                 ur"""(?P<squares>(""" \
                    ur"""([+-]""" + PAT_KOMA + ur""")""" \
                    ur"""|([^+-]..)"""\
                 ur"""){9})$"""

PAT_POSITION_3 = ur"""^P(?P<koma_location>[+-]((\d\d""" + PAT_KOMA + ur""")+|00AL))"""

PAT_TURN = "^[+-]$"
            
PAT_POSITION = ur"""(?P<position>"""\
    + "|".join([PAT_POSITION_1, 
        PAT_POSITION_2 + "{9}",
        PAT_POSITION_3 + "*"]) \
    + PAT_TURN + ur""")$"""

PAT_NMOVE = ur"^(?P<move_player>[+-])(?P<move_from>\d\d)(?P<move_to>\d\d)(?P<move_piece>\w\w)$"
PAT_IMOVE = ur"^%(?P<irregular_move>\w+)$"
PAT_COMMENT = ur"^`(?P<comment>.*)$"
PAT_TIME_COMSUMED = "^T(?P<time_consumed>\d+)$"



if __name__ == "__main__":
    #http://joernhees.de/blog/2010/12/15/python-unicode-doctest-howto-in-a-doctest/
    #http://stackoverflow.com/questions/1733414/how-do-i-include-unicode-strings-in-python-doctests
    import sys
    reload(sys)
    sys.setdefaultencoding("UTF-8")
    

    import doctest
    doctest.testmod()
    print 'done'


