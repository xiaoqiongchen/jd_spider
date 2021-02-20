import xlwt
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import requests
driver = webdriver.Chrome()
workbook =xlwt.Workbook(encoding='utf-8')
resultlist = []

def writeExcel(good_list,flag):
    count = 0
    worksheet = workbook.add_sheet('data'+str(flag))
    worksheet.write(count, 0, '序号')
    worksheet.write(count, 1, '价格')
    worksheet.write(count, 2, '名称')
    worksheet.write(count, 3, '图片')

    for g in good_list:
            count = count + 1
            worksheet.write(count, 0, count)
            worksheet.write(count, 1, g[0])
            worksheet.write(count, 2, g[1])
            worksheet.write(count, 3, g[2])

#把图片链接保存本地
def save_image_to_disk(imagepath,imageurl):
    if os.path.exists(imagepath):
       if imageurl.strip()!="":
           imagename=imageurl.split("/")[-1]
           r=requests.get(imageurl)
           with open(imagepath+imagename,"wb") as fp:
                fp.write(r.content)
                if fp.write(r.content)>0:
                    return imagepath+imagename
                else:
                    return "图片存储失败"
    else:
        return "图片路径error！"
#从本地读出来然后以二进制方式返回
#以二进制方式数据写入excel

def next_page(page):
    if page>1:
        driver.find_elements_by_xpath("//*[@id ='J_bottomPage']/span[1]/a[9]")[0].click()#模拟点击下一页按钮
    Parse_Html_Page()
    writeExcel(resultlist, page)#把结果保存至excel表格

def Parse_Html_Page():#获取每页源码存入至resultlist列表中
    resultlist.clear()#每次调用清空列表，避免每次获取数据都会累加上一页数据
    time.sleep(5)
    js = "var q=document.documentElement.scrollTop=10000"
    driver.execute_script(js)  # 因京东商品每页数据不是一次性加载出来(每次只加载30条数据)，但是每页有60条数据，这样爬取数据就不对了，所以要模拟鼠标手动刷新
    time.sleep(5)#刷新完再休眠5s
    html = driver.page_source  # 加载完所有商品获取网页源码
    soup = BeautifulSoup(html, "html.parser")#用BeautifulSoup解析网页源码，便于后面获取网页信息
    #print(soup)
    goodslist = soup.select("#J_goodsList>ul>li")#用BeautifulSoup提供的css选择器select函数获取所有的li标签，也就是所有的商品信息
    #print(goodslist)
    #print(len(goodslist))
    for good in goodslist:#循环遍历商品信息存入至resultlist结果列表
        temp = []
        good_price = good.find("i").text
        good_name = good.find_all("em")[1].text
        imgsrc =good.select("div > div.p-img > a>img")#返回的类型为<class 'bs4.element.ResultSet'>，如果想操作的话需要转换为<class 'bs4.element.Tag'>
                                                      #类型，所以if条件获取时需要写成imgsrc[0]
        if imgsrc[0]["data-lazy-img"] == "done":
            image="https:"+imgsrc[0]["src"]
            print(image)
        else:
            image="https:"+imgsrc[0]["data-lazy-img"]
            print(image)
        temp.append(good_price)
        temp.append(good_name)
        temp.append(image)
        resultlist.append(temp)

def main_index(key,filename):#主函数
    driver.get("https://www.jd.com/")#打开京东首页
    driver.maximize_window()#窗口最大化
    try:
        driver.find_element_by_id("key").send_keys(key)#输入关键字
        driver.find_element_by_xpath("//div[@id='search']/div/div[2]/button").click()#模拟鼠标点击事件
        time.sleep(5)
        total=driver.find_elements_by_xpath("//div[@id='J_bottomPage']/span[2]/em/b")[0].text#获取总页数
        for i in range(1,int(total)+1):#从第一页开始遍历
            next_page(i)
    except Exception as e:
         print(e)
    workbook.save(filename + '.xls')

if __name__=="__main__":
    start_time=time.time()
    print("爬虫开始时间%s" %start_time)
    main_index("LV包", "LV包")
    end_time=time.time()
    print("共耗时%s" %(end_time-start_time))