#coding:utf-8
'''
Created on 2016年4月26日

@author: xieli
'''
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

import urllib2
from bs4 import BeautifulSoup
import csv
import codecs 

item = ""       #item name
lowprice = ""   
aveprice = ""
highprice = ""
specification = ""
unit = ""
date = ""

veg_csv_file = file('XinFDVeg.csv', 'wb')
fruit_csv_file = file('XinFDFruit.csv', 'wb')

# Handle Chinese char in CSV file, f.write('\xEF\xBB\xBF') also works
veg_csv_file.write(codecs.BOM_UTF8)             
fruit_csv_file.write(codecs.BOM_UTF8) 

veg_w = csv.writer(veg_csv_file,dialect='excel')
veg_w.writerow(['品名', '最低价', '平均价','最高价','规格','单位','发布日期'])
fruit_w = csv.writer(fruit_csv_file,dialect='excel')
fruit_w.writerow(['品名', '最低价', '平均价','最高价','规格','单位','发布日期'])

for Veg_Fruit in range(2,3):
    
    url = "http://www.xinfadi.com.cn/marketanalysis/" + str(Veg_Fruit)+ "/list/1.shtml"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page,"html.parser")

    # Get the total number of pages from page footer, the 1st <em> body
    page_footer = soup.find_all("em")
    rec_total_txt = page_footer[1]
    Rec_Total = int(rec_total_txt.get_text())
    Page_Total = int(round(Rec_Total/20+1))
    # print 'Total records %d, total pages %d' %(Rec_Total,Page_Total)
    
    page_no = Page_Total
    while (page_no):
    
        print 'Page number %d' %page_no
        url = "http://www.xinfadi.com.cn/marketanalysis/"+str(Veg_Fruit)+"/list/"+str(page_no)+".shtml"
        # print 'Get  ' + url
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page,"html.parser")
    
        # Goto the price history table of page
        table = soup.find("table", {"class":"hq_table"})
        
        # Get all the rows, Rows_Total gives the total number of rows in table 
        rows = table.find_all("tr")
        Rows_Total = len(rows)
        print '本%d表有 %d 行记录' %(Veg_Fruit,Rows_Total)
     
        
        for row_no in range(1,Rows_Total):
            
            # Get each row identified by row_no from table, fetch each item info, assemble a line in CSV file.  
            cells = rows[Rows_Total-row_no].find_all("td")      # Descending sequence， easy to append new content. 
            
            item = cells[0].find(text=True)       #item name
            lowprice = cells[1].find(text=True)
            aveprice = cells[2].find(text=True)
            highprice = cells[3].find(text=True)
            specification = cells[4].find(text=True)
            unit = cells[5].find(text=True)
            date = cells[6].find(text=True)
            
            rec_line = (item,lowprice,aveprice,highprice,specification,unit,date)
            # print rec_line
    
            if Veg_Fruit == 1:      # Vegetable 
                veg_w.writerow(rec_line)
            elif Veg_Fruit == 2:    # Fruit
                fruit_w.writerow(rec_line)
            else: 
                print "Wrong! not veg nor fruit!"          
            
        page_no -= 1        
            
veg_csv_file.close()    
fruit_csv_file.close()    

