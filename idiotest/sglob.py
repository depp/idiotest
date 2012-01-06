# Copyright 2009 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
from __future__ import absolute_import
__all__ = ['SGlob']
import re

VALID_PART = re.compile('[A-Za-z_0-9?*]*$')
MULTI_PART = re.compile('.*\\*\\*')

class Part(object):
    def __init__(self, regexp):
        self.regexp = regexp

class SimplePart(Part):
    def prefix_match(self, val):
        if not val:
            return True
        if self.regexp.match(val[0]):
            return self.next.prefix_match(val[1:])
        return False
    def full_match(self, val):
        if not val:
            return False
        if self.regexp.match(val[0]):
            return self.next.full_match(val[1:])
        return False

class MultiPart(Part):
    def prefix_match(self, val):
        return True
    def full_match(self, val):
        for n in xrange(len(val) + 1):
            if (self.regexp.match('.'.join(val[:n]))
                and self.next.full_match(val[:n])):
                return True
        return False

class EndPart(object):
    def prefix_match(self, val):
        return True
    def full_match(self, val):
        return True

STAR = re.compile('\\*+')
QMARK = re.compile('\\?')

def _starsub(m):
    if len(m.group(0)) > 1:
        return '.*'
    return '[^.]*'

def _mkpart(p):
    if not VALID_PART.match(p):
        raise Exception('Invalid pattern: %s' % repr(p))
    regexp = STAR.sub(_starsub, p);
    regexp = QMARK.sub('[^.]', regexp)
    regexp = re.compile(regexp + '$')
    if MULTI_PART.match(p):
        return MultiPart(regexp)
    return SimplePart(regexp)

def _mkpat(str):
    ps = [_mkpart(p) for p in str.split('.')]
    e = EndPart()
    while ps:
        p = ps.pop()
        p.next = e
        e = p
    return e

class SGlob(object):
    def __init__(self, strs):
        self.pats = [_mkpat(s) for s in strs]
    def prefix_match(self, str):
        parts = str.split('.')
        for pat in self.pats:
            if pat.prefix_match(parts):
                return True
    def full_match(self, str):
        parts = str.split('.')
        for pat in self.pats:
            if pat.full_match(parts):
                return True
