#coding:utf-8
import threading
import random
import queue
import time
import sys
import re
import requests
from lxml import etree
#
#需求分析：有大批量数据需要执行，而且是重复一个函数操作（例如爆破密码），如果全部开始线程数N多，这里控制住线程数m个并行执行，其他等待
#
#继承一个Thread类，在run方法中进行需要重复的单个函数操作
class thread_curl(threading.Thread):
    def __init__(self,queue,lock,num,url):
        #传递一个队列queue和线程锁，并行数
        threading.Thread.__init__(self)
        self.queue=queue
        self.lock=lock
        self.num=num
        self.url=url
    def run(self):
        with self.num: # 同時並行指定的線程數量，執行完畢一個則死掉一個線程

            lock.acquire() # 鎖住線程，防止同時輸出造成混亂
            print ('开始一个线程：',self.name)
            print ('數據大小：',q.qsize())
            print('耗時：' , time.time() - tstart)
            lock.release()

            hrefs = []
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
                }
                r = requests.get(self.url, headers=headers , timeout=8)
                html = r.text
                hrefs = etree.HTML(html).xpath('//a/@href')
            except:
                pass

            for i,href in enumerate(hrefs):
                p = re.compile(r'http://.*?/')
                res = p.findall(str(href))
                if len(res) > 0:
                    if res[0] != self.url:
                        q.put(res[0])
                        
def save(urls):
    f = open("results.txt" , "w")
    results = []
    for _ in range(len(urls)):
        results.append(q.get()) # q.get（）按順序從q中拿出一個值
    results = '\n'.join(results)
    f.write(results)

#開始時間
tstart =time.time()

threads=[]
q=queue.Queue()
lock=threading.Lock()
num=threading.Semaphore(100) # 設置同時執行的線程數為100，其他等待執行

urls = [line for line in open('Urls.txt',"r").read().split("\n")]

for i in range(len(urls)):#总共需要执行的次数
    t=thread_curl(q,lock,num,urls[i])
    t.start()
    threads.append(t)
    while True:
        #判断正在运行的线程数量,如果小于100则退出while循环,
        #进入for循环启动新的进程.否则就一直在while循环进入死循环
        if(len(threading.enumerate()) < 100):
            tEnd = time.time()#計時結束
            break

for t in threads:
    t.join()

save(urls)

print ('所有执行完毕')
