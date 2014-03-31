#!/usr/bin/python
# -*- coding=utf8 -*-

import unittest
import codecs

import kif

class TestParser(unittest.TestCase):
    def test_new(self):
        p = kif.Parser()
        self.assertEqual(codecs.lookup('utf8'), codecs.lookup(p.encoding))


if __name__ == "__main__":
    unittest.main()


