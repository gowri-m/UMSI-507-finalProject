#################################
##### Name: Gowri Murthy
##### Uniqname: gowri
#################################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3 
from sys import exit
import plotly.graph_objs as go
import webbrowser


BASE_URL = "https://www.tripadvisor.in"
DB_NAME = 'tripAdvisor.sqlite'

def get_connection():
    ''' returns a connection to the database

    Parameters
    ----------
    none

    Returns
    -------
    connection to the database
    '''
    return sqlite3.connect(DB_NAME)


def get_hotels_list(path = "/Hotels-g297628-Bengaluru_Bangalore_District_Karnataka-Hotels.html"):
    ''' gets the list of top 120 hotels in Bangalore

    Parameters
    ----------
    path : string
        path to the tripAdvisor page 

    Returns
    -------
    none
    '''

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
    ''' performs pagination, gets the link for list of next 30 hotels 

    Parameters
    ----------
    main_div : string
        html code of the current page

    Returns
    -------
    none
    '''
    next_page_div = main_div.find("div",id="taplc_main_pagination_bar_dusty_hotels_resp_0")
    next_page = next_page_div.find(class_ = "unified ui_pagination standard_pagination ui_section listFooter").find(class_="nav next ui_button primary")
    next_page_path = next_page['href']
    next_page_num = int(next_page['data-page-number'])
    if(next_page_num < 6):
        get_hotels_list(next_page_path)


def get_hotel_path():
    ''' gets the path for each hotel from the database
    Parameters
    ----------
    none

    Returns
    -------
    none
    '''
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
    ''' retrives information about the hotel

    Parameters
    ----------
    path : string
        path to the hotel's tripAdvisor page

    Returns
    -------
    none
    '''
    rating = 0.0
    reviews = 0
    pool = ""
    internet = ""
    bar = ""
    coffee_maker = ""

    url = BASE_URL + path
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html.parser')
    name_div = soup.find("div",id="taplc_hotel_review_atf_hotel_info_web_component_0")
    name_child_div = name_div.find("div",class_="_1vnZ1tmP")
    name = name_child_div.find("h1", id = "HEADING").text
    about_div = soup.find("div", id = "taplc_about_with_photos_react_ssronly_0")

    if(about_div != None):
        about_child_div = about_div.find("div", id="ABOUT_TAB")
        rating  = float(about_child_div.find("span",class_ = "_3cjYfwwQ").text)
        reviews = int(about_child_div.find("span",class_="_3jEYFo-z").text.split()[0].replace(",",""))
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
    ''' creates Hotels and Info tables

    Parameters
    ----------
    none

    Returns
    -------
    none
    '''
    conn = get_connection()
    cur = conn.cursor()
    drop_hotels_list_sql = 'DROP TABLE IF EXISTS "Hotels"'
    drop_hotels_info_sql = 'DROP TABLE IF EXISTS "Info"'

    create_hotels_list_sql = '''
        CREATE TABLE "Hotels" (
	"Id"	INTEGER,
	"Name"	TEXT NOT NULL,
	"Link"	TEXT NOT NULL,
	PRIMARY KEY("Id" AUTOINCREMENT),
	FOREIGN KEY("Id") REFERENCES "Info"("Id")
)
    '''

    create_info_sql = '''
        CREATE TABLE "Info" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
            "Name" TEXT NOT NULL,
            "Rating" REAL NOT NULL,
            "Reviews" INTEGER NOT NULL,
            "Pool" TEXT NOT NULL,
            "Internet" TEXT NOT NULL,
            "Bar" TEXT NOT NULL,
            "CoffeeMaker" TEXT NOT NULL,
            FOREIGN KEY("Id") REFERENCES "Hotels"("Id")
        )
    '''

    cur.execute(drop_hotels_list_sql)
    cur.execute(drop_hotels_info_sql)
    cur.execute(create_hotels_list_sql)
    cur.execute(create_info_sql)
    conn.commit()
    conn.close()


