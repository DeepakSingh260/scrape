
import aiohttp
import asyncio 
import bs4 
import re 
from pandas import read_excel 
import time 
from function import *

field = input()

web_site = 'https://scholar.google.com'
base_url="https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors="
to_cut = len(base_url)

def create_links():
	return base_url+field

async def fetch_all_data(url ):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:

			name = url[to_cut:]
			status = response.status

			response = await response.text()
			soup = bs4.BeautifulSoup(response , 'html.parser')
			for tag in  soup.find_all("h3" , {'class' : 'gs_ai_name'}):
				print(tag.text)


def print_all_pages():
	pages = create_links()
	tasks = []
	print(pages)
	loop = asyncio.new_event_loop()

	try:

		
		tasks.append(loop.create_task(fetch_all_data(pages)))
			
		loop.run_until_complete(asyncio.wait(tasks))

	except KeyboardInterrupt:

		print("Program Terminated by User")

		print("<---Bye--->")

	loop.close()

print_all_pages()