#!/usr/bin/python
# -*- coding=utf8 -*-


"""
thanks to http://openlabo.blogspot.jp/2013/09/blog-post_16.html
"""

import re

WSS = ur"""[ \t\v　]*"""
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
            ur"""(\(\s*(?P<minutes>\d+):(?P<seconds>\d+/)\))"""
            )

kanji2int = dict(
        zip(u"１２３４５６７８９", range(1, 10)) 
        + zip(u"一二三四五六七八九", range(1, 10)))


u"""
piece2id>
    歩
    香
    桂
    銀
    金
    角
    飛
    王
    玉
    と馬竜)?"""

class Move:
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
        self.encoding = 'utf8'
        self.prev = None

    def feed(self, uline):
        match = regexp.match(uline)
        if match is not None:
            move = Move(match.groupdict(), self.prev)
            self.prev = move
            return move
        assert False
        return None


