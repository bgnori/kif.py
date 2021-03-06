#!/usr/bin/python
# -*- coding=utf8 -*-


u"""
概要:
柿木将棋フォーマットをparseするライブラリです.
将棋やる人は日本語読めるだろうから日本語で書いています.

使い方

file最後のif __name__ ~内を参照のこと

正規表現とか仕様に関して次のページを起点に作成を行った.
御礼申し上げます.
http://openlabo.blogspot.jp/2013/09/blog-post_16.html

To Do:
 * ヘッダへの対応
 * 変化分岐への対応
"""


import re

WSS = ur"""[ \t\v　]*""" #最後は全角スペース!
MOVE = re.compile(WSS+ ur"""(?P<nth>\d+)"""
            + WSS + \
            ur"""(?P<moveto>"""
                ur"""((?P<toX>[１２３４５６７８９])(?P<toY>[一二三四五六七八九]))"""
                ur"""|(?P<same>同)"""
            ur""")?"""
            + WSS + \
            ur"""(?P<piece>歩|成?香|成?桂|成?銀|金|角|飛|王|玉|と|馬|竜|龍)?"""
            ur"""(?P<promote>成)?"""
            ur"""(?P<place>打)?"""
            ur"""(?P<movefrom>\((?P<fromX>\d)(?P<fromY>\d)\))?"""
            ur"""(?P<resign>投了)?"""
            ur"""(?P<timeup>切れ負け)?"""
            ur"""(?P<illeagal>反則手)?"""
            + WSS + \
            ur"""(\("""
                ur"""\s*(?P<minutes>\d+):(?P<seconds>\d+)"""
                ur"""/"""
                ur"""((?P<hh>\d\d):(?P<mm>\d\d):(?P<ss>\d\d))?"""
            ur"""\))"""
            )

COLON = ur"""[:：]""" #2つめは全角

def make_header(uhdname, uhdbody):
    u"""2つめは全角"""
    return u"(" + uhdname + u"""[:：]""" + uhdbody + u")"


HEADER_PATTERN = u"|".join((
    make_header(u"記録ID", ur"(?P<record_id>.+$)"),
    make_header(u"対局ID", ur"(?P<match_id>.+$)"),
    make_header(u"開始日時", ur"(?P<start_datetime_year>\d\d\d\d)/(?P<start_datetime_month>\d\d)/(?P<start_datetime_day>\d\d)"),
    make_header(u"終了日時", ur"(?P<finish_datetime_year>\d\d\d\d)/(?P<finish_datetime_month>\d\d)/(?P<finish_datetime_day>\d\d)"),
    make_header(u"場所", ur"(?P<venue>.+$)"),
    make_header(u"持ち時間", ur"((?P<tc_initial>\d+)分\+(?P<tc_post>\d+)秒|(?P<tc_human_readable>.+$))"),
    make_header(u"手合割", ur"(?P<handicap>(?P<handicap_human_readable>.+$))"),
    make_header(u"先手", ur"(?P<white>\w+)"),
    make_header(u"後手", ur"(?P<black>\w+)"),
    make_header(u"消費時間", ur"(?P<time_comsumed>\w+)"),
    make_header(u"表題", ur"(?P<title>\w+)"),
    make_header(u"棋戦", ur"(?P<tourney>\w+)"),
    ))
HEADER = re.compile(HEADER_PATTERN)

kanji2int = dict(
        zip(u"１２３４５６７８９", range(1, 10)) 
        + zip(u"一二三四五六七八九", range(1, 10)))


COMMENT_PATTERN = ur"\*(?P<comment>.*$)"

COMMENT = re.compile(COMMENT_PATTERN)

BRANCH_PATTERN = make_header(u"変化", ur"(?P<nth>\d+)手")
#変化：103手

BRANCH = re.compile(BRANCH_PATTERN)



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
    切れ負けであるか否か move.timeup: bool
    持ち駒を打ったか否か move.place: bool
    """

    def __init__(self, matchdict, prev):
        assert isinstance(matchdict, dict)
        self.matchdict = matchdict
        self.prev = prev
        self.next = None

    def __unicode__(self):
        if self.resign:
            return u"%3d resign"%(self.nth)
        elif self.illeagal:
            return u"%3d illeagal"%(self.nth)
        elif self.timeup:
            return u"%3d timeup"%(self.nth)
        elif self.place:
            return u"%3d %4s (持駒) => (%1d,%1d) %s"%\
                    (self.nth, self.piece, self.toX, self.toY, self.promote)
        else:
            assert isinstance(self.fromX, int)
            assert isinstance(self.fromY, int)
            assert isinstance(self.toX, int)
            assert isinstance(self.toY, int)
            return u"%3d %4s (%1d,%1d)  => (%1d,%1d) %s"%\
                    (self.nth, self.piece, self.fromX, self.fromY, self.toX, self.toY, self.promote)

    def __repr__(self):
        return "< Move nth=%d...>"%(self.nth,)

    def __getattr__(self, name):
        value = self.matchdict[name]
        if name in ('toX', 'toY'):
            if self.resign:
                return None
            if self.illeagal:
                return None
            if self.timeup:
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
            if self.illeagal:
                return None
            if self.timeup:
                return None
            if self.place:
                assert value is None
                return None
            return int(value)
        elif name in ('promote', 'same', 'place', 'resign', 'timeup'):
            return bool(value)
        else:
            return value

class Line:
    def __init__(self, branch_from):
        self.branch_from = branch_from
        self.head = None
        self.moves = {}
        self.prev = None
        self.is_closed = False

    def add_comment(self, ustr):
        assert isinstance(ustr, unicode)
        self.prev.comment.append(ustr)

    def add_move(self, d):
        move = Move(d, self.prev)
        if self.head is None:
            self.head = move
        elif isinstance(self.prev, Move):
            self.prev.next = move
        if move.resign or move.illeagal or move.timeup:
            self.is_closed = True
        self.moves[move.nth] = move
        self.prev = move
        return move

    def __iter__(self):
        next = self.head
        while isinstance(next, Move):
            yield next
            next = next.next


class Parser:
    def __init__(self):
        self.lines = dict(mainline=Line(None))
        self.headers = {}
        self.current_line_name = u'mainline'

    @property
    def current_line(self):
        return self.lines[self.current_line_name]

    def parse(self, f):
        for uline in f:
            self.feed(uline)

    def feed(self, uline):
        line = self.current_line

        found = COMMENT.match(uline)
        if found is not None:
            line.add_comment(found.group('comment'))
            return None

        found = MOVE.match(uline)
        if found is not None:
            return line.add_move(found.groupdict())

        found = HEADER.match(uline)
        if found is not None:
            d = found.groupdict()
            for k, v in d.items():
                if v is not None:
                    self.headers[k] = v
            return None

        found = BRANCH.match(uline)
        if found is not None:
            print 'making line', found
            b = Line(self.current_line)
            nth = found.group('nth')
            self.lines[nth] = b
            b.prev = self.current_line.moves[int(nth)].prev

            self.current_line_name = nth

        return None


if __name__ == "__main__":
    import sys
    import codecs
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    with codecs.open(sys.argv[2], 'r', encoding=sys.argv[1]) as f:
        p = Parser()
        p.parse(f)
        print p.headers
        print p.lines.keys()
        print p.current_line_name
        for k, v in p.lines.items():
            print 'in branch:', k
            for m in v:
                print unicode(m)



