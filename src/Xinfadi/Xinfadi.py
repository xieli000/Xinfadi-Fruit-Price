#coding:utf-8
'''
Created on 2016年5月3日

@author: xieli
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib2
from bs4 import BeautifulSoup
import csv
import codecs 
import os
import pandas as pd 
import socket
import time


def get_file_size(file_to_handle):
    " If the file exist, return number of records; otherwise create a new file, and write-in the header"

    # Test whether the file exist
    if os.path.exists(file_to_handle):
        # df = pd.read_csv(csv_filename)
        # RecNuminFile = len(df)  # 
        # bottom = df.tail(1)
        # close(df)
        
        #csv_file = file(csv_filename,'r')
        with open(file_to_handle,'rb') as csv_file:
            reader = csv.reader(csv_file)
            Num_of_Rec = 0
            # Cal the number of records in file
            for eachline in reader:
                if len(eachline) > 1:  # not empty line
                    Num_of_Rec += 1  # 
            # bottom = df.tail(1)
            csv_file.close()
            Num_of_Rec -= 1    # Decrease the header line
            print 'Open file %s with %d records' %(file_to_handle, Num_of_Rec)
    else:
        # Create the file, and writein the header line
        # csv_file = file(csv_filename, 'wb')
        with open(file_to_handle, 'wb') as csv_file:
            print 'Create file ' + file_to_handle
            # Handle Chinese char in CSV file, f.write('\xEF\xBB\xBF') also works
            csv_file.write(codecs.BOM_UTF8)             
            csv_w = csv.writer(csv_file,dialect='excel')
            csv_w.writerow(['品名', '最低价', '平均价','最高价','规格','单位','发布日期']) 
            csv_file.close()   
            Num_of_Rec = 0

    return (Num_of_Rec)


def get_xinfadi_price():
    "Access XinFaDi website, get new updated veg/fruit price, and append to the files."

    veg_filename = 'XinFDVeg.csv'
    fruit_filename = 'XinFDFruit.csv'
    sleeptime = 5
    
    pr = """Update file %s
    ----------------------------------------------------------------------------------
        Append records     %d
        Total records      %d
    """

  
    for Veg_Fruit in range(1,3):
        
        # 1 for Vegetable, 2 for Fruit
        if Veg_Fruit == 1:
            csv_filename = veg_filename
        else:
            csv_filename = fruit_filename 
        
        # Test if the file exist, otherwise create new file       
        RecNuminFile = get_file_size(csv_filename)
        
        url = "http://www.xinfadi.com.cn/marketanalysis/" + str(Veg_Fruit)+ "/list/1.shtml"
        
        while (True):  # while() to handle network problem, like socket.error[10054]
            try: 
                page = urllib2.urlopen(url)
                soup = BeautifulSoup(page,"html.parser")
            except socket.error, e:
                if socket.error == 10054:
                    print 'Connection refused by server %d! Sleep %d seconds, then try again....' %(e.errno, sleeptime)
                    time.sleep(sleeptime)
                    sleeptime += 5
                    continue
                else:
                    print 'Network error, socket.error [%d]!' %e.errno
                    sys.exit(1)
            break
        
        # Get the total number of pages from page footer, the 1st <em> body
        page_footer = soup.find_all("em")
        rec_total_txt = page_footer[1]
        Rec_Total = int(rec_total_txt.get_text())
        Page_Total = int(round(Rec_Total/20+1))

        # row_no_in_page = int(round(RecNuminFile/20))
        print 'Total records %d, total pages %d' %(Rec_Total,Page_Total)
        
        # No need to get all records from website, just the update content from last time
        rec_to_handle = Rec_Total - RecNuminFile
        if rec_to_handle == 0:  # no records to append
            print pr %(csv_filename, rec_to_handle, Rec_Total)
            continue        
        
        if (rec_to_handle%20 ==0) : 
            # Start from a full page, page_no +1 because page_no start from 1 instead of 0
            page_no = int(round(rec_to_handle/20))
            rows_remain_in_page = 20         
        else:
            # Not from a full page, +1 for remain Recs in current page, +1 as page_no start from 1
            page_no = int(round(rec_to_handle/20))+1 
            rows_remain_in_page = rec_to_handle%20
 
        # Open CSV file to append new content
        # csv_file = open(csv_filename, 'ab')
        with open(csv_filename, 'ab') as csv_file: 
            csv_file.write(codecs.BOM_UTF8)             
            csv_w = csv.writer(csv_file,dialect='excel')
               
            while (page_no):
        
                # print 'Page number %d' %page_no
                url = "http://www.xinfadi.com.cn/marketanalysis/"+str(Veg_Fruit)+"/list/"+str(page_no)+".shtml"
                # print 'Get  ' + url
                
                try:   
                    page = urllib2.urlopen(url)
                    soup = BeautifulSoup(page,"html.parser")
                except socket.error, e:  #handle socket.errno(10054), etc.
                    if socket.error == 10054:
                        print 'Connection refused by server %d! Sleep %d seconds, then try again....' %(e.errno, sleeptime)
                        time.sleep(sleeptime)
                        sleeptime += 5
                        continue
                    else:
                        print 'Network error, socket.error [%d]!' %e.errno
                        csv_file.close()
                        sys.exit(1)
            
                # Goto the price history table of page
                table = soup.find("table", {"class":"hq_table"})
                
                # Get all the records to 'rows' 
                rows = table.find_all("tr")
                # print '本%d表有 %d 行记录' %(Veg_Fruit,len(rows))       
                
                while (rows_remain_in_page): 
                    # Get the row from table in page one by one, with descending sequence， easy to append 
                    # new content to CSV file. The record is identified by row_no from table, and assemble to msg.  
                    cells = rows[rows_remain_in_page].find_all("td")
                    
                    msg = []
                    for i in range(0,7): 
                        msg.append(cells[i].find(text=True))       #item name
                    
                    #csv_file.write(codecs.BOM_UTF8)         
                    # print(msg)
                    csv_w.writerow(msg)
                    rows_remain_in_page -= 1
                    continue
                 
                # print 'Append %d records' %(Rows_Total_in_Page-row_no)    
                page_no -= 1 
                rows_remain_in_page = 20      
                continue    
        
            print pr %(csv_filename, rec_to_handle, Rec_Total)  
                    
            csv_file.close() 
        continue   
    
if __name__ == '__main__':
    get_xinfadi_price()
