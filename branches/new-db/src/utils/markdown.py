#!/usr/bin/env python

# Python-Markdown
#
# Original Author: Manfred Stienstra (manfred.stienstra [at] dwerg.net)
#                  http://www.dwerg.net/projects/markdown/
#
# Maintained By:   Yuri Takhteyev (yuri [at] freewisdom.org)
#                  http://www.freewisdom.org
#
# Project website: http://www.freewisdom.org/projects/python-markdown
#
# License: GPL 2 (http://www.gnu.org/copyleft/gpl.html)

# Version: 1.2

import re
import sys
import os
import xml.dom.minidom

HTML_PLACEHOLDER = "HTML_BLOCK_GOES_HERE_21738940712938470198_ALKJDL"

def print_error(string):
    """
    Print an error string to stderr
    """
    sys.stderr.write(str(string)+'\n')



class Markdown:
    """Markdown formatter.

    This the class for creating a html document from Markdown text
    """

    regExp = {
        'reference-def' : re.compile(r'^(  )?\[([^\]]*)\]:\s*([^ ]*)(.*)'),
        
        'header':       re.compile(r'^(#*)([^#]*)(#*)$'),
        'listitem':     re.compile(r'^\*(.*)$|^[\d]*\.(.*)$'),
        'backtick':     re.compile(r'^([^\`]*)\`([^\`]*)\`(.*)$'),
        'escape':       re.compile(r'^([^\\]*)\\(.)(.*)$'),
        'emphasis':     re.compile(r'^([^\*]*)\*([^\*]*)\*(.*)$|^([^\_]*)\_([^\_]*)\_(.*)$'),
        'link':           re.compile(r'^([^\[]*)\[([^\]]*)\]\s*\(([^\)]*)\)(.*)$'),
        'reference-use' : re.compile(r'^([^\[]*)\[([^\]]*)\]\s*\[([^\]]*)\](.*)$'),
        'strong':       re.compile(r'^([^\*]*)\*\*(.*)\*\*([^\*]*)$|^([^\_]*)\_\_(.*)\_\_([^\_]*)$'),
        'containsline': re.compile(r'^([-]*)$|^([=]*)$', re.M),
        'o-liststart':    re.compile(r'^[\d]*\.'),
        'u-liststart':    re.compile(r'^\*\s+'),
        'isline':       re.compile(r'^(\**)$|^([-]*)$')
    }
    
    def __init__(self, text):
        """
        Create a new Markdown instance.

        @param text: The text in Markdown format.
        """
        # preprocess
        #print text
        self.references={}
        self.text = self._preprocess(text)
        self.rawHtmlBlocks=[]
        

    def _preprocess(self, text):
        """
        Preprocess the document

        @param text: The text in Markdown format.
        """
        # Remove whitespace.
        text = text.strip()
        # Zap carriage returns.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Extract references
        # E.g., [id]: http://example.com/  "Optional Title Here"

        text_no_ref = ""
        for line in text.split("\n") :
            m = self.regExp['reference-def'].match(line)
            if m:
                self.references[m.group(2)] = (m.group(3), m.group(4).strip())
            else :
                text_no_ref += line
                text_no_ref += "\n"

        return text_no_ref.strip()

    def _handleInline(self, doc, line):
        """
        Transform a Markdown line with inline elements to an XHTML part

        @param item: A block of Markdown text
        @return: A list of xml.dom.minidom elements
        """
        if not(line):
            return [doc.createTextNode(' '),]
        # two spaces at the end of the line denote a <br/>
        if line.endswith('  '):
            l = self._handleInline(doc, line.rstrip())
            l.append(doc.createElement('br'))
            return l

        m = self.regExp['link'].match(line)
        if m is not None:
            ll = self._handleInline(doc, m.group(1))
            lr = self._handleInline(doc, m.group(4))
            a = doc.createElement('a')
            a.appendChild(doc.createTextNode(m.group(2)))
            a.setAttribute('href', m.group(3))
            #ll.append(doc.createTextNode(" "))
            ll.append(a)
            #ll.append(doc.createTextNode(" "))
            ll.extend(lr)
            return ll

        m = self.regExp['reference-use'].match(line)
        if m is not None:
            ll = self._handleInline(doc, m.group(1))
            lr = self._handleInline(doc, m.group(4))
            a = doc.createElement('a')
            a.appendChild(doc.createTextNode(m.group(2)))

            href, title = self.references.get(m.group(3), ('undefined', '') )
            a.setAttribute('href', href)

            if title :
                a.setAttribute('title', title)
                                              
            #ll.append(doc.createTextNode(" "))
            ll.append(a)
            #ll.append(doc.createTextNode(" "))
            ll.extend(lr)
            return ll

        for type in ['escape', 'strong', 'emphasis', 'backtick']:
            m = self.regExp[type].match(line)
            if m is not None:
                if type == 'emphasis':
                    el = doc.createElement('em')
                elif type == 'strong':
                    el = doc.createElement('strong')
                elif type == 'backtick' :
                    el = doc.createElement('code')
                if m.group(2) is not None:
                    ll = self._handleInline(doc, m.group(1))
                    lr = self._handleInline(doc, m.group(3))
                    txtEl = doc.createTextNode(m.group(2))
                elif m.group(5) is not None:
                    ll = self._handleInline(doc, m.group(4))
                    lr = self._handleInline(doc, m.group(6))
                    txtEl = doc.createTextNode(m.group(5))
                if type in ['escape'] :
                    ll.append(txtEl)
                else :
                    el.appendChild(txtEl)
                    ll.append(el)
                    
                ll.extend(lr)
                return ll

                
        else:
            return [doc.createTextNode(line),]

    def _handleListitem(self, doc, item):
        """
        Transform a Markdown listitem to an XHTML part

        @param item: A block of Markdown text
        @return: An xml.dom.minidom element
        """
        m = self.regExp['listitem'].match(item)
        content = ''
        if m is not None:
            if m.group(1):
                content = m.group(1)
            elif m.group(2):
                content = m.group(2)
        el = doc.createElement("li")
        for element in self._handleInline(doc, content.strip()):
            el.appendChild(element)
        return el

    def _handleHeader(self, doc, text):
        """
        Transform a Markdown header to an XHTML part

        @param block: A block of Markdown text        
        @return: An xml.dom.minidom element
        """
        m = self.regExp['header'].match(text)
        if m is None:
            return doc.createTextNode('')

        # we only allow h1 - h6
        if len(m.group(1)) > 6:
            el = doc.createTextNode(text)
            return el
        else:
            el = doc.createElement("h%s" % len(m.group(1)))
            txtEl = doc.createTextNode(m.group(2).strip())
            el.appendChild(txtEl)
            return el

    def _handleParagraph(self, doc, block, noinline=False):
        """
        Transform a Markdown paragraph to an XHTML part

        @param block: A block of Markdown text 
        @param noinline: Whether to live inline elements alone or not
        @return: An xml.dom.minidom element
        """
        el = doc.createElement('p')
        for line in block.split('\n'):
            if line:
                if noinline:
                    el.appendChild(doc.createTextNode(line))
                else:
                    for item in self._handleInline(doc, line+'\n'):
                        el.appendChild(item)
                        
        #if noinline:
        #    el.appendChild(doc.createTextNode(block))
        #else:
        #    for item in self._handleInline(doc, block):
        #        el.appendChild(item)                        
        return el

    def _handleBlock(self, doc, block, noinline=False):
        """
        Transform a block of Markdown to an XHTML part

        @param block: A block of Markdown text
        @param noinline: Whether to live inline elements alone or not
        @return: A list of xml.dom.minidom elements
        """
        # we don't care about a bunch of newlines
        if not(block):
            return doc.createTextNode('')

        # header
        if block.startswith('#'):
            return self._handleHeader(doc, block)
        # code block
        elif block.startswith('    '):
            newblock = ''
            for line in block.split('\n'):
                newblock += line[3:]+'\n'
            if newblock:
                el = doc.createElement('pre')
                el2 = doc.createElement('code')
                el.appendChild(el2)
                try:
                    el2.appendChild(self._handleBlock(doc, newblock, True))
                except AttributeError, e:
                    print_error('Error: Found a strange code block')
                    print_error(newblock)
                    raise e
            else:
                el = doc.createTextNode('')
            return el

        elif block.startswith(">") :
            el = doc.createElement('blockquote')
            for line in block[1:].split('\n'):
                el.appendChild(doc.createTextNode(line))
            return el
        
        elif block.startswith("<") : # very permisive test for HTML
            self.rawHtmlBlocks.append(block)
            el = doc.createTextNode("\n" + HTML_PLACEHOLDER + "\n")
            return el

        # single line
        #elif len(block.split('\n')) == -1: #2:
        #    def countReps(block):
        #        text = block.replace(' ', '')
        #        match = self.regExp['isline'].match(text)
        #        if match and (match.group(1) or match.group(2)):
        #            return len(text)
        #        else:
        #            return 0
        #    if countReps(block.strip()) > 2:
        #        return doc.createElement('hr')
        #    else:
        #        return self._handleParagraph(doc, block, noinline)


        elif self._isLine(block) :
            return doc.createElement('hr')
        
        # unordened list
        #elif block.startswith('*'):
        elif self.regExp['u-liststart'].match(block):
            el = doc.createElement('ul')
            for line in block.split('\n'):
                if line:
                    el.appendChild(self._handleListitem(doc, line.strip()))
            return el
        # ordened list
        elif self.regExp['o-liststart'].match(block):
            el = doc.createElement('ol')
            for line in block.split('\n'):
                if line:
                    el.appendChild(self._handleListitem(doc, line.strip()))
            return el

        # images

        # everything else
        else:
            # header
            lineMatch = self.regExp['containsline'].search(block)
            if lineMatch and (lineMatch.group(1) or lineMatch.group(2)):
                lines = block.split('\n')
                try:
                    if lines[1].startswith('='):
                        return self._handleHeader(doc, '#'+lines[0])
                    elif lines[1].startswith('-'):
                        return self._handleHeader(doc, '##'+lines[0])
                except IndexError, e:
                    print_error('Error: Found a strange header block')
                    print_error(block)
                    raise e
                print_error('Error: Isline was true, while there was no line')
                print_error(block)
                return doc.createTextNode('\n')    
            # this is a block with no inline elements
            elif noinline:
                return doc.createTextNode(block)
            # this is a paragraph
            else:
                return self._handleParagraph(doc, block, noinline)


    def _isLine(self, block) :

        text = block.replace(' ', '')
        match = self.regExp['isline'].match(text)
        if match and (match.group(1) or match.group(2)) and len(text) > 2:
            return 1
        else:
            return 0

    def _transform(self):
        """
        Transform the Markdown text into a XHTML body document

        @returns: An xml.dom.minidom.Document
        """
        doc = xml.dom.minidom.Document()
        #body = doc.createElementNS("http://www.w3.org/1999/xhtml", "body")
        body = doc.createElement("span")
        body.setAttribute('class', 'markdown')
        doc.appendChild(body)

        # parser state
        block = ''

        # parse through the document and create block level events
        for line in self.text.split('\n'):
            # blocks are separated by blank lines
            if line.strip() == '':
                body.appendChild(self._handleBlock(doc, block))
                block = ''
            else:
                block += line+'\n'
        if block:
            body.appendChild(self._handleBlock(doc, block))
        return doc

    def __str__(self):
        """
        Return the document in XHTML format.

        @returns: A serialized XHTML body.
        """
        doc = self._transform()
        xml = doc.toxml()

        #print xml

        buffer = ""

        self.rawHtmlBlocks.reverse()

        #print self.rawHtmlBlocks

        for line in xml.split("\n")[1:] :
            if line == HTML_PLACEHOLDER :
                buffer += self.rawHtmlBlocks.pop()
                buffer += "\n"
            else :
                buffer += line
                buffer += "\n"

        return buffer
    
    toString = __str__


if __name__ == '__main__':
    print Markdown(file(sys.argv[1]).read())
