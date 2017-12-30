import sys
from BeautifulSoup import BeautifulSoup  

def help():
    print "onepage.py <index.html> <output.html>"

class Page:
    def __init__(self, path):
        print ']] Parsing: ' + path
        f = file(path)
        data = f.read()
        soup = BeautifulSoup(data)

        self.titleTag = soup.html.head.title
        self.bodyTag = soup.html.body
        
    def getTitle(self):
        return self.titleTag.string
        
    def getBody(self):
        body = ''.join(['%s' % x for x in self.bodyTag.contents])
        return body.replace('\n','\\\n')        
        
    def getLinks(self):
        links = self.bodyTag('a')
        return list(map(lambda link: link['href'], links))
       
class Parser:
    def __init__(self, indexPath, indexName):
        self.indexPath = indexPath
        self.indexName = indexName
        self.pages = {}
    
    def parse(self):
        self.parsePage(self.indexName)
        
    def parsePage(self, name):
        page = Page(self.indexPath + '/' + name)
        self.pages[name] = page
        links = page.getLinks()
        for link in links:
            if not link in self.pages:
                self.parsePage(link)
    
def pagesToJS(pages):
    buf = 'var pages = {'
    lines = []
    for pageIndex, pageVal in pages.iteritems():
        lines.append( '\'' + pageIndex + '\' :'  '{title: \'' + str(pageVal.getTitle()) + 
                '\', body:\'' + str(pageVal.getBody()) + '\'}')
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
