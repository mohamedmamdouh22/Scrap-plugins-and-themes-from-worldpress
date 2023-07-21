import sys
import os
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from colorama import Fore, init
import csv
init(True)

versions=[]
last_update=[]
links=[]
file_names=[]
# read input file function
def read_input(path):

    try:
        url_list = []
        input_file = open(path, 'r', encoding='utf8')
        raw_data = csv.reader(input_file, delimiter=",")
        for index, row in enumerate(raw_data):
            url_list.append(row)
        csv_header = url_list[0]
        url_list.remove(url_list[0])
        input_file.close()
        return url_list

    except Exception as e:
        print(Fore.RED + "[ERROR] Error occurred during the input file reading.")
        sys.exit(e)

def init(link):                         # driver initialization
    options=webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--log-level=3")
    preferences = {
                    "profile.default_content_settings.popups": 0,
                    "download.default_directory": os.getcwd(),
                    "directory_upgrade": True
                }
    options.add_experimental_option("prefs", preferences)
    options.add_argument("--headless=new")
    driver=webdriver.Chrome(options=options,service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(5)
    driver.maximize_window()
    driver.get(link)
    
    return driver
# method to get the downloaded file name
def getDownLoadedFileName(driver):
    

    tabs=driver.window_handles
    driver.switch_to.window(tabs[1])
    while True:
        try:
            # get downloaded percentage
            downloadPercentage = driver.execute_script(
                "return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('#progress').value")
            # check if downloadPercentage is 100 (otherwise the script will keep waiting)
            if downloadPercentage == 100:
                # return the file name once the download is completed
                return driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
        except:
            pass
def scrape_items(driver,url): # scraping plugin info
    try:
        driver.get(url)
        time.sleep(5)
        try:
            Ptitle=WebDriverWait(driver,20).until(
                EC.presence_of_element_located((By.CLASS_NAME,'edd_download_title'))
            )
        except:
            Ptitle='Not found'
        try:
            Pversion=driver.find_element(By.XPATH,'//span[@class="pp-list-item-text"]').text.split(':')[1].strip()
            if not Pversion:
                Pversion='Not Found'
        except:
            Pversion='Not found'
        try:
            Pdate=driver.find_element(By.XPATH,'//*[@id="main"]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div[3]/div/div/ul/li[2]/span[2]').text.split(':')[1].strip()
            if not Pdate:
                Pdate=driver.find_element(By.XPATH,"//*[@id='main']/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div[4]/div/h2/span").text.strip()
        except:
            Pdate='Not found'
        Plink=driver.find_element(By.XPATH,'//a[@aria-label="View Original Product & Demo"]').get_attribute('href')                  
        if not Plink:
            Plink='Not Available'
        #download part#########################################
        # try:
        #     download_btn=driver.find_element(By.XPATH,'//div[@class="edd_download_buy_button"]')# search for download button
        #     download_btn.click()
        #     try:
        #         dn=driver.find_element(By.ID,'uc-download-link') ## for page appears when size is too large
        #         dn.click()
        #         time.sleep(2)
        #         # driver.back()
        #     except:
        #         pass
        #     # time.sleep(2)
        # # get file name #############
        # ###################################################
        #     file_name=getDownLoadedFileName(driver)
        #     time.sleep(2)
        #     tabs=driver.window_handles
        #     driver.switch_to.window(tabs[0])
        #     time.sleep(5)
        # except:
        #     file_name='Not Found'
###############################################################

        
        versions.append(Pversion)
        last_update.append(Pdate)
        links.append(Plink)
        # file_names.append(file_name) #uncomment when ready for scraping
        # driver.back()
    except:
        pass
def main():
    data=read_input('E:/Data Science/task/Wordpresssit.csv')
    titles=[]
    urls=[]
    category=[]
    for element in data:
        titles.append(element[0])
        urls.append(element[1])
        if 'plugin' in element[0].lower():
            category.append('Plugin')
        else:
            category.append('Theme')
    driver =init('https://worldpressit.com/zivdszeb5045yksndcnu/?loggedout=true&wp_lang=en_US')
    driver.execute_script("window.open()")
    tabs=driver.window_handles
    driver.switch_to.window(tabs[1])
    driver.get('chrome://downloads')
    driver.switch_to.window(tabs[0])
    time.sleep(5)
    # myAcc_button=WebDriverWait(driver,10).until(
    #     EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/header/div/div[2]/div/div[4]/ul/li[1]/div/a/span'))
    # )
    # myAcc_button.click()
    # time.sleep(3)
    # login_button=driver.find_element(By.CLASS_NAME,'fl-button')
    # login_button.click()
    # time.sleep(5)
    email=driver.find_element(By.ID,'user_login')
    email.send_keys('Pallanti2020@gmail.com')
    time.sleep(2)
    password=driver.find_element(By.ID,'user_pass')
    password.send_keys('Des041122@')
    time.sleep(2)
    sub=driver.find_element(By.ID,'wp-submit')
    sub.click()
    driver.refresh()
    print('logged in successfully')
    time.sleep(5)
    for i in range(len(urls)):
        scrape_items(driver,urls[i])
        print(Fore.BLUE + f'[+] {i+1}/{len(urls)} item scraped.', end='\r')
        df=pd.DataFrame(
            {
                'Category':category[:i+1],
                'Title':titles[:i+1],
                'Version':versions,
                'Update Date':last_update,
                'Links':links,
                # 'File Name':file_names
            }
        )
        df.to_csv('output.csv',index=False)
        # print(len(titles),len(category[:i+1]))
main()