def load_hotels_list(name, link):
    ''' inserts the list of hotels got from crawling tripAdvisor into
    the database into Hotels table

    Parameters
    ----------
    name : string
        name of the hotel
    link : string
        path to the hotel's page

    Returns
    -------
    none
    '''

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
    ''' inserts information about each hotel to Info table

    Parameters
    ----------
    name : string
        name of the hotel
    rating : float
        hotel's rating
    reviews : int
        total number of reviews for the particular hotel
    pool : string
        "Yes" is pool is available, else "No"
    internet : string
        "Yes" is internet is available, else "No"
    bar : string
        "Yes" is bar is available, else "No"
    coffee_maker : string
        "Yes" is coffee_maker is available, else "No"

    Returns
    -------
    none
    '''

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

def print_menu():
    ''' displays options available for the user to choose from

    Parameters
    ----------
    none

    Returns
    -------
    none
    '''
    print("1. Distribution of hotels in Bangalore based on rating")
    print("2. Distribution of hotels in Bangalore based on number of reviews")
    print("3. Search for a hotel based on rating and amenities")

def search_hotels():
    ''' looks up hotels based on rating and amenities interested in

    Parameters
    ----------
    none

    Returns
    -------
    none
    '''
    while(True):
        rating = input("Enter a rating[0-5] above which to search hotels: ")
        if (rating.isnumeric()):
            float_rating = float(rating)
            if(float_rating in range(0,6)):
                opt = get_amenity()
                draw_plot(rating,opt)
        else:
            print("Invalid Input")


def get_amenity():
    ''' returns amenity user is interested in

    Parameters
    ----------
    none

    Returns
    -------
    opt : int
        number associated with amenity
    '''
    conn = get_connection()
    cur = conn.cursor()
    print('''
1. Pool
2. Bar
3. Internet
4. Coffee Maker in room''')
    opt = input("\nChoose an amenity you are interested in: ")
    if(opt.isdigit() and int(opt) in range(1,5)):
        return(int(opt))
    else:
        print("Enter a valid choice")


def draw_plot(rating,opt):
    ''' draws graphs showing distribution of hotels with a particular rating 
    having an amenity

    Parameters
    ----------
    rating : float
        rating above which to look for hotels
    opt : int
        chosen amenity option

    Returns
    -------
    none
    '''
    xvals = []
    yvals = []
    conn = get_connection()
    cur = conn.cursor()
    
    if(opt == 1):
        query = '''SELECT Count(Id),Rating,Pool 
                FROM "Info"
                WHERE Rating >= ? AND Pool = "Yes"
                Group By Rating
                '''
        q_top10 = '''SELECT Id,Name
                FROM Info
                Where Rating >= ? AND Pool = "Yes"
                Limit 10'''

        amenity = "Pool"

    elif(opt == 2):
        query = '''SELECT Count(Id),Rating,Bar 
                FROM "Info"
                WHERE Rating >= ? AND Bar = "Yes"
                Group By Rating'''

        q_top10 = '''SELECT Id,Name
                FROM Info
                Where Rating >= ? AND Pool = "Yes"
                Limit 10'''

        amenity = "Bar"

    elif(opt == 3):
        query = '''SELECT Count(Id),Rating,Internet 
                FROM "Info"
                WHERE Rating >= ? AND Internet = "Yes"
                Group By Rating'''
        
        q_top10 = '''SELECT Id,Name
                FROM Info
                Where Rating >= ? AND Pool = "Yes"
                Limit 10'''

        amenity = "Internet"

    elif(opt == 4):
        query = '''SELECT Count(Id),Rating,CoffeeMaker 
                FROM "Info"
                WHERE Rating >= ? AND CoffeeMaker = "Yes"
                Group By Rating'''
        
        q_top10 = '''SELECT Id,Name
                FROM Info
                Where Rating >= ? AND Pool = "Yes"
                Limit 10'''

        amenity = "Coffer maker"

    else:
        print("Invalid Selection")
        exitFromProgram()

    res = cur.execute(query,rating) 
    for r in res:
        xvals.append(r[1])
        yvals.append(r[0])

    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title="A bargraph showing distribution of hotels above rating "+rating+" having a"+amenity,xaxis = dict(
        title = "Rating",
        tickmode = 'linear',
        tick0 = 0,
        dtick = 0.5
    ),
    yaxis = dict(
        title = "Number of hotels"
    )
    )
    fig = go.Figure(data=bar_data,layout = basic_layout)
    fig.write_html("bar.html", auto_open=True)
    list_top10 = cur.execute(q_top10,rating)
    print("Top 10 hotels in Bangalore with rating",rating,"and above with",amenity,"are:" )
    launch_hotel(list_top10)
    conn.close()


