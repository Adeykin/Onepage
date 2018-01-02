import sys
from BeautifulSoup import BeautifulSoup  

def help():
    print "onepage.py <index.html> <output.html>"
    
def wrapString(text):
    return text.replace('\n','\\\n')
    
class Page:
    def __init__(self, pagePath, pageName):
        self.path = pagePath + '/' + pageName
        self.pagePath = pagePath
        self.pageName = pageName
        print ']] Parsing: ' + self.path
        f = file(self.path)
        data = f.read()
        soup = BeautifulSoup(data)
             
        cssTags = soup.html.head(['link', 'style'])
        #TODO: add filter
        self.styles = list(map(lambda tag: self.__processCSS(tag), cssTags))
       
        self.titleTag = soup.html.head.title
        self.bodyTag = soup.html.body
        
    def getTitle(self):
        return self.titleTag.string
        
    def getBody(self):
        body = ''.join(['%s' % x for x in self.bodyTag.contents])
        return wrapString(body)
        
    def getStyles(self):
        return wrapString( ''.join(self.styles) )
        
    def getLinks(self):
        links = self.bodyTag('a')
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
            if not link in self.pages:
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
