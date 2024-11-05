import math

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import shutil
import glob
import time
import datetime
import appConfig
import logger
#----------------------------------------------
appConfigData=appConfig.get_config()
defaultDownloadFolder = os.path.expanduser('~')+'/Downloads/'
appAction = input("This web scraping process will automatically login to Brevo site on chrome browser, you need manual interaction during captcha verification and logs filters selection. Do you want to proceed(y/n)?:")
if appAction=='y':
   browser = webdriver.Chrome()
    browser.get(appConfigData['targetURL'])
    user = browser.find_element(By.ID, "email")
    pwd = browser.find_element(By.ID, "password")
    login = browser.find_element(By.CLASS_NAME, "LoginForm_submitBtn__u_4LK")
    user.send_keys(appConfigData['userId'])
    time.sleep(3)
    pwd.send_keys(appConfigData['pwd'])
    time.sleep(5)
    login.click()
    WebDriverWait(browser, 160).until(EC.visibility_of_any_elements_located(
    (By.CLASS_NAME, "brevo-header")))
   # O time.sleep(15)
    browser.maximize_window()
    time.sleep(5)
    browser.get(f"{appConfigData['targetURL']}log")
    action = input("if required data is filtered on the logs page, do you want to proceed with download process(y/n)?:")
    if action=='y':
        logTxt =""
        logger.writeLog("-----------Process Started--------------")
        # Process downloading required documents
        paginationDetail = browser.find_element(By.CLASS_NAME,"footer-pagination")
        recordDetail=paginationDetail.find_elements(By.TAG_NAME,"b")
        #print(len(recordDetail))
        #print(recordDetail)
        totalPages = int(recordDetail[0].text)
        print(totalPages)
        if totalPages== 1:
            totalRecords = int(recordDetail[2].text)
        else:
            totalRecords = int(recordDetail[3].text)

        perPageRecords=math.ceil(totalRecords/totalPages)
        PageSize=25
        if(perPageRecords>25 and perPageRecords<=50):
            PageSize=50
        else:
            if perPageRecords>50:
                PageSize = 50
        logTxt=f"Total record(s) found:{totalRecords}, Page(s): {totalPages}, Page size: {PageSize}"
        print(logTxt)
        logger.writeLog(logTxt)

        pageNo=1
        while pageNo<=totalPages:
            currPaginationDetail=""
            pagingButtons=""
            if totalPages > 1:
                currPaginationDetail = browser.find_element(By.CLASS_NAME, "footer-pagination")
                # nexPage =browser.find_element(By.XPATH, "//button[contains(@class,'btn') and contains(@class,' btn-blank') and contains(@class,'next')]")
                pagingButtons=currPaginationDetail.find_elements(By.TAG_NAME,"button")
            # processing each row under the selected page
            pageTableRows =browser.find_elements(By.XPATH, "//tr[contains(@class,'cursor-pointer') and contains(@class,'ng-scope')]")
            logTxt = f"Processing records on page:{pageNo}"
            print(logTxt)
            logger.writeLog(logTxt)
            record=0
            for trData in pageTableRows:
                record+=1
                tdsData = trData.find_elements(By.TAG_NAME, "td")
                logTxt=f"Start Processing: record {record} of Page {pageNo}"
                print(logTxt)
                logger.writeLog(logTxt)
                logTxt =f"[{trData.text}]"
                print(logTxt)
                logger.writeLog(logTxt)

                event = tdsData[0].text
                eventDate = tdsData[1].text
                eventTitle = tdsData[2].text
                renamedDownloadFileName=f"{eventTitle}_{eventDate[0:10]}_{pageNo}-{record}.pdf"
                #print(renamedDownloadFileName)

                try:
                    trData.click()  # click to view detail
                    time.sleep(10)
                    try:
                        browser.switch_to.frame("preview-iframe")
                        WebDriverWait(browser, 20).until(EC.visibility_of_element_located(
                            (By.CLASS_NAME, "download")))
                        fileLinkElement = browser.find_element(By.CLASS_NAME, "download")
                        fileUrl = fileLinkElement.get_attribute("href")
                        fileLinkElement.click()
                        print("downloading file from link..")
                        logger.writeLog("downloading file from link..")
                    except Exception as e:
                        # error handling
                        logTxt = f"Error downloading file from link: {repr(e)}"
                        print(logTxt)
                        logger.writeLog(logTxt)
                        logTxt = f"End with Error record  {record} of Page {pageNo}"
                        logger.writeLog(logTxt)
                        continue
                    time.sleep(5)
                    # # Wait for download
                    while True:
                        filenames = glob.glob(defaultDownloadFolder+"*.*")
                        #print(filenames)
                        if len(filenames) > 0 and not any('.crdownload' in name for name in filenames):
                            break
                    #get latest downloaded file
                    print("Processing downloaded file")
                    logger.writeLog("Processing downloaded file")
                    downloadedFileName = max(
                        [defaultDownloadFolder + f for f in os.listdir(defaultDownloadFolder)],
                        key=os.path.getctime)
                    targetfileName = os.path.join(appConfigData['appDownloadFilePath'], rf"{renamedDownloadFileName}")
                    logTxt=f"Saving downloaded file on path:{targetfileName}"
                    print(logTxt)
                    logger.writeLog(logTxt)
                    os.replace(downloadedFileName,targetfileName)
                    logTxt = f"End Processing: record {record} of Page {pageNo}"
                    print(logTxt)
                    logger.writeLog(logTxt)
                    browser.switch_to.default_content()
                    if record == PageSize:
                        sideMenuHeader = browser.find_element(By.ID,"details-block")
                        # closeSideBar = sideMenuHeader.find_element(By.XPATH,
                        #                                         "//button[contains(@class,'close')]")
                        closeSideBar = sideMenuHeader.find_element(By.TAG_NAME,"button")
                        # print(closeSideBar)
                        # print(closeSideBar.text)
                        closeSideBar.click()
                        time.sleep(5)
                    #view record logicy
                except Exception as e:
                    #error handling
                    logTxt = f"Error Processing: record {record} of Page {pageNo}: {repr(e)}"
                    print(logTxt)
                    logger.writeLog(logTxt)
                    continue
            # click to move next page
            pageNo+=1
            if pageNo <= totalPages:
                try:
                    pagingButtons[2].click()
                except Exception as e:
                    #error handling
                    logTxt = f"Error on moving next Page {pageNo}: {repr(e)}"
                    print(logTxt)
                    logger.writeLog(logTxt)

            time.sleep(10)
        print("Process is completed, see log detail.")
        logger.writeLog("---------------------Process Ended-------------------")
    else:
        browser.quit()
    browser.quit()
    os.system('Press any key to close the program window.')
