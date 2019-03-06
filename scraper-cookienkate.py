#!/usr/bin/env python3

import re
from scraperConnection import simple_get
from bs4 import BeautifulSoup





def get_recipe_pages():
    '''
    Will start from recipe index on cookie and kate page then scrape each recipe in the diet
    For now we're doing only vegan
    :param query:
    :return:
    '''
    url = "https://cookieandkate.com/vegan-recipe-index/"
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

    html = get_recipe_pages()

    # This is where forks or threads would be great
    # nested findall searching for fixed-recipe-card and pulling url from a href

    for i, article in enumerate(html.find_all("div", {"class":"lcp_catlist_item"})):
        url = article.find("a")["href"]
        #if "-recipe/" in url and i < 10: # might try and find a better way, we lose recipes this way
            #print(url)
        get_recipe_info(url)
            




def get_recipe_info(url):
    raw_recipe_html = simple_get(url)
    recipe_html = BeautifulSoup(raw_recipe_html, "html.parser")
# we should have error checking here

    get_recipe_description(recipe_html)
    name = get_recipe_name(recipe_html)
    print(name)
    rating = get_rating(recipe_html)
    print(rating)
    cook_time = get_time_info(recipe_html)
    print("{} seconds".format(cook_time))
    ingredients = get_ingredients(recipe_html)
    print(ingredients)
    directions = get_directions(recipe_html)
    print(directions)



# Title
def get_recipe_name(html):
    for i, li in enumerate(html.find_all("h1", {"class":"entry-title"})):
        return(li.text.strip()) #TODO get this in a better form


def get_recipe_description(html):
    for i, li in enumerate(html.find_all("div", {"class":"tasty-recipes-description"})):
        print(li.text.strip())

def get_ingredients(html):
    '''
    This function scrapes ingredients from a single recipe page on the Cookie and Kate site. 
    Params: html 
    Return: ingredients [(Quantity, Unit, Ingredient)]
    '''


    units = [" teaspoons ", " teaspoon ", " tablespoons ", " tablespoon ", " cups ", " cup ", " ounces ", " ounce ", " pounds ", " pound "]

    ingredients = []
    ingredient_string = None
    unit_found = False
    for i, div in enumerate(html.find_all('div', {"class":"tasty-recipe-ingredients"})):
        for li in div.find_all("li"):
            ingredient_string = li.text.strip()

            # We are going to split up the ingredient string by measurement first
            for unit in units:
                if unit in ingredient_string:
                    ingredient_string = ingredient_string.split(unit)
                    unit_found = True
                    break
            if not unit_found:
                # What's a better name to give this? Item? 
                unit = "Unit"
            
            quantity = ingredient_string[0]
            ingredient = ingredient_string[1]


            ingredients.append([quantity, unit, ingredient])
       #ingredients = ingredient_string.split()
    return(ingredients)





# Time return is in seconds
def get_time_info(html):
    # Need to split into seconds
    total = 0
    raw_time = html.find('span', {"class":"tasty-recipes-total-time"})
    if raw_time:
        time = raw_time.text.strip()
        print(time)

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
    else:
        return None

# Directions
def get_directions(html):
    directions = html.find('div',"tasty-recipe-instructions")
    if directions:

        directions = directions.text.strip()

        directions = directions.split('. ')
        return directions
    else:
        return None

# Ratinginfo


def get_rating(html):

    rating = html.find('span', {"class":"average"})
    if rating is not None:
        rating = rating.text.strip()
        return(rating)
    else:
        return(0.0)


# Photo (if we can get into database)
# <div class="hero-photo__wrap">
# some have a video as the main "picture"




get_recipes()
