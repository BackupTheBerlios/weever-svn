#!/usr/bin/python

# Napalm
#
# Author: Valentino Volonghi (dialtone [at] divmod.com)
#
# License: MIT
#
# The basic interface was borrowed from Python-Markdown to allow
# intechangeability without many efforts. besides this module is
# called napalm and not markdown.
#
# Version: 0.0.1

import re
import sys
import os
import warnings
warnings.filterwarnings('ignore', '', DeprecationWarning)

from nevow import tags as t

regExp = {
    'reference-def' : re.compile(r'^(  )?\[([^\]]*)\]:\s*([^ ]*)(.*)'),
    'header':         re.compile(r'^(#*)([^#]*)(#*)$'),
    'listitem':       re.compile(r'^(\*|[\d]*\.)\t(.*)'),
    'nestedlistitem': re.compile(r'^(\t)+(\*|[\d]*\.)\t(.*)'),
    'backtick':       re.compile(r'^([^\`]*)\`([^\`]*)\`(.*)$'),
    'escape':         re.compile(r'^([^\\]*)\\(.)(.*)$'),
    'emphasis':       re.compile(r'^([^\*]*)\*([^\*]*)\*(.*)$|^([^\_]*)\_([^\_]*)\_(.*)$'),
    'link':           re.compile(r'^([^\[]*)[ ]*\[(.*)\]\(([^\s]*)(\s+(.*))?\)(.*)$'),
    'reference-use':  re.compile(r'^([^\[]*)\[([^\]]*)\]\s*\[([^\]]*)\](.*)$'),
    'strong':         re.compile(r'^([^\*]*)\*\*(.*)\*\*([^\*]*)$|^([^\_]*)\_\_(.*)\_\_([^\_]*)$'),
    'containsline':   re.compile(r'^([-]*)$|^([=]*)$', re.M),
    'o-liststart':    re.compile(r'^[\d]*\.'),
    'u-liststart':    re.compile(r'^(\*|\+|\-)\t+(.*)'),
    'isline':         re.compile(r'^(\**)$|^([-]*)$|^(\*[ ]?){3,}')
}

