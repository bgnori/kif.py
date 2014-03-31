#!/usr/bin/python
# -*- coding=utf8 -*-


"""
概要:
柿木将棋フォーマットをparseするライブラリです.
将棋やる人は日本語読めるだろうから日本語で書いています.

使い方

>>> import kif
>>> p = kif.Parser()
>>> with <処理したいkifファイルを開く> as f
        for line in f:
            m = p.feed(line)
            <指し手の表現であるMoveのインスタンスを使って処理をする>


正規表現とか仕様に関して次のページを起点に作成を行った.
御礼申し上げます.
http://openlabo.blogspot.jp/2013/09/blog-post_16.html

To Do:
 * ヘッダへの対応
 * 変化分岐への対応

"""

import re

WSS = ur"""[ \t\v　]*""" #最後は全角スペース!
regexp = re.compile(WSS+ ur"""(?P<nth>\d+)"""
            + WSS + \
            ur"""(?P<moveto>"""
                ur"""((?P<toX>[１２３４５６７８９])(?P<toY>[一二三四五六七八九]))"""
                ur"""|(?P<same>同)"""
            ur""")?"""
            + WSS + \
            ur"""(?P<piece>歩|成?香|成?桂|成?銀|金|角|飛|王|玉|と|馬|竜)?"""
            ur"""(?P<promote>成)?"""
            ur"""(?P<place>打)?"""
            ur"""(?P<movefrom>\((?P<fromX>\d)(?P<fromY>\d)\))?"""
            ur"""(?P<resign>投了)?"""
            + WSS + \
            ur"""(\("""
                ur"""\s*(?P<minutes>\d+):(?P<seconds>\d+)"""
                ur"""/"""
                ur"""((?P<hh>\d\d):(?P<mm>\d\d):(?P<ss>\d\d))?"""
            ur"""\))"""
            )

kanji2int = dict(
        zip(u"１２３４５６７８９", range(1, 10)) 
        + zip(u"一二三四五六七八九", range(1, 10)))


class Move:
    u"""
    ユーザは参照するモノ.
    ユーザが直接作ることはないです.

    公開インターフェース

    手数 move.nth: int
    コマの種類 move.piece: unicode string 
        歩, 香, 桂, 銀, 金, 角, 飛, 王, 玉, と, 成香, 成桂, 成銀, 馬, 竜のいづれか
    コマの到着X座標 move.toX: int or None if self.resign
    コマの到着Y座標 move.toY: int or None if self.resign
    コマの出発X座標 move.fromX: int or None if self.resign or self.place
    コマの出発Y座標 move.fromY: int or None if self.resign or self.place
    成りを行ったか否か move.promote: bool
    同~かであるか否か  move.same: bool
    投了であるか否か   move.resign: bool
    持ち駒を打ったか否か move.place: bool
    """

    def __init__(self, matchdict, prev):
        assert isinstance(matchdict, dict)
        self.matchdict = matchdict
        self.prev = prev

    def __getattr__(self, name):
        value = self.matchdict[name]
        if name in ('toX', 'toY'):
            if self.resign:
                return None
            if self.same:
                assert value is None
                assert isinstance(self.prev, Move)
                return getattr(self.prev, name)
            return kanji2int[value]
        elif name in ('nth',):
            return int(value)
        elif name in ('fromX', 'fromY'):
            if self.resign:
                return None
            if self.place:
                assert value is None
                return None
            return int(value)
        elif name in ('promote', 'same', 'place'):
            return bool(value)
        else:
            return value


class Parser:
    def __init__(self):
        self.prev = None

    def feed(self, uline):
        match = regexp.match(uline)
        if match is not None:
            move = Move(match.groupdict(), self.prev)
            self.prev = move
            return move
        return None


if __name__ == "__main__":
    import sys
    import codecs
    with codecs.open(sys.argv[2], 'r', encoding=sys.argv[1]) as f:
        p = Parser()
        for uline in f:
            print uline
            m = p.feed(uline)
            if m is not None:
                if m.resign:
                    print u"%3d resign"%(m.nth)
                elif m.place:
                    print u"%3d %4s (持駒) => (%1d,%1d) %s"%\
                            (m.nth, m.piece, m.toX, m.toY, m.promote)
                else:
                    print u"%3d %4s (%1d,%1d)  => (%1d,%1d) %s"%\
                            (m.nth, m.piece, m.fromX, m.fromY, m.toX, m.toY, m.promote)




