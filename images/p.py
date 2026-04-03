from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def send_whatsapp_message(phone_number, message, quantity):

    url = f"https://web.whatsapp.com/send?phone={phone_number}"

    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:\\Users\\MEET\\whatsapp_profile")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    wait = WebDriverWait(driver, 60)

    try:
        # Wait until chat input box appears
        input_box = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
        )

        time.sleep(2)

        for i in range(quantity):
            input_box.send_keys(message)
            input_box.send_keys(Keys.ENTER)
            print(f"Message {i+1} sent ✅")
            time.sleep(1.5)   # small delay to avoid spam detection

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
    driver.quit()


phone = ""
msg = "Hello  Automation Test"
qty = 100

send_whatsapp_message(phone, msg, qty)