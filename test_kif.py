#!/usr/bin/python
# -*- coding=utf8 -*-

import unittest
import codecs

import kif

class TestParser(unittest.TestCase):
    def test_new(self):
        p = kif.Parser()
        self.assertEqual(codecs.lookup('utf8'), codecs.lookup(p.encoding))

    def test_feed_1(self):
        p = kif.Parser()
        line = "   1 ７六歩(77)   ( 0:3/)"
        got = p.feed(line)
        self.assertEqual(1, got.nth)
        self.assertEqual(7, got.toX)
        self.assertEqual(6, got.toY)
        self.assertEqual(7, got.fromX)
        self.assertEqual(7, got.fromY)
        self.assertEqual('Pawn', got.piece)
        self.assertFalse(got.promote)

    def test_feed_2(self):
        p = kif.Parser()
        line = "   6 ４二飛(82)   ( 0:4/)"
        got = p.feed(line)
        self.assertEqual(6, got.nth)
        self.assertEqual(4, got.toX)
        self.assertEqual(2, got.toY)
        self.assertEqual(8, got.fromX)
        self.assertEqual(2, got.fromY)
        self.assertEqual('Rook', got.piece)
        self.assertFalse(got.promote)

    def test_feed_promotion(self):
        p = kif.Parser()
        line = "  58 ９七桂成(85)   ( 0:2/)"
        got = p.feed(line)
        self.assertEqual(6, got.nth)
        self.assertEqual(4, got.toX)
        self.assertEqual(2, got.toY)
        self.assertEqual(8, got.fromX)
        self.assertEqual(2, got.fromY)
        self.assertEqual('Knite', got.piece)
        self.assert_(got.promote)

    def test_feed_same(self):
        p = kif.Parser()
        line0 = "  66 ２六角(44)   ( 0:16/)"
        got = p.feed(line0)
        line1 = "  67 同　飛(28)   ( 0:2/)"
        got = p.feed(line1)
        self.assertEqual(66, got.nth)
        self.assertEqual(2, got.toX)
        self.assertEqual(6, got.toY)
        self.assertEqual(2, got.fromX)
        self.assertEqual(8, got.fromY)
        self.assertEqual('Rook', got.piece)
        self.assertFalse(got.promote)

    def test_feed_place(self):
        p = kif.Parser()
        line = '  61 ６四歩打   ( 0:12/)'
        got = p.feed(line)
        self.assertEqual(61, got.nth)
        self.assertEqual(6, got.toX)
        self.assertEqual(4, got.toY)
        self.assertIsNone(got.fromX)
        self.assertIsNone(got.fromY)
        self.assertEqual('pawn', got.piece)
        self.assertFalse(got.promote)

    def test_feed_resign(self):
        p = kif.Parser()
        line = ' 131 投了   ( 0:2/)'
        got = p.feed(line)
        self.assertEqual(131, got.nth)
        self.assertIsNone(got.toX)
        self.assertIsNone(got.toY)
        self.assertIsNone(got.fromX)
        self.assertIsNone(got.fromY)
        self.assertIsNone(got.piece)
        self.assertFalse(got.promote)
        self.assert_(got.resign)



if __name__ == "__main__":
    unittest.main()