def launch_hotel(res):
    ''' launches the url of the hotel

    Parameters
    ----------
    res : sql query result
        result of the sql query

    Returns
    -------
    none
    '''
    name = []
    conn = get_connection()
    cur = conn.cursor()
    i = 1
    for r in res:
        print(i,r[1])
        name.append(r[0])
        i = i+1
    while(True):
        x = input("Choose a hotel to view it on tripAdvisor, enter a number: ")
        if(x.isdigit() and int(x) in range(1,11)):
            sel = name[int(x)-1]
            print(sel)
            q = ''' 
                Select Info.Id,Hotels.Name,Hotels.Link
                FROM Info
                JOIN Hotels
                ON Info.Id = Hotels.Id
                WHERE Info.Id = ?
                '''
            link  = cur.execute(q,[sel])
            for item in link:
                url = BASE_URL + item[2]
                webbrowser.open(url)
                exitFromProgram()
        else:
            print("Invalid Input")
    conn.close()
             
    

def rating_distribution_chart():
    ''' draws a bar graph showing the distribution of ratings of top 150 hotels in Bangalore

    Parameters
    ----------
    none

    Returns
    -------
    none
    '''
    xvals = []
    yvals = []
    conn = get_connection()
    cur = conn.cursor()
    get_rating = '''
    SELECT Rating,Count(Id)
    FROM "Info"
    GROUP BY Rating
    '''

    res = cur.execute(get_rating)
    for item in res:
        xvals.append(item[0])
        yvals.append(item[1])

    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title="A bar plot showing number of hotels for each rating",xaxis = dict(
        title = "Rating",
        tickmode = 'linear',
        tick0 = 0,
        dtick = 0.5
    ),
    yaxis = dict(
        title = "Number of hotels"
    )
    )
    fig = go.Figure(data=bar_data,layout = basic_layout)
    
    fig.write_html("ratingDist.html", auto_open=True)

    conn.close()
    

def reviews_distribution_chart():
    ''' draws a histogram showing the distribution of reviews of top 150 hotels in Bangalore

    Parameters
    ----------
    none

    Returns
    -------
    none
    '''
    xvals = []
    conn = get_connection()
    cur = conn.cursor()
    get_reviews = '''
    SELECT Reviews 
    FROM "Info"
    '''
    res = cur.execute(get_reviews)
    for item in res:
        xvals.append(item[0])
    hist_data = go.Histogram(x=xvals)
    basic_layout = go.Layout(title="Distribution of total number of reviews for the top 150 hotels in Bangalore",xaxis = dict(
        title = "Number of Reviews",
        tickmode = 'linear',
        tick0 = 0,
        dtick = 500,
    ),
    bargap = 0.05
    )
    fig = go.Figure(data=hist_data,layout = basic_layout)
    fig.write_html("reviewDist.html", auto_open=True)
    conn.close()
    

if __name__ == "__main__":
    print("Fetching Data...")
    create_db()
    get_hotels_list()
    get_hotel_path()

    while(True):
        print_menu()
        sel = input("Enter an option from the above list or enter 'exit' to quit: ")
        if (sel.isdigit()):
            int_sel = int(sel)
            if(int_sel in range(1,4)):
                if(int_sel == 1):
                    rating_distribution_chart()
                elif(int_sel == 2):
                    reviews_distribution_chart()
                elif(int_sel == 3):
                    search_hotels()
            else:
                print("Invalid selection. Please enter a number between 1 and 3 or 'exit' to quit")
        elif(sel == "exit"):
            exitFromProgram()
        else:
            print("Invalid selection.")
    

