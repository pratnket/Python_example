#coding:utf-8
import threading
import random
import queue
import time
import sys
import re

import requests                

import concurrent.futures

import pycurl
import io # python3 導入法 

from lxml import etree

#------------------------自动处理cookile的函数----------------------------------#
def initCurl():
    c = pycurl.Curl()
    c.setopt(pycurl.COOKIEFILE, "cookie_file_name")#把cookie保存在该文件中
    c.setopt(pycurl.COOKIEJAR, "cookie_file_name")
    c.setopt(pycurl.FOLLOWLOCATION, 1) #允许跟踪来源
    c.setopt(pycurl.MAXREDIRS, 1) # 最大重定向次数,可以预防重定向陷阱
    c.setopt(pycurl.CONNECTTIMEOUT, 2) #链接超时
    #设置代理 如果有需要请去掉注释，并设置合适的参数
    #c.setopt(pycurl.PROXY, ‘http://11.11.11.11:8080′)
    #c.setopt(pycurl.PROXYUSERPWD, ‘aaa:aaa’)
    return c
#-----------------------------------get函数-----------------------------------#
def GetDate(curl, url):
    head = ['Accept:*/*', 'User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0']
    buf = io.BytesIO()
    curl.setopt(pycurl.WRITEFUNCTION, buf.write)
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.HTTPHEADER,  head)
    curl.perform()
    the_page =buf.getvalue()
    buf.close()
    return the_page
#-----------------------------------post函数-----------------------------------#
def PostData(curl, url, data):
    head = ['Accept:*/*',
                'Content-Type:application/xml',
                'render:json',
                'clientType:json',
                'Accept-Charset:GBK,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding:gzip,deflate,sdch',
                'Accept-Language:zh-CN,zh;q=0.8',
                'User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0']
    buf = StringIO.StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, buf.write)
    curl.setopt(pycurl.POSTFIELDS,  data)
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.HTTPHEADER,  head)
    curl.perform()
    the_page = buf.getvalue()
    buf.close()
    return the_page
#-----------------------------------post函数-----------------------------------#
#c = initCurl()
#html = GetDate(c, 'http://www.baidu.com')
#print (html)
    
class thread_curl(threading.Thread):
    def __init__(self,lock,num,url):
        #传递一个队列queue和线程锁，并行数
        threading.Thread.__init__(self)
        self.lock=lock
        self.num=num
        self.url=url
    def run(self):
        global count
        
        with self.num: # 同時並行指定的線程數量，執行完畢一個則死掉一個線程
            c = initCurl()
            hrefs = []
            try:
                html = GetDate(c,self.url)
                hrefs = etree.HTML(html).xpath('//a/@href')
            except:
                save()

            for i,href in enumerate(hrefs):
                try:
                    res = re.compile(r'http://.*?/').findall(href)
                    if len(res) > 0:
                        res = res[0]
                        if res[:-1] != self.url:
                            q.put(res[:-1])
                except:
                    pass

            self.lock.acquire() # 鎖住線程，防止同時輸出造成混亂
            count += 1
            print ('進度：', count ," / " , max_count )
            print ('數據大小：',q.qsize())
            print ('耗時：' , int(time.time() - Tstart) )
            self.lock.release()

def main():
    threads=[]
    lock=threading.Lock()
    num=threading.Semaphore(100) # 設置同時執行的線程數為100，其他等待執行
    
    urls = [line for line in open('Urls.txt',"r").read().split("\n")]
    for i in range(len(urls)):#总共需要执行的次数
        t=thread_curl(lock,num,urls[i])
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    save()

def save():
    f = open("results.txt" , "a")
    print("檔案保存中")
    while not q.empty():
        try:
            f.write(q.get() + "\n")
        except:
            pass
    f.close()
    
def get_content(url):
    try:
        r = requests.get(url,timeout=8)
        return r.text
    except:
        pass

def scrap():# 並發，遇到網站無法連線的會停住 (X)

    URLS = [line for line in open('Urls.txt',"r").read().split("\n")]
    max_count = len(URLS)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        
        c = initCurl()
        future_to_url = {executor.submit(get_content, url): url for url in URLS}
        for index , future in enumerate(concurrent.futures.as_completed(future_to_url)):

            hrefs = []
            url = future_to_url[future]
            print(url)

            try:
                data = future.result()
                hrefs = etree.HTML(data).xpath('//a/@href')
            except Execption as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print('%d / %d length is %d' % (index + 1 , max_count , q.qsize()))
            if len(hrefs) > 0:   
                for i,href in enumerate(hrefs):
                    res = re.compile(r'http://.*?/').findall(href)
                    if len(res) > 0:
                        if res[0] != url and res[0] != None:
                            q.put(res[0])

if __name__ == '__main__':
    max_count = len([line for line in open('Urls.txt',"r").read().split("\n")])
    count = 0
    Tstart = time.time()
    q=queue.Queue()
    main()
    print("總耗時:" , time.time() - Tstart)

