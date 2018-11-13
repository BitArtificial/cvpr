# -*- coding: utf-8 -*-
import os
import re
import requests
from bs4 import BeautifulSoup


log=r'E:\Book'

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
            #when you analysis the html you can get the rule
            href=dd.find('a').get('href')
            book_url=r'http://openaccess.thecvf.com/'+href
            book_url_list.append(book_url)
    return book_url_list

def download(content,year_num,book_url_list):
    year=str(year_num)
    root_dir=r'E:\Book\{}_{}'.format(content,year)
    print('正在爬取的是 {} 年的 {} 会议论文'.format(year,content))
    if not os.path.exists(root_dir):
        os.makedirs(root_dir) 
    break_mark,sub_num,patten=get_recover(content,year)
    total_num=len(book_url_list)
    book_url_list=book_url_list[sub_num:]
    num=len(book_url_list)
    print('{} 年 {} 会议一共 {} 个文件,还有 {} 个文件'.format(year,content,total_num,num))
    
    key_interrupt=0
    for i,url in enumerate(book_url_list):
        if break_mark and i==0:
            if not re.search(patten,url):
                print('文件校验{}不匹配，url:{}'.format(patten,url))
                return
        
        name=url.split('/')[-1]
        ab_name=os.path.join(root_dir,name)
        if os.path.exists(ab_name):
            print('{} has already existed'.format(name))
            return
        #this is to avoid the repeating download
        try:
            r=requests.get(url,stream=True)
            with open(ab_name,'wb') as f:
                print('正在写入第{}个文件 ：{}'.format(i+sub_num,name))
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        f.flush
            r.close()
        except KeyboardInterrupt:
            make_point(i,name,content,year)
            key_interrupt=1
            if os.path.exists(ab_name):
                os.remove(ab_name)
            #this is to remove the imcomplete files
            return key_interrupt
        except Exception:
            make_point(i,name,content,year)
            key_interrupt=1
            return key_interrupt
    #this means download successfully
    print('{}年的{}论文全部下载完成'.format(year,content))

#    with open(r'E:\Book\{}_{}_log.txt'.format(content,year),'w') as f:
#        con='{},{}'.format(str(i),name)
#        f.writelines(con)
#    
#定义断点校验
def make_point(i,name,content,year):
    root_dir=r'E:\Book\{}_{}'.format(content,year)
    ab_name=os.path.join(root_dir,name)
    print('第 {} 个文件写入失败，文件名是： {}'.format(i,name))
    with open(r'E:\Book\{}_{}_log.txt'.format(content,year),'w') as f:
        con='{},{}'.format(str(i),name)
        f.writelines(con)
    if os.path.exists(ab_name):
        os.remove(ab_name)
    return
#断点恢复
def get_recover(content,year):
    sub_num=0
    break_mark=0
    patten=''
    try:
        with open(r'E:\Book\{}_{}_log.txt'.format(content,year),'r') as f:
            con=f.readline()
            if con:
                sub=con.split(',')[0]
                pdf=con.split(',')[1]
                patten=pdf.split('CVPR')[0]
                print('上次的文件是第{}个 文件名是:{}'.format(sub,patten))
                sub_num=int(sub)
                break_mark=1         
    except Exception:
        print('log文件丢失或者没有断点')
    if break_mark:
        print('有断点，正在从上次记录中下载')
    return break_mark,sub_num,patten


def judge(content,year,book_url_list):
    all_match=0
    books_num=len(book_url_list)
    root_dir=r'E:\Book\{}_{}'.format(content,year)
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
    #all the year pdfs
    for content,year_list in year_content_dict.items():
        for year in year_list:
            #print('{} : {}'.format(content,year))
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
