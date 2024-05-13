import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

options = webdriver.EdgeOptions()

output_locations = [
    r"C:\Users\Iggy\Desktop\Faks\2. Semestar\APVO\pdf\01_humanisticke-znanosti",
    r"C:\Users\Iggy\Desktop\Faks\2. Semestar\APVO\pdf\02_biomedicina-i-zdravstvo",
    r"C:\Users\Iggy\Desktop\Faks\2. Semestar\APVO\pdf\03_tehnicke-znanosti",
    r"C:\Users\Iggy\Desktop\Faks\2. Semestar\APVO\pdf\04_drustvene-znanosti",
    r"C:\Users\Iggy\Desktop\Faks\2. Semestar\APVO\pdf\05_prirodne-znanosti",
    r"C:\Users\Iggy\Desktop\Faks\2. Semestar\APVO\pdf\06_biotehnicke-znanosti"
]

for i in range(1, 7):
    url = pd.read_csv(rf"C:\Users\Iggy\Desktop\Faks\2. Semestar\APVO\dabar_popis_radova_{i}.csv", usecols=['url'], delimiter=';')
    options.add_experimental_option("prefs", {"download.default_directory": output_locations[i-1]})
    driver = webdriver.Edge(options=options)
    print(url)
    for j in range(len(url)):
        driver.get("https://www.google.com/")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.COMMAND + 't')
        driver.get(url.iloc[j, 0])
        time.sleep(1)
        downloadButton = driver.find_element(By.CLASS_NAME, "pdf_download").click()
        time.sleep(2)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.COMMAND + 'w')



driver.quit()





