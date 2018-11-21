# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 17:11:28 2018

@author: Zhiming Zhang

mail: i@dropout.cn

"""

import os
import re
import requests
from bs4 import BeautifulSoup


log=r'E:\Dataset\book_test'
save_dir=r'E:\Dataset\book_test'
#save_dir is the default download dir

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

def download(content,year_num,book_url_list,save_dir):
    year=str(year_num)
    root_dir=os.path.join('{}_{}'.format(content,year))
    print('downloading  the {} content papar of {} year'.format(content,year))
    if not os.path.exists(root_dir):
        os.makedirs(root_dir) 
    total_num=len(book_url_list)
    print('{} content of {} year total is {} '.format(content,year,total_num))
    
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
                print('Now writing the {} file ：{}'.format(i+1,name))
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
    print('{} content of {} year has downloaded successfully'.format(content,year))


def run():
    key_interrupt=0
    year_content_dict={'CVPR':[year for year in range(2015,2017)],'ICCV':[2013,2015,2017]}
    for content,year_list in year_content_dict.items():
        for year in year_list:
            book_url_list=get_url_name(content,year)
            key_interrupt=download(content,year,book_url_list,save_dir)
            if key_interrupt:
                print('keyboard interrupt')
                return
        
if __name__=='__main__':
    run()


