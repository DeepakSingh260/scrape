import aiohttp
import asyncio
import bs4
import re
import urllib
import requests
from pandas import read_excel
import time
from function import *
ind=0
field = input()
nameList = []
web_site = 'https://scholar.google.com/'
base_url = "https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors="
to_cut = len(base_url)
def download_subpage(link):
    r1=requests.get(web_site + link)
    return r1.text


def data_not_available(url ):
    print("Data not available for " +str(url))
def create_links():
    return base_url+field

async def find_and_extract_data_name(soup):

    central_table = soup.find(id = "gsc_prf_w")
    description = central_table.find("div" , {'class' : "gsc_prf_il"})
    fields = []

    for field in central_table.find("div" , {'class' : "gsc_prf_il" , 'id' : "gsc_prf_int"} ).contents:
        if isinstance(field , bs4.element.NavigableString):
            continue

        if isinstance(field , bs4.element.Tag):
            fields.append(field.text)

    corner_table = soup.find("div",{"class":"gsc_rsb_s gsc_prf_pnl"})

    try:
        # num_cit_index = list(corner_table.find_all("td" , {"class":"gsc_rsb_std"}))
        num_cit_index=list(corner_table.find_all("td", {"class":"gsc_rsb_std"}))
        hist = corner_table.find("div" , {"class":"gsc_md_hist_b"}).contents

    except:
        raise ValueError


    for i in range(len(hist)):
        if isinstance(hist[i] , bs4.element.Tag):
            hist.append(hist[i])

    num_cit = num_cit_index[0].text
    h_index = num_cit_index[2].text
    ii0_index = num_cit_index[4].text
    n6 = hist[-6].text
    n5 = hist[-5].text
    n4 = hist[-4].text
    n3 = hist[-3].text
    n2 = hist[-2].text
    n1 = hist[-1].text
    Data = [num_cit , h_index , ii0_index , fields , n6,n5,n4,n3,n2,n1]
    return Data


def create_linksName(x):

    all = []

    URL = base_url
    for a in x:
        URL += a + "+"

    # all.append(URL)
    # all = cut(all, n)

    return URL[:len(URL)-1]


async def fetch_all_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            name = url[to_cut:]
            status = response.status

            response = await response.text()
            soup = bs4.BeautifulSoup(response , 'html.parser')

            for tag in  soup.find_all("h3" , {'class' : 'gs_ai_name'}):
                # print(tag.text)
                name = [x for x in str(tag.text).split()]
                print(name)
                nameList.append(create_linksName(name))
                

async def fetch_all_data_name(url):



    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            name = url

            status = response.status
            response = await response.text()

            if status == 429:
                print("too many request to server , error code : 429")

            # if verbose:
            #     print(name, status)


            soup = bs4.BeautifulSoup(response , 'html.parser')

            result = soup.find("h3" , {'class' : 'gs_ai_name'})

            if result is None:

                data_not_available(f,name)
            else :

                link = result.find('a' , href = re.compile(r'[/]([a-z]|[A-Z])\w+')).attrs['href']
                print("LINK:  " + str(link))
               

                L = []

                async with session.get(web_site+link) as subresponse:

                    print("request: " + name + " with status: " + str(subresponse.status))

                    html = await subresponse.text()
 
                    soup = bs4.BeautifulSoup(html ,'html.parser')
                    Data = await find_and_extract_data_name(soup)
                    # soup = bs4.BeautifulSoup(download_subpage(link), 'html.parser')
                    print(Data)
                    # a = await store_in_list(L,name , Data)

                    # await save_in_file(f,name , Data)

                # ind+=1

           


def print_all_pages():
    pages = create_links()
    tasks = []
    names = []
    print(pages)
    loop = asyncio.new_event_loop()

    try:

        tasks.append(loop.create_task(fetch_all_data(pages)))

        loop.run_until_complete(asyncio.wait(tasks))

    except KeyboardInterrupt:

        print("Program Terminated by User")

        print("<---Bye--->")

    loop.close()

    loop = asyncio.new_event_loop()

    try:
        for page in nameList:

            names.append(loop.create_task(fetch_all_data_name(page)))


            loop.run_until_complete(asyncio.wait(names))

    except KeyboardInterrupt:

        print("Program Terminated by User")

        print("<---Bye--->")

    loop.close()







print_all_pages()