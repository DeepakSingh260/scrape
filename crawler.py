import aiohttp
import asyncio 
import bs4 
import re 
from pandas import read_excel 
import time 
from function import *

debug = False

verbose = True 

my_sheet = 'new_file'

file_name = 'my_file.xlsv'

df = [['Mahajan' , 'Gupta'] ,['Jyoti' , 'Ram']]

output = "stats.txt" 

def enable_debug_mode(debug_bool):
    if debug_bool == True:
        web_site = 'http://127.0.0.1:5000'
        base_url="http://127.0.0.1:5000/"
    else:
        web_site = 'https://scholar.google.com'
        base_url="https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors="
    
    return web_site, base_url , len(base_url)


web_site , base_url, to_cut = enable_debug_mode(debug)

async def get_name(url):

	name = url[to_cut:]

	return name

async def save_in_file(f, name, Data):

    temp_name_list=name.split('+')
    name=temp_name_list[0]
    surname=temp_name_list[1]
    print("saving: " + name + " " + surname)
    f.write(name + "; " + surname + "; ")
    f.write(Data[0] + "; " + Data[1] + "; " + Data[2] + "; ")
    for i in Data[3]:
        f.write(i + ", ")
    f.write("; " + Data[4] + "; " + Data[5] + "; " + Data[6] + " ;" + Data[7]+ "; " + Data[8] + "; " + Data[9] + "\n")

async def find_and_extract_data(soup):

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

async def fetch_all_data(url,f):



    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            name = url[to_cut:]

            status = response.status
            response = await response.text()

            if status == 429:
                print("too many request to server , error code : 429")

            if verbose:
                print(name, status)


            soup = bs4.BeautifulSoup(response , 'html.parser')

            result = soup.find("h3" , {'class' : 'gs_ai_name'})

            if result is None:

                data_not_available(f,name)
            else :

                link = result.find('a' , href = re.compile(r'[/]([a-z]|[A-Z])\w+')).attrs['href']
                print("LINK:  " + str(web_site+link))

                L = []

                async with session.get(web_site+link) as subresponse:

                    print("request: " + name + " with status: " + str(subresponse.status))

                    html = await subresponse.text()
 
                    soup = bs4.BeautifulSoup(html ,'html.parser')
                    Data = await find_and_extract_data(soup)

                    # a = await store_in_list(L,name , Data)

                    await save_in_file(f,name , Data)


def cut(L , n ):

    if n == 0:
        n= len(L)

    return L[:n]

def create_links(n):

    all = []

    for i in range(len(df[0])):
        name = df[1][i]
        surname = df[0][i]

        if isinstance(name , str) and isinstance(surname ,str) :
            all.append(base_url+name+"+"+surname)


        else:
            break

    all = cut(all ,n)

    return all

def init_file():

    f=open("stats_parallel.txt","a")
    #create base columns Names
    for i in range(len(df[0])):
        f.write(df[1][0] + "; ")
        f.write("\n")
    return f

def close_file(f):

    print("File saved \n")
    f.close()

def print_all_pages(n , out):

    f = init_file()

    pages = create_links(n)

    tasks = []
    loop = asyncio.new_event_loop()

    try:
        for page in pages:

            tasks.append(loop.create_task(fetch_all_data(page, f)))

        loop.run_until_complete(asyncio.wait(tasks))

    except KeyboardInterrupt:

        print("Program Terminated by User")

        print("<---Bye--->")

    loop.close()
    close_file(f)


def main(out_file):
    n=5
    print_all_pages(n,out_file)


if __name__ == '__main__':
    main(output)






	













	