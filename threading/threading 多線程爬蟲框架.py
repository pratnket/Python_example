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
        with self.num:#同时并行指定的线程数量，执行完毕一个则死掉一个线程

            lock.acquire()#锁住线程，防止同时输出造成混乱
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
        results.append(q.get())  #q.get()按顺序从q中拿出一个值
    results = '\n'.join(results)
    f.write(results)

#開始時間
tstart =time.time()

threads=[]
q=queue.Queue()
lock=threading.Lock()
num=threading.Semaphore(100)#设置同时执行的线程数为100，其他等待执行

urls = [line for line in open('Urls.txt',"r").read().split("\n")]

#启动所有线程
for i in range(len(urls)):#总共需要执行的次数
    t=thread_curl(q,lock,num,urls[i])
    t.start()
    threads.append(t)

for t in threads:
    t.join()

save(urls)

print ('所有执行完毕')
