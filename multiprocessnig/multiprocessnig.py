#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import queue
import threading
import time
import requests
import re
from lxml import etree

def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
    }
    r = requests.get(url, headers=headers , timeout=8)
    return r.text

def parse(url):
    hrefs = []

    html = get_html(url)
    hrefs = etree.HTML(html).xpath('//a/@href')
        
    for i,href in enumerate(hrefs):
        tmp = [re.match( r'(http://.*?/)', href, re.M|re.I).group(1)]
        if tmp[:-1] != url:
            q.put(tmp)   #多线程调用的函数不能用return返回值

def save(f):
    results = []
    for _ in range(len(urls)):
        results.extend(q.get())  #q.get()按顺序从q中拿出一个值
    results = '\n'.join(results)
    f.write(results)

if __name__ == '__main__':

    tStart = time.time()#計時開始
      
    q =queue.Queue()    #q中存放返回值，代替return的返回值
    threads = []

    urls = [line for line in open('Urls.txt',"r").read().split("\n")]

    max_count = len(urls)

    for i in range(len(urls)):   #定义四个线程
        print( str(i) + " / " + str(max_count) + "  " + urls[i])
        t = threading.Thread(target=parse,args=(urls[i],)) #Thread首字母要大写，被调用的job函数没有括号，只是一个索引，参数在后面
        t.start()#开始线程
        threads.append(t) #把每个线程append到线程列表中
        while True:
            #判断正在运行的线程数量,如果小于800则退出while循环,
            #进入for循环启动新的进程.否则就一直在while循环进入死循环
            if(len(threading.enumerate()) < 800):
                tEnd = time.time()#計時結束
                print( "目前線程池數量:" + str(threading.activeCount()) +"  "+ "數據大小:" + str(q.qsize()) +"  "+ "耗時:" + str(tEnd - tStart))
                break

    for thread in threads:
        tEnd = time.time()#計時結束
        print( "GET請求完畢，等待回傳，線程池剩餘數量:" + str(threading.activeCount()) +"  "+ "數據大小:" + str(q.qsize()) +"  "+ "耗時:" + str(tEnd - tStart))
        thread.join()

    f = open("results.txt" , "w" , buffering=2048)
    save(f)
    print("結束")
    f.close()
