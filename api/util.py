#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Utility library containing various helpers used by the API.

Contains miscellaneous functions used internally by the API.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'


import document


CUSTOM_SERIALIZE_METHOD_NAME = 'Serialize'


def IsListOrDict(inst):
  """Returns whether or not this is a list, tuple, set or dict ."""
  return hasattr(inst, '__iter__')


def IsDict(inst):
  """Returns whether or not the specified instance is a dict."""
  return hasattr(inst, 'iteritems')


def IsInstance(obj):
  """Returns whether or not the specified instance is a user-defined type."""
  # NOTE(davidbyttow): This seems like a reasonably safe hack for now...
  # I'm not exactly sure how to test if something is a subclass of object.
  # And no, "is InstanceType" does not work here. :(
  return str(type(obj)).startswith('<class ')


def CollapseJavaCollections(data):
  """Collapses the unnecessary extra data structures in the wire format.

  Currently the wire format is built from marshalling of Java objects. This
  introduces overhead of extra key/value pairs with respect to collections and
  superfluous fields. As such, this method attempts to collapse those structures
  out of the data format by collapsing the collection objects and removing
  the java class fields.

  This preserves the data that is passed in and only removes the collection
  types.

  Args:
    data: Some arbitrary dict, list or primitive type.

  Returns:
    The same data structure with the collapsed and unnecessary objects
    removed.
  """
  if IsDict(data):
    java_class = data.get('javaClass')
    if java_class:
      del data['javaClass']
    if java_class == 'java.util.HashMap':
      return CollapseJavaCollections(data['map'])
    elif java_class == 'java.util.ArrayList':
      return CollapseJavaCollections(data['list'])
    for key, val in data.iteritems():
      data[key] = CollapseJavaCollections(val)
  elif IsListOrDict(data):
    for index in range(len(data)):
      data[index] = CollapseJavaCollections(data[index])
    return data
  return data


def ToLowerCamelCase(s):
  """Converts a string to lower camel case.

  Examples:
    foo => foo
    foo_bar => fooBar
    foo__bar => fooBar
    foo_bar_baz => fooBarBaz

  Args:
    s: The string to convert to lower camel case.

  Returns:
    The lower camel cased string.
  """
  upper_cased = ToUpperCamelCase(s)
  return upper_cased[:1].lower() + upper_cased[1:]


def ToUpperCamelCase(s):
  """Converts a string to upper camel case.

  Examples:
    foo => Foo
    foo_bar => FooBar
    foo__bar => FooBar
    foo_bar_baz => FooBarBaz

  Args:
    s: The string to convert to upper camel case.

  Returns:
    The upper camel cased string.
  """
  return ''.join(fragment.capitalize() for fragment in s.split('_'))


def DefaultKeyWriter(key_name):
  """This key writer rewrites keys as lower camel case.

  Expects that the input is formed by '_' delimited words.

  Args:
    key_name: Name of the key to serialize.

  Returns:
    Key name in lower camel-cased form.
  """
  return ToLowerCamelCase(key_name)


def _SerializeAttributes(obj, key_writer=DefaultKeyWriter):
  """Serializes attributes of an instance.

  Iterates all attributes of an object and invokes serialize if they are
  public and not callable.

  Args:
    obj: The instance to serialize.
    key_writer: Optional function that takes a string key and optionally mutates
        it before serialization. For example:

        def randomize(key_name):
          return key_name += str(random.random())

  Returns:
    The serialized object.
  """
  data = {}
  for attr_name in dir(obj):
    if attr_name.startswith('_'):
      continue
    attr = getattr(obj, attr_name)
    if callable(attr):
      continue
    if attr is None:
      continue
    # Looks okay, serialize it.
    data[key_writer(attr_name)] = Serialize(attr)
  return data


def _SerializeList(l):
  """Invokes Serialize on all of its elements.

  Args:
    l: The list object to serialize.

  Returns:
    The serialized list.
  """
  data = [Serialize(v) for v in l]
  return {
      'javaClass': 'java.util.ArrayList',
      'list': data
  }


def _SerializeDict(d, key_writer=DefaultKeyWriter):
  """Invokes serialize on all of its key/value pairs.

  Args:
    d: The dict instance to serialize.
    key_writer: Optional key writer function.

  Returns:
    The serialized dict.
  """
  data = {}
  for k, v in d.iteritems():
    data[key_writer(k)] = Serialize(v)
  return {
      'javaClass': 'java.util.HashMap',
      'map': data
  }


def Serialize(obj, key_writer=DefaultKeyWriter):
  """Serializes any instance.

  If this is a user-defined instance
  type, it will first check for a custom Serialize() function and use that
  if it exists. Otherwise, it will invoke serialize all of its public
  attributes. Lists and dicts are serialized trivially.

  Args:
    obj: The instance to serialize.
    key_writer: Optional key writer function.

  Returns:
    The serialized object.
  """
  if IsInstance(obj):
    if obj and hasattr(obj, CUSTOM_SERIALIZE_METHOD_NAME):
      method = getattr(obj, CUSTOM_SERIALIZE_METHOD_NAME)
      if callable(method):
        return method()
    return _SerializeAttributes(obj, key_writer)
  elif IsDict(obj):
    return _SerializeDict(obj, key_writer)
  elif IsListOrDict(obj):
    return _SerializeList(obj)
  return obj


def ClipRange(r, clip_range):
  """Clips one range to another.

  Given a range to be clipped and a clipping range, will result in a list
  of 0-2 new ranges. If the range is completely inside of the clipping range
  then an empty list will be returned. If it is completely outside, then
  a list with only the same range will be returned.

  Otherwise, other permutations may result in a single clipped range or
  two ranges that were the result of a split.

  Args:
    r: The range to be clipped.
    clip_range: The range that is clipping the other.

  Returns:
    A list of 0-2 ranges as a result of performing the clip.
  """
  # Check if completely outside the clipping range.
  if r.end <= clip_range.start or r.start >= clip_range.end:
    return [r]
  # Check if completely clipped.
  if r.start >= clip_range.start and r.end <= clip_range.end:
    return []
  # Check if split.
  if clip_range.start >= r.start and clip_range.end <= r.end:
    splits = []
    if r.start < clip_range.start:
      splits.append(document.Range(r.start, clip_range.start))
    if clip_range.end < r.end:
      splits.append(document.Range(clip_range.end, r.end))
    return splits
  # Just a trim.
  if clip_range.start < r.start:
    return [document.Range(clip_range.end, r.end)]
  return [document.Range(r.start, clip_range.start)]
