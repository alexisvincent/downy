#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Unit tests for the util module."""


__author__ = 'davidbyttow@google.com (David Byttow)'


import unittest

import document
import util


class TestUtils(unittest.TestCase):
  """Tests utility functions."""

  def testIsListOrDict(self):
    self.assertTrue(util.IsListOrDict([]))
    self.assertTrue(util.IsListOrDict({}))
    self.assertTrue(util.IsListOrDict(set()))
    self.assertTrue(util.IsListOrDict(()))
    self.assertFalse(util.IsListOrDict(42))
    self.assertFalse(util.IsListOrDict('list?'))
    self.assertFalse(util.IsListOrDict(object))

  def testIsDict(self):
    self.assertFalse(util.IsDict([]))
    self.assertTrue(util.IsDict({}))
    self.assertFalse(util.IsDict(set()))
    self.assertFalse(util.IsDict(()))
    self.assertFalse(util.IsDict(42))
    self.assertFalse(util.IsDict('dict?'))
    self.assertFalse(util.IsDict(object))

  def testIsInstance(self):
    class OldClass:
      pass

    class NewClass(object):
      pass

    self.assertFalse(util.IsInstance(OldClass()))
    self.assertTrue(util.IsInstance(NewClass()))
    self.assertFalse(util.IsInstance({}))
    self.assertFalse(util.IsInstance(()))
    self.assertFalse(util.IsInstance(42))
    self.assertFalse(util.IsInstance('instance?'))

  def testCollapseJavaCollections(self):
    def MakeList(e0=1):
      return {
          'javaClass': 'java.util.ArrayList',
          'list': [e0, 2, 3]
      }

    def MakeMap(v='value'):
      return {
          'javaClass': 'java.util.HashMap',
          'map': {'key': v}
      }

    l = util.CollapseJavaCollections(MakeList())
    self.assertEquals(2, l[1])

    m = util.CollapseJavaCollections(MakeMap())
    self.assertEquals('value', m['key'])

    nested = util.CollapseJavaCollections(MakeMap(MakeList(MakeMap())))
    self.assertEquals('value', nested['key'][0]['key'])

  def testToLowerCamelCase(self):
    self.assertEquals('foo', util.ToLowerCamelCase('foo'))
    self.assertEquals('fooBar', util.ToLowerCamelCase('foo_bar'))
    self.assertEquals('fooBar', util.ToLowerCamelCase('foo__bar'))
    self.assertEquals('fooBarBaz', util.ToLowerCamelCase('foo_bar_baz'))
    self.assertEquals('f', util.ToLowerCamelCase('f'))
    self.assertEquals('f', util.ToLowerCamelCase('f_'))
    self.assertEquals('', util.ToLowerCamelCase(''))
    self.assertEquals('', util.ToLowerCamelCase('_'))
    self.assertEquals('aBCDEF', util.ToLowerCamelCase('_a_b_c_d_e_f_'))

  def testToUpperCamelCase(self):
    self.assertEquals('Foo', util.ToUpperCamelCase('foo'))
    self.assertEquals('FooBar', util.ToUpperCamelCase('foo_bar'))
    self.assertEquals('FooBar', util.ToUpperCamelCase('foo__bar'))
    self.assertEquals('FooBarBaz', util.ToUpperCamelCase('foo_bar_baz'))
    self.assertEquals('F', util.ToUpperCamelCase('f'))
    self.assertEquals('F', util.ToUpperCamelCase('f_'))
    self.assertEquals('', util.ToUpperCamelCase(''))
    self.assertEquals('', util.ToUpperCamelCase('_'))
    self.assertEquals('ABCDEF', util.ToUpperCamelCase('_a_b_c_d_e_f_'))

  def assertListsEqual(self, a, b):
    self.assertEquals(len(a), len(b))
    for i in range(len(a)):
      self.assertEquals(a[i], b[i])

  def assertDictsEqual(self, a, b):
    self.assertEquals(len(a.keys()), len(b.keys()))
    for k, v in a.iteritems():
      self.assertEquals(v, b[k])

  def testSerializeList(self):
    data = [1, 2, 3]
    output = util.Serialize(data)
    self.assertEquals('java.util.ArrayList', output['javaClass'])
    self.assertListsEqual(data, output['list'])

  def testSerializeDict(self):
    data = {'key': 'value'}
    output = util.Serialize(data)
    self.assertEquals('java.util.HashMap', output['javaClass'])
    self.assertDictsEqual(data, output['map'])

  def testSerializeAttributes(self):

    class Data(object):
      java_class = 'json.org.JSONObject'

      def __init__(self):
        self.public = 1
        self._protected = 2
        self.__private = 3

      def Func(self):
        pass

    data = Data()
    output = util.Serialize(data)
    # Functions and non-public fields should not be serialized.
    self.assertEquals(2, len(output.keys()))
    self.assertEquals(Data.java_class, output['javaClass'])
    self.assertEquals(data.public, output['public'])

  def testClipRange(self):
    def R(x, y):
      return document.Range(x, y)

    def Test(test_range, clipping_range, expected):
      ret = util.ClipRange(test_range, clipping_range)
      self.assertEquals(len(expected), len(ret))
      for i in range(len(ret)):
        self.assertEquals(expected[i].start, ret[i].start)
        self.assertEquals(expected[i].end, ret[i].end)

    # completely out
    Test(R(0, 1), R(2, 3), [R(0, 1)])
    # completely out
    Test(R(3, 4), R(2, 3), [R(3, 4)])
    # completely in
    Test(R(2, 3), R(1, 4), [])
    # completely in
    Test(R(1, 4), R(1, 4), [])
    # tRim left
    Test(R(1, 3), R(2, 4), [R(1, 2)])
    # tRim Right
    Test(R(2, 4), R(1, 3), [R(3, 4)])
    # split with two
    Test(R(1, 4), R(2, 3), [R(1, 2), R(3, 4)])
    # split with one
    Test(R(1, 4), R(1, 3), [R(3, 4)])


if __name__ == '__main__':
  unittest.main()
