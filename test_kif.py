#!/usr/bin/python
# -*- coding=utf8 -*-

import unittest
import codecs

import kif

class TestParser(unittest.TestCase):
    def test_new(self):
        p = kif.Parser()
        self.assertIsNone(p.current_line.prev)

    def test_feed_1(self):
        p = kif.Parser()
        uline = u"   1 ７六歩(77)   ( 0:3/)"
        got = p.feed(uline)
        self.assertIsNotNone(got)
        self.assertEqual(1, got.nth)
        self.assertEqual(7, got.toX)
        self.assertEqual(6, got.toY)
        self.assertEqual(7, got.fromX)
        self.assertEqual(7, got.fromY)
        self.assertEqual(u'歩', got.piece)
        self.assertFalse(got.promote)
        self.assertFalse(got.timeup)
        self.assertFalse(got.resign)

    def test_feed_2(self):
        p = kif.Parser()
        uline = u"   6 ４二飛(82)   ( 0:4/)"
        got = p.feed(uline)
        self.assertIsNotNone(got)
        self.assertEqual(6, got.nth)
        self.assertEqual(4, got.toX)
        self.assertEqual(2, got.toY)
        self.assertEqual(8, got.fromX)
        self.assertEqual(2, got.fromY)
        self.assertEqual(u'飛', got.piece)
        self.assertFalse(got.promote)
        self.assertFalse(got.timeup)
        self.assertFalse(got.resign)

    def test_feed_promotion(self):
        p = kif.Parser()
        uline = u"  58 ９七桂成(85)   ( 0:2/)"
        got = p.feed(uline)
        self.assertIsNotNone(got)
        self.assertEqual(58, got.nth)
        self.assertEqual(9, got.toX)
        self.assertEqual(7, got.toY)
        self.assertEqual(8, got.fromX)
        self.assertEqual(5, got.fromY)
        self.assertEqual(u'桂', got.piece)
        self.assert_(got.promote)
        self.assertFalse(got.timeup)
        self.assertFalse(got.resign)

    def test_feed_same_a(self):
        p = kif.Parser()
        uline0 = u"  66 ２六角(44)   ( 0:16/)"
        f = p.feed(uline0)
        self.assertIsNotNone(f)
        self.assertIsNotNone(p.current_line.prev)
        self.assertEqual(id(p.current_line.prev), id(f))
        uline1 = u"  67 同　飛(28)   ( 0:2/)"
        got = p.feed(uline1)
        self.assertIsNotNone(got)
        self.assertIsNotNone(p.current_line.prev)
        self.assertEqual(id(f), id(got.prev))
        self.assert_(got.same)
        self.assertEqual(67, got.nth)
        self.assertEqual(2, got.toX)
        self.assertEqual(6, got.toY)
        self.assertEqual(2, got.fromX)
        self.assertEqual(8, got.fromY)
        self.assertEqual(u'飛', got.piece)
        self.assertFalse(got.promote)
        self.assertFalse(got.timeup)
        self.assertFalse(got.resign)

    def test_feed_same_b(self):
        p = kif.Parser()
        uline0 = u"  66 ２六角(44)   ( 0:16/)"
        f = p.feed(uline0)
        self.assertIsNotNone(f)
        self.assertIsNotNone(p.current_line.prev)
        self.assertEqual(id(p.current_line.prev), id(f))
        uline1 = u" 67 同成桂(67)   ( 0:0/)"
        got = p.feed(uline1)
        self.assertIsNotNone(got)
        self.assertIsNotNone(p.current_line.prev)
        self.assertEqual(id(f), id(got.prev))
        self.assert_(got.same)
        self.assertEqual(67, got.nth)
        self.assertEqual(2, got.toX)
        self.assertEqual(6, got.toY)
        self.assertEqual(6, got.fromX)
        self.assertEqual(7, got.fromY)
        self.assertEqual(u'成桂', got.piece)
        self.assertFalse(got.promote)
        self.assertFalse(got.timeup)
        self.assertFalse(got.resign)


    def test_feed_place(self):
        p = kif.Parser()
        uline = u"  61 ６四歩打   ( 0:12/)"
        got = p.feed(uline)
        self.assertIsNotNone(got)
        self.assert_(got.place)
        self.assertEqual(61, got.nth)
        self.assertEqual(6, got.toX)
        self.assertEqual(4, got.toY)
        self.assertIsNone(got.fromX)
        self.assertIsNone(got.fromY)
        self.assertEqual(u'歩', got.piece)
        self.assertFalse(got.promote)
        self.assertFalse(got.timeup)
        self.assertFalse(got.resign)

    def test_feed_resign(self):
        p = kif.Parser()
        uline = u" 131 投了   ( 0:2/)"
        got = p.feed(uline)
        self.assertIsNotNone(got)
        self.assertEqual(131, got.nth)
        self.assertIsNone(got.toX)
        self.assertIsNone(got.toY)
        self.assertIsNone(got.fromX)
        self.assertIsNone(got.fromY)
        self.assertIsNone(got.piece)
        self.assertFalse(got.promote)
        self.assertFalse(got.timeup)
        self.assert_(got.resign)

    def test_feed_timeup(self):
        p = kif.Parser()
        uline = u" 131 切れ負け   ( 0:2/)"
        got = p.feed(uline)
        self.assertIsNotNone(got)
        self.assertEqual(131, got.nth)
        self.assertIsNone(got.toX)
        self.assertIsNone(got.toY)
        self.assertIsNone(got.fromX)
        self.assertIsNone(got.fromY)
        self.assertIsNone(got.piece)
        self.assertFalse(got.promote)
        self.assertFalse(got.resign)
        self.assert_(got.timeup)

    def test_comment(self):
        p = kif.Parser()
        uline = u"   1 ７六歩(77)   ( 0:3/)"
        got = p.feed(uline)
        self.assertIsNotNone(got)
        self.assertEqual(1, got.nth)
        self.assertEqual(7, got.toX)
        self.assertEqual(6, got.toY)
        self.assertEqual(7, got.fromX)
        self.assertEqual(7, got.fromY)
        self.assertEqual(u'歩', got.piece)
        self.assertFalse(got.promote)
        self.assertFalse(got.timeup)
        self.assertFalse(got.resign)


if __name__ == "__main__":
    unittest.main()

