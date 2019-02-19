#!/usr/bin/env python3

import re
from mathmaticians import simple_get
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




# Might be silly to do
search_types = [("Category", 0), ("Ingredient", 1), ("Name",2)]


def get_name_search_html(query):
    '''
    This function grabs the search html for a recipe search based on name of meal

    :param query:
    :return:
    '''
    query_url = query.replace(" ", "%20")
    search_url = "https://www.allrecipes.com/search/results/?wt={}&sort=re".format(query_url)

    raw_search_html = simple_get(search_url)

    if raw_search_html:
        search_html = BeautifulSoup(raw_search_html, "html.parser")

        return search_html
    else:
        print ("failed")


# The ingredient query need to be separated by commas, which might be an issue in the future
def get_ingredient_search_html(query):
    '''
    this function grabs the search html for a recipe search based on ingredient input
    :param query:
    :return:
    '''
    query_url = query.replace(", ", ",")
    search_url = "https://www.allrecipes.com/search/results/?ingIncl={}&sort=re".format(query_url)

    raw_search_html = simple_get(search_url)

    if raw_search_html is not None:
        search_html = BeautifulSoup(raw_search_html, "html.parser")

        return search_html
    else:
        print("failed")


def get_recipes(search_type,num_recipes, query):
    """
    This function returns n recipes with all the data associated with them
    based on ingredient, word, or category search
    :param search_type, num_recipes, query:
    :return:
    """
    # Could make this into it's own function as well
    if search_type == 0:
        # search_html = get_category_search_html
        print("henlo")
    elif search_type == 1:
        search_html = get_ingredient_search_html(query)
    else:
        search_html = get_name_search_html(query)

    # This is where forks or threads would be great
    # nested findall searching for fixed-recipe-card and pulling url from a href
    for i, article in enumerate(search_html.find_all("article", {"class": "fixed-recipe-card"})):
        recipe_url = article.find("a")["href"]
        # call a recipe info function
        # place return into a database or what not
        get_recipe_info(recipe_url)
        if i == num_recipes-1:
            break


def get_recipe_info(url):
    raw_recipe_html = simple_get(url)
    recipe_html = BeautifulSoup(raw_recipe_html, "html.parser")
    get_recipe_name(recipe_html)
    get_rating(recipe_html)
    get_time_info(recipe_html)
    get_ingredients(recipe_html)
    get_directions(recipe_html)


# Category items : <meta itemprop="recipeCategory" ...>
#


# html = BeautifulSoup(raw_html, 'html.parser')

# for i, li in enumerate(html.find_all('li', {"class":"wprm-recipe-ingredient"})):
#     print(i, li.text)

# Title
def get_recipe_name(html):
    for i, li in enumerate(html.find_all("h1", {"class":"recipe-summary__h1"})):
        print(li.text.strip()) #TODO get this in a better form

# This gets ingredients but also includes the random add all ingredients line
# in the future we may want to split the quantity and the item

# For splitting the ingredients we should have the ounces multiplied by number
# the ounces seem to be denoted in parens
# measurements seem to be all fully written out not just abbreviated
# (ingredient, unit, amount)
def get_ingredients(html):
    ingredients = []
    for i, li in enumerate(html.find_all('li', {"class":"checkList__line"})):


        ingredients.append(li.text.strip())

    print(ingredients)

# for i, li in enumerate(html.find_a)

# Time info
# li class="prepTime__item" 3 of them usually
# They aria-labels which may or may not be an issue

# Time return is in seconds
def get_time_info(html):
    # Need to split into seconds
    for i, li in enumerate(html.find_all('li', {"class":"prepTime__item"})):
        if "Ready In" in li.text.strip():
            time = li.text.strip()

            time = time[8:]
            if "h" in time and "m" in time:
                hours, mins = time.split("h ")
                mins = mins[:-1]
                total = (int(hours)*3600 + int(mins)*60)
            elif "h" in time and "m" not in time:
                hours = time.split("h")
                print(hours)
                total = (int(hours)*3600)

            else:
                mins = time.partition("m")[0]
                total = int(mins) * 60
            print(total)



# Directions
def get_directions(html):
    directions = []
    for i, li in enumerate(html.find_all('li', {"class":"step"})):
        directions.append(li.text.strip())
    print(directions)

# Ratinginfo


def get_rating(html):

    rating = html.find('meta', property="og:rating")
# this is randomly causing an error...
    if rating is not None:
        rating = round(float(rating["content"]), 1)
        print(rating)
    else:
        print("Rating unavailable")


# Photo (if we can get into database)
# <div class="hero-photo__wrap">
# some have a video as the main "picture"


search_type = int(input("Search type: "))
num_recipes = input("Number Recipes: ")

if search_type == 1:  # Ingredients
    search_input = input("Ingredients to search for: ")

if search_type == 2: # Name
    search_input = input("Search: ")

get_recipes(search_type, int(num_recipes), search_input)


