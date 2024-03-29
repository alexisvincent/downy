#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Unit tests for the document module."""


__author__ = 'davidbyttow@google.com (David Byttow)'


import unittest

import document
import util


class TestRange(unittest.TestCase):
  """Tests for the document.Range class."""

  def testDefaults(self):
    r = document.Range()
    self.assertEquals(0, r.start)
    self.assertEquals(1, r.end)

  def testValidRanges(self):
    r = document.Range(1, 2)
    self.assertEquals(1, r.start)
    self.assertEquals(2, r.end)

  def testInvalidRanges(self):
    self.assertRaises(ValueError, document.Range, 1, 0)
    self.assertRaises(ValueError, document.Range, 0, -1)
    self.assertRaises(ValueError, document.Range, 3, 1)

  def testCollapsedRanges(self):
    self.assertTrue(document.Range(0, 0).IsCollapsed())
    self.assertTrue(document.Range(1, 1).IsCollapsed())


class TestAnnotation(unittest.TestCase):
  """Tests for the document.Annotation class."""

  def testDefaults(self):
    annotation = document.Annotation('key', 'value')
    self.assertEquals(document.Range().start, annotation.range.start)
    self.assertEquals(document.Range().end, annotation.range.end)

  def testFields(self):
    annotation = document.Annotation('key', 'value', document.Range(2, 3))
    self.assertEquals('key', annotation.name)
    self.assertEquals('value', annotation.value)
    self.assertEquals(2, annotation.range.start)
    self.assertEquals(3, annotation.range.end)


class TestElement(unittest.TestCase):
  """Tests for the document.Element class."""

  def testProperties(self):
    element = document.Element(document.ELEMENT_TYPE.GADGET,
                               key='value')
    self.assertEquals('value', element.key)

  def testFormElement(self):
    element = document.FormElement(document.ELEMENT_TYPE.INPUT, 'input', label='label')
    self.assertEquals(document.ELEMENT_TYPE.INPUT, element.type)
    self.assertEquals(element.value, '')
    self.assertEquals(element.name, 'input')
    self.assertEquals(element.label, 'label')

  def testImage(self):
    image = document.Image('http://test.com/image.png', width=100, height=100)
    self.assertEquals(document.ELEMENT_TYPE.IMAGE, image.type)
    self.assertEquals(image.url, 'http://test.com/image.png')
    self.assertEquals(image.width, 100)
    self.assertEquals(image.height, 100)

  def testGadget(self):
    gadget = document.Gadget('http://test.com/gadget.xml')
    self.assertEquals(document.ELEMENT_TYPE.GADGET, gadget.type)
    self.assertEquals(gadget.url, 'http://test.com/gadget.xml')

  def testSerialize(self):
    image = document.Image('http://test.com/image.png', width=100, height=100)
    s = util.Serialize(image)
    k = s.keys()
    k.sort()
    # we should really only have three things to serialize
    self.assertEquals(['java_class', 'properties', 'type'], k)
    self.assertEquals(s['properties']['javaClass'], 'java.util.HashMap')
    props = s['properties']['map']
    self.assertEquals(len(props), 3)
    self.assertEquals(props['url'], 'http://test.com/image.png')
    self.assertEquals(props['width'], 100)
    self.assertEquals(props['height'], 100)


if __name__ == '__main__':
  unittest.main()
