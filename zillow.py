from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pynput.keyboard import Key, Controller
from datetime import datetime
import csv
import re
import json
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

baseUrl = "https://www.zillow.com/homes/"
#a77723b0-2281-11ea-a609-834481bfdd31&vid=
def createDriverInstance():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument("--enable-file-cookies")
    #options.add_argument('--headless')
    options.add_argument("start-maximized")
    #options.add_argument('--incognito')
    driver = webdriver.Chrome(chrome_options=options, port=9999)
    return driver

class Home:
    pass

def collectData(dirver, writer):
    ulElem = driver.find_element_by_class_name("photo-cards")
    liElems = ulElem.find_elements_by_xpath("./*")
    for item in liElems :
        try:
            scriptElem = item.find_element_by_tag_name("script")            
            stateElem = item.find_element_by_class_name("list-card-type")
            priceElem = item.find_element_by_class_name("list-card-price")            
            overlayElem = item.find_element_by_class_name("list-card-variable-text")
            if scriptElem is None: continue
            data = scriptElem.get_attribute('innerHTML')
            jsonData = json.loads(data)
            home = Home()
            home.type = jsonData["@type"]
            home.name = jsonData["name"]
            if 'value' in jsonData["floorSize"]:
                home.floorSize = jsonData["floorSize"]["value"]
            else:
                home.floorSize = "-"
            if 'numberOfRooms' in jsonData:
                home.numberOfRooms = jsonData["numberOfRooms"]
            else:
                home.numberOfRooms = ""
            home.address = jsonData["address"]["streetAddress"]
            home.locality = jsonData["address"]["addressLocality"]
            home.region = jsonData["address"]["addressRegion"]
            home.latitude = jsonData["geo"]["latitude"]
            home.longitude = jsonData["geo"]["longitude"]
            home.zipCode = jsonData["address"]["postalCode"]
            if stateElem is not None:
                home.state = stateElem.text
            else :
                home.state = ""
            if priceElem is not None:
                home.price = priceElem.text
            else:
                home.price = ""
            if overlayElem is not None:
                home.notification = overlayElem.text
            writer.writerow(home.__dict__)
        except Exception as e:
            pass
        
        # #data = item.find_element_by_xpath("//script[@type='application/ld+json']")
        # print(item.find_element_by_xpath("//script[@type='application/ld+json']").get_attribute('innerHTML'))
        # r = re.compile(r'\$(\d[\d.,]*) \((.*?)\)')
        # values = re.findall(r, item.find_element_by_class_name("price-reduction").text)
        # home.priceCut = values[1].replace(',', '')
        # home.priceCutDate = values[2]
        # r = re.compile(r'\d[\d.,]*')
        # values = re.findall(r, item.find_element_by_class_name("list-card-price").text)
        # home.price = values[0]list-loading-message-cover
class removed_element(object):
    def __init__(self, css_class):
        self.css_class = css_class
    def __call__(self, driver):
        try:
            target = driver.find_element_by_class_name(self.css_class)
            if target is None:
                return True
            else:
                return False
        except:
            return True


class page_has_loaded():
    def __call__(self, driver):
        page_state = driver.execute_script('return document.readyState;')
        if page_state == 'complete':
            return True
        else:
            return False

def waitPageLoaing(driver):
    # current_url = driver.current_url
    # WebDriverWait(driver, 30).until(EC.url_changes(
    #     current_url))  # list-loading-message-cover
    try:
        WebDriverWait(driver, 30).until(removed_element("list-loading-message-cover"))
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "zsg-pagination-next")))
        nextBtnElem = driver.find_element_by_class_name("zsg-pagination-next")
        if (nextBtnElem.text != "" ):
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='zsg-pagination-next']/a")))
        WebDriverWait(driver, 30).until(page_has_loaded())
    except:
        pass

def getDataFromFilter(driver, writer):
    while flag == True:
        time.sleep(2)
        try:
            nextBtnElem = driver.find_element_by_class_name("zsg-pagination-next")        
            waitPageLoaing(driver)
            collectData(driver, writer)
            if (nextBtnElem.text == ""):
                break        
            nextBtnElem.find_element_by_xpath("//a[@aria-label='NEXT Page']").click()
            waitPageLoaing(driver)
        except:
            pass
    time.sleep(2)

