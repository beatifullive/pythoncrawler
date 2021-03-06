#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import urllib2
import re


class Tool:
    removeImg = re.compile('<img.*?>| {7}|')
    # 删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    # 把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    # 将表格制表<td>替换为\t
    replaceTD = re.compile('<td>')
    # 把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    # 将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    # 将其余标签剔除
    removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.replaceLine, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replacePara, "\n    ", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        # strip()将前后多余内容删除
        return x.strip()

class BDTB(Tool):
    def __init__(self, baseUrl, seeLZ, floorTag):
        self.baseURL = baseUrl
        self.seeLZ = '?see_lz='+str(seeLZ)
        self.tool = Tool()
        self.file = None
        self.floor = 1
        self.deafaultTitle = u'百度贴吧'
        self.floorTag = floorTag

    def getPageNum(self, page):
        pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>',re.S)
        result = re.search(pattern, page)
        if result:
            # print "getPageNum"
            # print result.group(1)
            return result.group(1)
        else:
            return None


    def getPage(self, pageMum):
        try:
            url = self.baseURL+self.seeLZ+'&pn='+str(pageMum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            # print response.read()
            # print "getPage!"
            return response.read()
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接百度贴吧失败，错误原因",e.reason
                return None

    def getTitle(self,page):
        pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>', re.S)
        result = re.search(pattern, page)

        if result:
            # print "getTitle!"
            # print result.group(1)
            return result.group(1)
        else:
            print "not getTitle!"
            return None

    def getContent(self, page):
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        items = re.findall(pattern, page)
        #  for item in items:
        #     print item
        # print self.tool.replace(items[1])
        contents = []
        for item in items:
            content = "\n"+self.tool.replace(item)+"\n"
            contents.append(content)
        return contents

    def setFileTitle(self, title):

        if title is not None:
            self.file = open(title.decode('utf-8') + ".txt", "w+")
        else:
            self.file = open(self.defaultTitle.decode('utf-8') + ".txt", "w+")

    def writeData(self, contents):
        for item in contents:
            if self.floorTag == '1':
                floorLine = "\n" + str(
                    self.floor) + u"-----------------------------------------------------------------------------------------\n"
                self.file.write(floorLine)
            self.file.write(item)
            self.floor += 1

    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        print title
        self.setFileTitle(title)
        if pageNum == None:
            print "URL已失效，请重试"
            return
        try:
            print "该帖子共有"+str(pageNum)+"页"
            for i in range(1, int(pageNum)+1):
                print "正在写入第"+str(i)+"页数据"
                page = self.getPage(i)
                contents = self.getContent(page)
                self.writeData(contents)
        except IOError, e:
            print "写入异常，原因" + e.message
        finally:
            print "写入任务完成"

# baseURL = 'http://tieba.baidu.com/p/'+ str(raw_input(u'http://tieba.baidu.com/p/'))
baseURL = 'http://tieba.baidu.com/p/4180574341'
# seeLZ = raw_input("是否只获取楼主发言，是输入1，否输入0\n")
# floorTag = raw_input("是否写入楼层信息，是输入1，否输入0\n")
seeLZ = 1
floorTag = 1
bdtb = BDTB(baseURL,seeLZ,floorTag)
bdtb.start()