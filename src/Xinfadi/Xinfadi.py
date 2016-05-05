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

def get_xinfadi_price():
    "Access XinFaDi website, get new updated veg/fruit price, and append to the files."

    veg_filename = 'XinFDVeg.csv'
    fruit_filename = 'XinFDFruit.csv'
    
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
               
        # Test whether the file exist
        if os.path.exists(csv_filename):
            # df = pd.read_csv(csv_filename)
            # RecNuminFile = len(df)  # 
            # bottom = df.tail(1)
            # close(df)
            
            #csv_file = file(csv_filename,'r')
            with open(csv_filename,'rb') as csv_file:
                reader = csv.reader(csv_file)
                RecNuminFile = 0
                # Cal the number of records in file
                for eachline in reader:
                    if len(eachline) > 1:  # not empty line
                        RecNuminFile += 1  # 
                # bottom = df.tail(1)
                csv_file.close()
                RecNuminFile -= 1    # Decrease the header line
                print 'Open file %s with %d records' %(csv_filename, RecNuminFile)
        else:
            # Create the file, and writein the header line
            # csv_file = file(csv_filename, 'wb')
            with open(csv_filename, 'wb') as csv_file:
                print 'Create file ' + csv_filename
                # Handle Chinese char in CSV file, f.write('\xEF\xBB\xBF') also works
                csv_file.write(codecs.BOM_UTF8)             
                csv_w = csv.writer(csv_file,dialect='excel')
                csv_w.writerow(['品名', '最低价', '平均价','最高价','规格','单位','发布日期']) 
                csv_file.close()   
                RecNuminFile = 0
         
        url = "http://www.xinfadi.com.cn/marketanalysis/" + str(Veg_Fruit)+ "/list/1.shtml"
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page,"html.parser")
    
        # Get the total number of pages from page footer, the 1st <em> body
        page_footer = soup.find_all("em")
        rec_total_txt = page_footer[1]
        Rec_Total = int(rec_total_txt.get_text())
        Page_Total = int(round(Rec_Total/20+1))

        # row_no_in_page = int(round(RecNuminFile/20))
        print 'Total records %d, total pages %d' %(Rec_Total,Page_Total)
        
        # No need to get all records from website, just the update content from last time
        rec_to_handle = Rec_Total - RecNuminFile
        page_no = int(round(rec_to_handle/20+1))
        rows_remain_in_page = rec_to_handle%20
        if rows_remain_in_page==0:
            # Start from a full page, then page_no -1 
            rows_remain_in_page = 20
            page_no -= 1
 
        # Open CSV file to append new content
        # csv_file = open(csv_filename, 'ab')
        with open(csv_filename, 'ab') as csv_file: 
            csv_file.write(codecs.BOM_UTF8)             
            csv_w = csv.writer(csv_file,dialect='excel')
               
            while (page_no):
        
                # print 'Page number %d' %page_no
                url = "http://www.xinfadi.com.cn/marketanalysis/"+str(Veg_Fruit)+"/list/"+str(page_no)+".shtml"
                # print 'Get  ' + url
                page = urllib2.urlopen(url)
                soup = BeautifulSoup(page,"html.parser")
            
                # Goto the price history table of page
                table = soup.find("table", {"class":"hq_table"})
                
                # Get all the records to 'rows' 
                rows = table.find_all("tr")
                # print '本%d表有 %d 行记录' %(Veg_Fruit,len(rows))       
                
                for row_pointer in range(rows_remain_in_page,0,-1): 
                    # Get the row from table in page one by one, with descending sequence， easy to append 
                    # new content to CSV file. The record is identified by row_no from table, and assemble to msg.  
                    cells = rows[row_pointer].find_all("td")      
                    
                    msg = []
                    for i in range(0,7): 
                        msg.append(cells[i].find(text=True))       #item name
                    
                    #csv_file.write(codecs.BOM_UTF8)         
                    # print(msg)
                    csv_w.writerow(msg)
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