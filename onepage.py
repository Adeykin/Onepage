import sys
#import xml.etree.ElementTree
from xml.dom import minidom
import xml.sax
from BeautifulSoup import BeautifulSoup  

def help():
    print "onepage.py <index.html> <output.html>"
    
def getLinks(page):
    return []

class Page:
    def __init__(self, title, body):
        self.title = title
        self.body = body
       

def pagesToJS(pages):
    buf = 'var pages = ['
    lines = []
    for page in pages:
        lines.append( '{title: \'' + str(page[0]) + 
                '\', body:\'' + str(page[1]) + '\'}')
    buf +=','.join(lines)
    buf += ']'
    return buf
    

templatePath = 'template.html'
pages = []

if len(sys.argv) != 3:
    help()
    quit()
    
indexPath = sys.argv[1]
outputPath = sys.argv[2]
    
f = file(indexPath)
data = f.read()
#print data

#doc = xml.etree.ElementTree.parse(indexPath)
#doc = minidom.parse(indexPath)
doc = minidom.parseString(data)
head = doc.getElementsByTagName('head')[0]
title = head.getElementsByTagName('title')[0]
body = doc.getElementsByTagName('body')[0]

#print 'head'
#print head.firstChild.nodeValue
#print head.firstChild.childNodes[0].data
#print " ".join(t.nodeValue for t in head if t.nodeType == t.TEXT_NODE)

soup = BeautifulSoup(data)

#print soup.prettify()

titleTag = soup.html.head.title

bodyTag = soup.html.body
body = ''.join(['%s' % x for x in bodyTag.contents])
body = body.replace('\n','\\\n')

pages.append( (titleTag.string, body) )

#====================================

jsArray = pagesToJS(pages)

print jsArray

#====================================
f = file(templatePath)
template = f.read()
template = template.replace('%PAGES%', jsArray)
f = file(outputPath, 'w')
f.write(template)
