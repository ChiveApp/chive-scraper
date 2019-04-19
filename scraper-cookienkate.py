#!/usr/bin/env python3

import re
import json
import signal, sys

from pymongo import MongoClient
from scraperConnection import simple_get
from bs4 import BeautifulSoup




def fix_unicode(string):
    unicode_dict = {"\u00bd" : "1/2", "\u00bc" : "1/4", "\u2153" : "1/3", "\u00be" : "3/4", 
    "\u2019" : "'","\u201c":"\"", "\u2033":"\"","\u201d":"\"","\u00e9" : "e" ,
    "\u2014" : "-","\u00f1":"n" , "\u215b":"1/8", "\u00d7":"x" ,"\u2154":"2/3" ,"\u00a0" : "",
    "\u00ed" : "i", "\u00e8" : "e", "\u00ee" : "i", "\u00e7" : "c", "\u00b0" : " degrees ",
    "\u2026" : "...", "\u00e1" : "a", "\u2044" : "/", "\u2013" : "-", "\u00ae" : "", 
    "\u00e4" : "a"}
    for unicode_key in unicode_dict:
        string = string.replace(unicode_key, unicode_dict[unicode_key])
    return string

def get_recipe_pages(page):
    '''
    Will start from recipe index on cookie and kate page then scrape each recipe
    :param query:
    :return:
    '''
    if page == 0:
        url = "https://cookieandkate.com/category/food-recipes/"
    else:
        url = "https://cookieandkate.com/category/food-recipes/page/{}".format(page)
    #url = "https://cookieandkate.com/2019/sweet-potato-arugula-wild-rice-salad-recipe/"
    raw_html = simple_get(url)


    if raw_html is not None:
        html = BeautifulSoup(raw_html, "html.parser")
        return html
    else:
        print("failed")

def get_recipes():
    """
    This function returns n recipes with all the data associated with them
    based on ingredient, word, or category search
    Forking would be lit here
    :param search_type, num_recipes, query:
    :return:
    """


    pyclient = MongoClient()
    db = pyclient["chive"]
    collection = db["recipes"]

    for page in range(31, 35):
        html = get_recipe_pages(page)


        # nested findall searching for fixed-recipe-card and pulling url from a href

        for i, article in enumerate(html.find_all("div", {"class":"lcp_catlist_item"})):
            url = article.find("a")["href"]
            collection.insert_one(get_recipe_info(url))

            #get_recipe_info(url)
        print("Page: {} visited".format(page))





def get_recipe_info(url):
    raw_recipe_html = simple_get(url)
    recipe_html = BeautifulSoup(raw_recipe_html, "html.parser")

    # Check if any required values are None to avoid getting errors
    description = get_recipe_description(recipe_html)
    
    name = get_recipe_name(recipe_html)

    if name == "Bubblies on New Year's Eve": #fuck this check
        return
    rating = get_rating(recipe_html)
    #print(rating)
    cook_time = get_time_info(recipe_html)
    #print("{} seconds".format(cook_time))
    ingredients = get_ingredients(recipe_html)
    #print(ingredients)
    directions = get_directions(recipe_html)
    if not directions:
        return
    image = get_image(recipe_html)

    # Create JSON Object 
    data = {"name" : name, "description" : description, "ingredients" : ingredients, "directions" : directions, "time" : cook_time, "rating" : rating, "image" : image}
    #json_data = json.dumps(data)
    return(data)

# Title
def get_recipe_name(html):
    for i, li in enumerate(html.find_all("h1", {"class":"entry-title"})):
        return(fix_unicode(li.text.strip())) #TODO get this in a better form


def get_recipe_description(html):
    for i, li in enumerate(html.find_all("div", {"class":"tasty-recipes-description"})):
        description = li.text.strip()
        # for unicode_key in unicode_dict:
        #     description = description.replace(unicode_key, unicode_dict[unicode_key])
        description = fix_unicode(description)
        return(description)

def get_ingredients(html):
    '''
    This function scrapes ingredients from a single recipe page on the Cookie and Kate site. 
    Params: html 
    Return: ingredients [(Quantity, Unit, Ingredient)]
    '''


    units = ["Pinch ", " teaspoons ", " teaspoon ", " tablespoons ", " tablespoon ", " cups ", " cup ", " ounces ", " ounce ", " pounds ", " pound ", "Unit"]
    ingredients = []
    whole_ingredient_string = None
    unit_found = False
    for i, div in enumerate(html.find_all('div', {"class":"tasty-recipe-ingredients"})):
        for li in div.find_all("li"):
            whole_ingredient_string = li.text.strip()
            whole_ingredient_string = fix_unicode(whole_ingredient_string)

            # We are going to split up the ingredient string by measurement first
            for unit in units:
                if unit in whole_ingredient_string:
                    ingredient_string = whole_ingredient_string.split(unit)
                    unit_found = True
                    break
            if not unit_found:
                unit = ""
                quantity = ""
                ingredient = whole_ingredient_string
            else:
                quantity = ingredient_string[0]

                ingredient = ingredient_string[1]


            ingredients.append([ingredient, quantity, unit])
    return(ingredients)





# Time return is in seconds
def get_time_info(html):
    total = None
    time = None
    raw_time = html.find('span', {"class":"tasty-recipes-total-time"})
    if raw_time:
        time = raw_time.text.strip()

        if "min" in time and "hour" not in time:
            mins = time.split("minutes")
            if len(mins) == 2:
                total = int(mins[0])*60
            else:
                total = None

        elif "hour" in time and "min" in time:
            time = time.split(" ")
            if len(time) == 4:
                hours = int(time[0])
                mins = int(time[2])
                total = hours*3600+mins*60
            else: 
                total = None

        elif "hour" in time and "min" not in time:
            time = time.split(" ")
            if len(time) == 2:
                hours = int(time[0])
                total = hours*3600
            else:
                total = None

    return total

# Directions
def get_directions(html):
    #directions = []
    directions = None
    for i, li in enumerate(html.find_all('div',"tasty-recipe-instructions")):
       directions = li.text.strip()
    if directions:
        directions = fix_unicode(directions)
        directions = directions.split('.')

    return directions

# Ratinginfo


def get_rating(html):

    rating = html.find('span', {"class":"average"})
    if rating is not None:
        rating = rating.text.strip()
        return(rating)
    else:
        return(0.0)



def get_image(html):
    photos = [x['src'] for x in html.findAll('img')]
    photo = photos[3] # Hard coded cause fuck
    return(photo)



get_recipes()


# This being a hoe
# def sig_handler(sig, frame):
#     '''
#     Exits the program gracefully when CTRL+C is pressed
#     '''
#     print("hello")
    

#     sys.exit(0)

# signal.signal(signal.SIGINT, sig_handler)
# signal.pause()