if __name__ == '__main__':
    
    print("Enter the browser to simulate")
    print("Chrome: 1")
    print("Firefox: 2")

    browserType = input("Enter : ")

    if (browserType == "1"):
        driver = createDriverInstance()
    else:
        #cap = DesiredCapabilities().FIREFOX.copy()
        #cap["marionette"] = True
        # binary = r'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
        # options = Options()
        # options.binary = binary
        # profile = webdriver.FirefoxProfile()
        # options.profile = profile
        # driver = webdriver.Firefox(options=options, executable_path="D:\\MUTT\\Mark\\scrape-zillow\\geckodriver.exe")
        driver = webdriver.Firefox()
    #driver.delete_all_cookies()
    #driver = webdriver.Firefox( options=options, capabilities=cap, executable_path="D:\\MUTT\\Mark\\scrape-zillow\\geckodriver.exe")
    wait = WebDriverWait(driver, 30)
    driver.get(baseUrl)
    driver.implicitly_wait(30)
    waitPageLoaing(driver)
    keyboard = Controller()
    with open('zipcodes.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            print(row[0])
            zipCode = row[0]
            #driver.delete_all_cookies()
            driver.execute_script('localStorage.clear();')
            try:
                searchTxtElem = driver.find_element_by_class_name("react-autosuggest__input")
            except:
                pass
            searchTxtElem.click()
            searchTxtElem.clear()            
            searchTxtElem.send_keys(Keys.CONTROL, 'a')
            keyboard.type(zipCode)

            #filterBtn = driver.find_element_by_id("listing-type")
            #filterBtn.click()
            #driver.find_element_by_id(
            #    "isForSaleByAgent_isForSaleByOwner_isNewConstruction_isComingSoon_isAuction_isForSaleForeclosure_isPreMarketForeclosure_isPreMarketPreForeclosure").click()
            
            searchTxtElem.send_keys(Keys.RETURN)
            
            waitPageLoaing(driver)
            
            flag = True
            fileName = zipCode + datetime.today().strftime("_%d_%m_%Y_%H_%M.csv")
            fieldNames = ['type', 'name', 'floorSize', 'numberOfRooms', 'address',
                        'locality', 'region', 'zipCode', 'latitude', 'longitude', 'state', 'price', 'notification']
            with open(fileName, 'w+') as csvFile:
                writer = csv.DictWriter(csvFile, fieldnames=fieldNames, delimiter=';', quoting=csv.QUOTE_NONE)
                writer.writeheader()
                try:
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "listing-type")))
                except:
                    pass
                filterBtn= driver.find_element_by_id("listing-type")
                filterBtn.click()
                #WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='isForRent']")))
                checkBox = driver.find_element_by_id(
                    "isForSaleByAgent_isForSaleByOwner_isNewConstruction_isComingSoon_isAuction_isForSaleForeclosure_isPreMarketForeclosure_isPreMarketPreForeclosure")
                if( checkBox.get_attribute('type') == "radio"):
                    print("radio")
                    #checkBox.click()
                    elemBtn = driver.find_element_by_css_selector(
                        "div.zsg-button.filter-button.filter-expandable")
                    if elemBtn.get_attribute('class') != "zsg-button filter-button filter-expandable filter_applied":
                        print("click")
                        elemBtn.click()
                        waitPageLoaing(driver)
                    getDataFromFilter(driver, writer)
                    
                    filterBtn.click()
                    #checkBox = driver.find_element_by_id("isForRent")
                    #checkBox.click()
                    elemBtn = driver.find_elements_by_xpath("//div[@class='zsg-button zsg-separator_secondary filter-button']")
                    if elemBtn[0].get_attribute('class') != "zsg-button zsg-separator_secondary filter-button filter_applied":
                        elemBtn[0].click()
                        waitPageLoaing(driver)
                    getDataFromFilter(driver, writer)

                    filterBtn.click()
                    #checkBox = driver.find_element_by_id("isRecentlySold")
                    if elemBtn[1].get_attribute('class') != "zsg-button zsg-separator_secondary filter-button filter_applied":
                        elemBtn[1].click()
                        waitPageLoaing(driver)
                    getDataFromFilter(driver, writer)
                else:
                    print("checkbox")
                    try:
                        elemBtn = driver.find_element_by_xpath(
                        "//div[@class='zsg-button filter-button filter-expandable']")
                        if elemBtn is not None:
                            elemBtn.click()
                            time.sleep(0.5)
                    except:
                        pass
                    #checkBox = driver.find_element_by_id("isForRent")
                    #checkBox.click()
                    try:
                        elemBtn = driver.find_elements_by_xpath(
                        "//div[@class='zsg-button zsg-separator_secondary filter-button']")
                        for item in elemBtn:
                            item.click()
                            time.sleep(0.5)
                    except:
                        pass
                    # print(len(elemBtn))
                    # if elemBtn[0].get_attribute('class') != "zsg-button zsg-separator_secondary filter-button filter_applied":
                    #     elemBtn[0].click()
                    #     time.sleep(0.5)
                    # #checkBox = driver.find_element_by_id("isRecentlySold")
                    # if elemBtn[1].get_attribute('class') != "zsg-button zsg-separator_secondary filter-button filter_applied":
                    #     elemBtn[1].click()

                    waitPageLoaing(driver)
                    getDataFromFilter(driver, writer)
                    # if checkBox.get_attribute('checked') == False:
                    #     elemBtn = driver.find_element_by_class_name(
                    #         "zsg-button.filter-button.filter-expandable")
                    #     elemBtn.click()
                    # checkBox = driver.find_element_by_id("isForRent")
                    # if checkBox.get_attribute('checked') == False:
                    #     elemBtn = driver.find_element_by_class_name(
                    #         "zsg-button.zsg-separator_secondary.filter-button")
                    #     elemBtn.click()
                    # checkBox = driver.find_element_by_id("isRecentlySold")
                    # if checkBox.get_attribute('checked') == False:
                    #     elemBtn = driver.find_element_by_class_name(
                    #         "zsg-button.zsg-separator_secondary.filter-button.filter_applied")
                    #     elemBtn.click()
                    # waitPageLoaing(driver)
                    # getDataFromFilter(driver, writer)



                
                       
        


