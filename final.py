#################################
##### Name: Gowri Murthy
##### Uniqname: gowri
#################################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3 
from sys import exit


BASE_URL = "https://www.tripadvisor.in"
DB_NAME = 'tripAdvisor.sqlite'

def get_connection():
    return sqlite3.connect(DB_NAME)

def get_hotels_list(path = "/Hotels-g297628-Bengaluru_Bangalore_District_Karnataka-Hotels.html"):

    url = BASE_URL + path
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html.parser')
    main_div = soup.find(class_ = "bodycon_main")
    hotels_list = main_div.find_all(class_="listing_title")

    conn = get_connection()

    for item in hotels_list:
        x = item.select_one('a')
        link = x['href']
        text = x.text
        load_hotels_list(text, link)

    get_next_page(main_div)

    conn.commit()
    conn.close()


def get_next_page(main_div):
    next_page_div = main_div.find("div",id="taplc_main_pagination_bar_dusty_hotels_resp_0")
    next_page = next_page_div.find(class_ = "unified ui_pagination standard_pagination ui_section listFooter").find(class_="nav next ui_button primary")
    next_page_path = next_page['href']
    next_page_num = int(next_page['data-page-number'])
    if(next_page_num < 5):
        get_hotels_list(next_page_path)


def get_hotel_path():
    conn = get_connection()
    cur = conn.cursor()

    select_hotel_path_sql = '''
        SELECT Link FROM Hotels
    '''
    
    cur.execute(select_hotel_path_sql)
    results = cur.fetchall()
    for r in results:
        get_info(r[0])
        
    conn.close()

def get_info(path):
    url = BASE_URL + path
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html.parser')
    name_div = soup.find("div",id="taplc_hotel_review_atf_hotel_info_web_component_0")
    name = name_div.find("h1", id = "HEADING").text
    about_div = soup.find("div", id = "taplc_about_with_photos_react_ssronly_0")
    about_child_div = about_div.find("div", class_="_3koVEFzz")
    rating  = float(about_child_div.find("span",class_ = "_3cjYfwwQ").text)
    reviews = int(about_child_div.find("span",class_="_3jEYFo-z").text.split()[0].replace(",",""))
    #amenities_div = about_child_div.find("div", class_="ssr-init-26f")
    prop_amenities = about_child_div.find("div", class_="_1nAmDotd")
    if(prop_amenities.find("span",class_="ui_icon pool _13VIieax") != None):
        pool = "Yes"
    else:
        pool = "No"
    
    if(prop_amenities.find("span",class_="ui_icon internet _13VIieax") != None or prop_amenities.find("span",class_="ui_icon wifi _13VIieax") != None):
        internet = "Yes"
    else:
        internet = "No"

    if(prop_amenities.find("span",class_="ui_icon bar _13VIieax") != None):
        bar = "Yes"
    else:
        bar = "No"

    if(prop_amenities.find("span",class_="ui_icon restaurants _13VIieax") != None):
        coffee_maker = "Yes"
    else:
        coffee_maker = "No"

    load_hotel_info(name,rating,reviews,pool,internet,bar,coffee_maker)



def create_db():
    conn = get_connection()
    cur = conn.cursor()
    drop_hotels_list_sql = 'DROP TABLE IF EXISTS "Hotels"'
    drop_hotels_info_sql = 'DROP TABLE IF EXISTS "Info"'

    create_hotels_list_sql = '''
        CREATE TABLE IF NOT EXISTS "Hotels" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
            "Name" TEXT NOT NULL,
            "Link" TEXT NOT NULL
        )
    '''

    create_info_sql = '''
        CREATE TABLE IF NOT EXISTS "Info" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
            "Name" TEXT NOT NULL,
            "Rating" REAL NOT NULL,
            "Reviews" INTEGER NOT NULL,
            "Pool" TEXT NOT NULL,
            "Internet" TEXT NOT NULL,
            "Bar" TEXT NOT NULL,
            "CoffeeMaker" TEXT NOT NULL
        )
    '''

    cur.execute(drop_hotels_list_sql)
    cur.execute(drop_hotels_info_sql)
    cur.execute(create_hotels_list_sql)
    cur.execute(create_info_sql)
    conn.commit()
    conn.close()


def load_hotels_list(name, link):

    insert_hotelsList_sql = '''
        INSERT INTO Hotels
        VALUES (NULL, ?, ?)
    '''

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(insert_hotelsList_sql,
            [
                name,
                link
            ]
        )
    conn.commit()
    conn.close()

def load_hotel_info(name,rating,reviews,pool,internet,bar,coffee_maker):

    insert_info_sql = '''
        INSERT INTO Info
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
    '''
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(insert_info_sql,
            [
                name,
                rating,
                reviews,
                pool,
                internet,
                bar,
                coffee_maker
            ]
        )
    conn.commit()
    conn.close()

def exitFromProgram():
    ''' exits from the program

    Parameters
    ----------
    none

    Returns
    -------
    none
    '''
    print("\nBye!")
    exit(0)


create_db()
get_hotels_list()
get_hotel_path()
print("Done")