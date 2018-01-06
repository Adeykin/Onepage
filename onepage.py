#!/usr/bin/python

import os, sys
import base64
import mimetypes
import urlparse
from bs4 import BeautifulSoup, SoupStrainer, Comment

def help():
    print "onepage.py <index.html> <output.html>"
    
def wrapString(text):
    return text.replace('\'','\\\'').replace('\n','\\\n').replace('script','scr\'+\'ipt')
    
def isInternalLink(link):
    return urlparse.urlparse(link).netloc == ''

def isJavaScriptLink(link):
    return link.split(':')[0].lower() == 'javascript'
    
class Page:
    def __init__(self, pagePath, pageName):
        self.path = pagePath + '/' + pageName
        self.pagePath = pagePath
        self.pageName = pageName
        print ']] Parsing: ' + self.path
        f = file(self.path)
        data = f.read()
        data = data.decode('utf8')
        soup = BeautifulSoup(data, 'lxml')
        
        #exculude commensts
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
             
        cssTags = soup.html.head(['link', 'style'])
        #TODO: add filter
        self.styles = list(map(lambda tag: self.__processCSS(tag), cssTags))
       
        self.titleTag = soup.html.head.title
        
        body = soup.html.body
        for img in body('img'):
            img['src'] = self.__processImage(img['src'])
            
        #preprocess links
        links = body('a')
        for link in links:
            if not link.has_attr('href'):
                continue
            linkUrl = link['href']
            if isInternalLink(linkUrl) and not isJavaScriptLink(linkUrl):
                print link
                link['class'] = 'op_internal_link'
                #link.attrs.append(('class', 'op_internal_link'))
            
        self.bodyTag = body
        
    def getTitle(self):
        return self.titleTag.string
        
    def getBody(self):
        body = ''.join([str(x) for x in self.bodyTag.contents])
        return wrapString(body)
        
    def getStyles(self):
        return wrapString( ''.join(self.styles) )
        
    def getLinks(self):
        links = self.bodyTag('a')
        links = list(filter(lambda link: link.has_attr('href'), links))
        return list(map(lambda link: link['href'], links))
        
    def __processCSS(self, tag):
        if tag.name == 'link':
            fileName =  tag['href']
            filePath = self.pagePath + '/' + fileName
            f = file(filePath)
            css = f.read()
            return '<style type="text/css">' + css + '</style>' 
        elif tag.name == 'style':
            return str(tag)
        else:
            print 'ERROR'
            quit()
            
    def __processImage(self, src):
        #TODO: internet url support
        mimetype = mimetypes.guess_type(src)
        f = file(self.pagePath + '/' + src)
        data = f.read()
        return 'data:' + mimetype[0] + ';base64,' + base64.b64encode(data)
       
class Parser:
    def __init__(self, indexPath, indexName):
        self.indexPath = indexPath
        self.indexName = indexName
        self.pages = {}
    
    def parse(self):
        self.parsePage(self.indexName)
        
    def parsePage(self, name):
        page = Page(self.indexPath, name)
        self.pages[name] = page
        links = page.getLinks()
        for link in links:
            if not link in self.pages and isInternalLink(link) and not isJavaScriptLink(link):
                if not os.path.exists(self.indexPath + '/' + link): #TODO: refactor it
                    print "[Warning] File doesnt exist: " + self.indexPath + '/' + link
                    continue
                self.parsePage(link)
    
def pageToJS(page):
    buf = 'title: \'' + str(page.getTitle()) \
        + '\', styles: \'' + str(page.getStyles()) \
        + '\', body:\'' + str(page.getBody())
    return buf    
    
def pagesToJS(pages):
    buf = 'var pages = {'
    lines = []
    for pageIndex, pageVal in pages.iteritems():
        lines.append( '\'' + pageIndex + '\' : {'  + pageToJS(pageVal) +  '\'}')    
    buf +=','.join(lines)
    buf += '}'
    return buf    

templatePath = 'template.html'
pages = []

if len(sys.argv) != 3:
    help()
    quit()
    
indexPath = sys.argv[1]
outputPath = sys.argv[2]

parser = Parser(indexPath, 'index.html')
parser.parse()

jsArray = pagesToJS(parser.pages)

#print jsArray

f = file(templatePath)
template = f.read()
template = template.replace('%PAGES%', jsArray)
f = file(outputPath, 'w')
f.write(template)
