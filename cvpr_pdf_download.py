# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 17:11:28 2018

@author: Zhiming Zhang
"""

import os
import re
import requests
from bs4 import BeautifulSoup


log=r'E:\Dataset\book_test'

def get_url_name(content,year_num):
    year=str(year_num)
    book_url_list=[]
    url='http://openaccess.thecvf.com/{}{}.py'.format(content,year)
    r=requests.get(url)
    html=r.text
    soup=BeautifulSoup(html,'html.parser')
    dds=soup.find_all('dd')
    for i,dd in enumerate(dds):
        if i%2==1:
            href=dd.find('a').get('href')
            book_url=r'http://openaccess.thecvf.com/'+href
            book_url_list.append(book_url)
    return book_url_list

def download(content,year_num,book_url_list):
    year=str(year_num)
    root_dir=r'E:\Dataset\book_test\{}_{}'.format(content,year)
    print('正在爬取的是 {} 年的 {} 会议论文'.format(year,content))
    if not os.path.exists(root_dir):
        os.makedirs(root_dir) 
    total_num=len(book_url_list)
    print('{} 年 {} 会议一共 {} 个文件'.format(year,content,total_num))
    
    key_interrupt=0
    for i,url in enumerate(book_url_list):
        name=url.split('/')[-1]
        ab_name=os.path.join(root_dir,name)
        if os.path.exists(ab_name):
            print('{} has already existed'.format(name))
            return
        try:
            r=requests.get(url,stream=True)
            with open(ab_name,'wb') as f:
                print('正在写入第{}个文件 ：{}'.format(i+1,name))
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        f.flush
            r.close()
        except KeyboardInterrupt:
            key_interrupt=1
            if os.path.exists(ab_name):
                os.remove(ab_name)
            return key_interrupt
        except Exception:
            key_interrupt=1
            return key_interrupt
    print('{}年的{}论文全部下载完成'.format(year,content))


def judge(content,year,book_url_list):
    all_match=0
    books_num=len(book_url_list)
    root_dir=r'E:\Dataset\book_test\{}_{}'.format(content,year)
    for root,dirs,files in os.walk(root_dir):
        if not len(files)==len(book_url_list):
            print('有未匹配的')
        for file in files:
            signal=0
            patten=file.split('CVPR')[0]
            for url in book_url_list:
                if re.search(patten,url):
                    signal=1
                    break
            if not signal:
                all_match=1
                print(file,'未匹配')
    if all_match:
        print('{} 年的 {} 会议论文 共{}篇 已经全部下载到本地了。'.format(year,content,len(books_num)))
    return all_match

def run():
    break_interrupt=0
    year_content_dict={'CVPR':[year for year in range(2015,2017)],'ICCV':[2013,2015,2017]}
    for content,year_list in year_content_dict.items():
        for year in year_list:
            book_url_list=get_url_name(content,year)
            all_match=judge(content,year,book_url_list)
            if all_match:
                break
            break_interrupt=download(content,year,book_url_list)
            if break_interrupt:
                print('下载被停止了')
                return
        
if __name__=='__main__':
    run()