class MarkdownParser(object):
    def __init__(self, text):
        t = text.strip()
        self.references = {}
        self.last_item = ''
        self.text = self._preprocess(t) 

    def _preprocess(self, text):
        t = text.replace("\r\n", "\n").replace("\r", "\n").split('\n')
        preprocessed_text = []
        for line in t:
            m = regExp['reference-def'].match(line)
            if m:
                self.references[m.group(2)] = (m.group(3), m.group(4).strip())
            else:
                preprocessed_text.append(line.rstrip())
        return preprocessed_text
    
    def parse(self):
        #body = t.div(class_="markdown")
        #return body[self._parse(self.text)]
        return self._parse(self.text)

    def _parse(self, lines):
        content = []
        current_block = []
        for line in lines:
            # Every line has already been stripped during
            # preprocessing. No need to repeat myself
            if line == '':
                content.append(self._handleBlock(current_block))
                current_block = []
            else:
                current_block.append(line)
        if current_block != []:
            content.append(self._handleBlock(current_block))
        return content
        
    def _handleBlock(self, current_block, noinline=False):
        if not len(current_block) or current_block[0].strip() == '':
            return ''

        if current_block[0].startswith('#'):
            return self._handleHeader(' '.join(current_block))
        
        elif current_block[0].startswith('    '):
            stripped_block = [line[4:] for line in current_block]
            if stripped_block:
                return t.pre[
                           t.code[
                               self._handleBlock(stripped_block, True)
                           ]
                       ]
            return ''

        elif current_block[0].startswith("> "):
            unquoted_block = []
            for line in current_block:
                if line.startswith("> "):
                    unquoted_block.append(line[2:])
                elif line == '>':
                    unquoted_block.append('')
                else:
                    unquoted_block.append(line)
            return t.blockquote[self._parse(unquoted_block)]

        elif self._isLine(current_block):
            return t.hr

        elif regExp['u-liststart'].match(current_block[0]):
            return t.ul[
                       [item for item in self._handleListitems(current_block)]
                   ]

        elif regExp['o-liststart'].match(current_block[0]):
            return t.ol[
                       [item for item in self._handleListitems(current_block)]
                   ]


        # header
        lineMatch = regExp['containsline'].search(current_block[0])
        if lineMatch and (lineMatch.group(1) or lineMatch.group(2)):
            try:
                if current_block[1].startswith('='):
                    return self._handleHeader('#'+current_block[0])
                elif current_block[1].startswith('-'):
                    return self._handleHeader('##'+current_block[0])
            except IndexError, e:
                raise IndexError("Weird Header")
            return ''
        # this is a block with no inline elements
        elif noinline:
            return '\n'.join(current_block)
        # this is a paragraph
        return self._handleParagraph(current_block, noinline)
        
    def _handleParagraph(self, block, noinline=False):
        par = t.p
        for line in block:
            if line.strip():
                if noinline:
                    return t.p[line.strip()]
                else:
                    for item in self._handleInline(line):
                        par = par[item]
        return par

    def _handleInline(self, line):
        if line.endswith('  '):
            l = self._handleInline(line.rstrip()) or []
            return l.append(t.br)

        m = regExp['link'].match(line)
        if m is not None:
            ll = self._handleInline(m.group(1)) or []
            lr = self._handleInline(m.group(6)) or []
            a = t.a(href=m.group(3))[m.group(2)]
            if m.group(5):
                a = a(title=m.group(5)[1:-1])
            ll.append(a)
            ll.extend(lr)
            return ll
        
        m = regExp['reference-use'].match(line)
        if m is not None:
            ll = self._handleInline(m.group(1)) or []
            lr = self._handleInline(m.group(4)) or []
            a = t.a[m.group(2)]
            href, title = self.references.get(m.group(3), ('undefined', ''))
            a = a(href=href)
            if title:
                a = a(title=title)
            ll.append(a)
            ll.extend(lr)
            return ll

        for decoration in ['escape', 'strong', 'emphasis', 'backtick']:
            m = regExp[decoration].match(line)
            if m is not None:
                if decoration == 'emphasis':
                    el = t.em
                elif decoration == 'strong':
                    el = t.strong
                elif decoration == 'backtick':
                    el = t.code
                if m.group(2) is not None:
                    ll = self._handleInline(m.group(1)) or []
                    lr = self._handleInline(m.group(3)) or []
                    text = m.group(2)
                elif m.group(5) is not None:
                    ll = self._handleInline(m.group(4)) or []
                    lr = self._handleInline(m.group(6)) or []
                    text = m.group(5)
                if decoration in ['escape']:
                    ll.append(text)
                else:
                    el[text]
                    ll.append(el)
                ll.append(t.br)
                ll.extend(lr)
                return ll
        else:
            return [line,]
    
    def _handleListitems(self, items):
        unlisted_items = []
        for item in items: 
            m = regExp['listitem'].match(item)
            if m is not None:
                unlisted_items.append(m.group(2))
        accumulate = []
        for item in unlisted_items:
            m = regExp['nestedlistitem'].match(item.strip())
            if m is not None:
                print m.group(3).strip()
                accumulate.append(m.group(3).strip())
            else:
                if accumulate != []:
                    yield self._handleListitems(accumulate)
                    accumulate = []
                yield t.li[item]
        yield ''

    def _isLine(self, block):
        text = ''.join(block)
        match = regExp['isline'].match(text)
        if match and (match.group(0) or match.group(1) or match.group(2)) and len(text) > 2:
            return 1
        else:
            return 0

    def _handleHeader(self, header):
        m = regExp['header'].match(header)
        if m is None:
            return ''

        # allow only from h1 to h6
        if len(m.group(1)) > 6:
            return t.h6[m.group(2).strip()]
        else:
            return getattr(t, 'h%s'%len(m.group(1)))[m.group(2).strip()]

if __name__ == "__main__":
    a = MarkdownParser(file(sys.argv[1]).read())
    from nevow import loaders
    print loaders.stan(a.parse()).load()[0]
        
