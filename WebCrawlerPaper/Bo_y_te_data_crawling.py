from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


# Khởi tạo WebDriver
driver = webdriver.Chrome()
# Mở URL
driver.get('https://moh.gov.vn/tin-tong-hop')
all_page_urls = []
all_titles = []
all_times = []

while True:
    try: 
        # Tìm tất cả các thẻ a có trong các h3 có class 'asset-title'
        links = driver.find_elements(By.CSS_SELECTOR, 'h3.asset-title a')
        one_page_urls = [link.get_attribute('href') for link in links]
        all_page_urls = all_page_urls + one_page_urls
        
        # Tìm tất cả các phần tử chứa tiêu đề
        titles = driver.find_elements(By.CSS_SELECTOR, "h3.asset-title a")
        one_page_titles = [title.text for title in titles]
        all_titles = all_titles + one_page_titles
        
        # Tìm tất cả các phần tử chứa thời gian
        times = driver.find_elements(By.CSS_SELECTOR, "span.time")
        one_page_times = [time.text for time in times]
        all_times = all_times + one_page_times
        
        print(len(all_page_urls))

        # Chờ đợi cho đến khi nút "Tiếp theo" xuất hiện và có thể click được
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Tiếp theo')]"))
        )
        next_button.click()
        
        print("Đã click vào nút 'Tiếp theo!")
        # sleep(random.randint(1, 3))
    
    except: 
        print("Nút 'Tiếp theo' đã bị disable!")
        break

# Đóng trình duyệt
driver.quit()      


id = [f'{element}' for element in list(range(10000, 10000 + len(all_page_urls)))]    
df = pd.DataFrame({"doc_id": id, "url": all_page_urls, "title": all_titles, "times_post": all_times})
# df.to_csv("all_posts.csv", sep=';')
df.head() 