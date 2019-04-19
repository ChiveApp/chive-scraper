#!/usr/bin/env python3

import re
import json

from pymongo import MongoClient
from scraperConnection import simple_get
from bs4 import BeautifulSoup

# TODO use threads for recipes?
# For now we're focusing on using only allrecipes.com

# in the future when we want to scrap other sites we just need
# to check the host in the get (or post?)

# This is how the search works, we might be able to make this dictate where we pull
# recipes from
# https://www.allrecipes.com/search/results/?wt=word%20word%20word&sort=re

# This is how the search per ingredient is :
# https://www.allrecipes.com/search/results/?ingIncl=carrot,chicken&sort=re

# The list of recipes is in
# <article class="fixed-recipe-card">
# in this section there is all information if we need rating n more
# <a ng-class=" ...
# in this : data-id can be used to find the recipe site to pull from
# https://www.allrecipes.com/recipe/30485/ < data id





def get_html(page):
    '''
    This function grabs the search html for a recipe search based on name of meal

    :param query:
    :return:
    '''
    #query_url = query.replace(" ", "%20")
    search = "pork"
    if page == 0:
        search_url = "https://www.allrecipes.com/search/results/?wt={}&sort=re".format(search)
    else:
        search_url = "https://www.allrecipes.com/search/results/?wt={}&sort=re&page={}".format(search, page)

    raw_search_html = simple_get(search_url)

    if raw_search_html:
        search_html = BeautifulSoup(raw_search_html, "html.parser")

        return search_html
    else:
        print ("failed")




def get_recipes():
    """
    This function returns n recipes with all the data associated with them
    based on ingredient, word, or category search
    :param search_type, num_recipes, query:
    :return:
    """
    pyclient = MongoClient()
    db = pyclient["chive"]
    collection = db["recipes"]

    for page in range(18, 255):
        search_html = get_html(page)

        # This is where forks or threads would be great
        # nested findall searching for fixed-recipe-card and pulling url from a href
        for i, article in enumerate(search_html.find_all("article", {"class": "fixed-recipe-card"})):
            recipe_url = article.find("a")["href"]
            # call a recipe info function
            # place return into a database or what not
            data_to_insert = get_recipe_info(recipe_url)

            collection.insert_one(data_to_insert)
            #get_recipe_info(recipe_url)
        print("Page: {} visited".format(page))



def get_recipe_info(url):
    raw_recipe_html = simple_get(url)
    recipe_html = BeautifulSoup(raw_recipe_html, "html.parser")


    name = get_recipe_name(recipe_html)
    description = get_description(recipe_html)
    rating = get_rating(recipe_html)
    cook_time = get_time_info(recipe_html)
    ingredients = get_ingredients(recipe_html)
    directions = get_directions(recipe_html)
    image = get_image(recipe_html)
    data = {"name" : name, "description" : description, "ingredients" : ingredients, "directions" : directions, "time" : cook_time, "rating" : rating, "image" : image}
    
    return(data)    

    #json_data = json.dumps(data)
   #print(json_data)





# Title
def get_recipe_name(html):
    for i, li in enumerate(html.find_all("h1", {"class":"recipe-summary__h1"})):
        return(li.text.strip()) #TODO get this in a better form


def get_description(html):
    description = ""
    for i, li in enumerate(html.find_all("div", {"class":"submitter__description"})):
        description = li.text.strip()
    return(description)

def get_ingredients(html):

    units = ["pinch","teaspoons ", "teaspoon ", "tablespoons ", "tablespoon ", "cups ", "cup ", "ounces", "ounce", "pounds ", "pound "]

    ingredients = []
    for i, li in enumerate(html.find_all('li', {"class":"checkList__line"})):
        unit_found = False

        ingredient_string = li.text.strip()
        whole_ingredient_string = li.text.strip()

        if ingredient_string != "Add all ingredients to list":
            for unit in units:
                if unit in ingredient_string:
                    ingredient_string = ingredient_string.split(unit)
                    unit_found = True
                    break
            if not unit_found:
                ingredient_string = ingredient_string.split(" ")
                if ingredient_string[0].isdigit(): 
                    unit = ""
                    quantity = ingredient_string[0]
                    ingredient = ingredient_string[1:]
                    ingredient = ' '.join(ingredient)
                else:
                    unit = ""
                    quantity = ""
                    ingredient = whole_ingredient_string
            else:
                quantity = ingredient_string[0]
                ingredient = ingredient_string[1]
            #ingredient_split_list = ingredient_string.split(" ")


            ingredients.append({ "ingredient" : ingredient, "unit" : unit, "quantity" : quantity})
    #del ingredients[-1]

    return(ingredients)



# Time return is in seconds
def get_time_info(html):
    total = 0
    # Need to split into seconds
    for i, li in enumerate(html.find_all('li', {"class":"prepTime__item"})):
        if "Ready In" in li.text.strip():
            time = li.text.strip()
            time = time.lower()


            time = time[8:]
            if "d" in time:
                days = time.split("d")[0]
                total = (int(days)* 8400)
            elif "h" in time and "m" in time:
                hours, mins = time.split("h ")
                mins = mins[:-1]
                total = (int(hours)*3600 + int(mins)*60)
            elif "h" in time and "m" not in time:
                hours = time.split("h")[0]
                total = (int(hours)*3600)

            else:
                mins = time.partition("m")[0]
                total = int(mins) * 60

    return total

# Directions
def get_directions(html):
    directions = []
    for i, li in enumerate(html.find_all('li', {"class":"step"})):
        if "Watch Now" in li.text.strip():
            directions.append(li.text.strip())
    return directions

# Ratinginfo


def get_rating(html):

    rating = html.find('meta', property="og:rating")
# this is randomly causing an error...
    if rating is not None:
        rating = round(float(rating["content"]), 1)
        return(rating)
    else:
        return(0.0)

def get_image(html):
    photo =""
    for i,li in enumerate(html.find_all('img', {"class" : "rec-photo"})):
        photo = li['src']

    return(photo)


# Photo (if we can get into database)
# <div class="hero-photo__wrap">
# some have a video as the main "picture"


# search_type = int(input("Search type: "))
# num_recipes = input("Number Recipes: ")

# if search_type == 1:  # Ingredients
#     search_input = input("Ingredients to search for: ")

# if search_type == 2: # Name
#     search_input = input("Search: ")

get_recipes()


