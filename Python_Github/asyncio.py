# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import re
from lxml import etree

urls = ["http://www.bj-sh.com/","http://www.bwlc.net/","http://www.96628.com/",]

count_max = len(urls)

count = 0

# 限制并发数为5个
semaphore = asyncio.Semaphore(5)

f = open("restult.txt", "a")

async def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
    }
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as html:
                response = await html.text(encoding="utf-8")
                # print(response)
                return response

async def parse(url):

    global count
    count += 1
    
    print( str( count ) + " / " + str(count_max) + "  " + url)

    try:
        html = await get_html(url)
        hrefs = etree.HTML(html).xpath('//a/@href')
    except:
        pass
    for href in hrefs:
        try:
            href = re.search('http://.*?/',href).group(0)
            if href != url:
                f.write( str(href[:-1]) + '\n')
        except:
            pass
    
loop = asyncio.get_event_loop()
tasks = [parse(url) for url in urls]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
f.close()
