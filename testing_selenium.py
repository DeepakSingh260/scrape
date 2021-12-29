from selenium import webdriver

from time import sleep 
# browser = webdriver.Safari()

op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome(options=op)
browser.get('https://scholars.iitm.ac.in')
browser.maximize_window()

sample = "deep learning"
browser.find_element_by_id("keywords").send_keys(sample)
browser.find_element_by_id("elasticSearch").click()
sleep(8)
try:
	
	items = []
	containers =  browser.find_element_by_xpath('.//div[@class="container"]')
	for items in containers:
	    name = items.find_element_by_xpath('.//div[@class="col-md-3"]')
	    print(name.text)
	sleep(5)
finally:

	browser.quit() 