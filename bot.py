import os
import base64
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from datetime import datetime




load_dotenv()

EMAIL=os.getenv("LOGIN_EMAIL")
PASSWORD=os.getenv("LOGIN_PASSWORD")
TG_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT=os.getenv("TELEGRAM_CHAT_ID")

options=Options()
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")
# options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver=webdriver.Chrome(service=service, options=options)

#created a wait object for 15 sec wait time
wait=WebDriverWait(driver,15)

#gave a login url for Qspiders here
login_url="https://student.qspiders.com/"
driver.get(login_url)

#trying to find the email element after waiting to load


try:
    email=wait.until(EC.presence_of_element_located((By.NAME,"email")))

except:
    email=driver.find_element(By.NAME,"email")

#clearing and typing email
email.clear()
email.send_keys(EMAIL)

# now same for password, since there are 4 elements and first 3 are not displayed
#we have to find the password that is displayed

pwd_elements=driver.find_elements(By.NAME,"password")
pwd = None
for elem in pwd_elements:
    if elem.is_displayed():
        pwd=elem
        break
if pwd is None:
    raise Exception("No visible password element displayed")
pwd.clear()
pwd.send_keys(PASSWORD)

#now finding and clicking submit(login button)
submit=driver.find_element(By.XPATH,"//button[@type='submit']")
submit.click()

#finding and pressing the qrbtn
qr_btn=wait.until(EC.presence_of_element_located((By.XPATH,"//button[span[contains(normalize-space(text()),'QRCode')]]")))
qr_btn.click()

#wait and get the src of the qr image
modal_img=wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"div.grid.justify-items-center img")))
src=modal_img.get_attribute("src")

#checking if the image is base64, then splitting and storing it
if src.startswith("data:image"):
    header,b64data=src.split(",",1)
    img_bytes=base64.b64decode(b64data)
    with open("qrcode.png","wb") as f:
        f.write(img_bytes)
else:
    modal_img.screenshot("qrcode.png")

# creating a fn for sending the image to telegram with day as caption
now=datetime.now()
captiondate=now.strftime("%d-%b-%a")



def send_to_telegram(token,chat_id,img_path,caption):
    url=f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(img_path,"rb") as img:
        files={"photo":img}
        data={"chat_id":chat_id}
        if caption:
            data["caption"]=caption
        resp=requests.post(url,data=data,files=files,timeout=30)
    resp.raise_for_status()
    return resp.json()
send_to_telegram(TG_TOKEN,TG_CHAT,"qrcode.png",f"Good Morning Sagar!😊🌟\nHere's your QRCode for the day\n{captiondate}")
driver.quit()

