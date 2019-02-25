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
        if "-recipe/" in url and i < 1: # might try and find a better way, we lose recipes this way
            print(url)
            get_recipe_info(url)
            




def get_recipe_info(url):
    raw_recipe_html = simple_get(url)
    recipe_html = BeautifulSoup(raw_recipe_html, "html.parser")


    get_recipe_description(recipe_html)
    name = get_recipe_name(recipe_html)
    print(name)
    # rating = get_rating(recipe_html)
    cook_time = get_time_info(recipe_html)
    print(cook_time)
    ingredients = get_ingredients(recipe_html)
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


    units = ["teaspoons ", "teaspoon ", "tablespoons ", "tablespoon ", "cups ", "cup ", "ounces ", "ounce ", "pounds ", "pound "]
    #units = ["teaspoon", "tablespoon", "cup", "ounce","pound"]

    ingredients = []
    #for i, li in enumerate(html.find_all('li', {"class":"tasty-recipe-ingredients"})):
    for i, li in enumerate(html.find_all('li', {"class":"tasty-recipe-ingredients"})):

        ingredient_string = li.text.strip()
        ingredients.append(ingredient_string)

        print(ingredient_string)

    #     ingredient_split_list = []
    #     for unit in units:
    #         if unit in ingredient_string:
    #             ingredient_string = ingredient_string.replace(unit, "")
    #             break
    #         unit = None
    #     #ingredient_split_list = ingredient_string.split(" ")

    #     ingredient_split_list = re.sub('[()]', '', ingredient_string).split(" ")

    #     print(ingredient_split_list)

    #     for elem in ingredient_split_list:
    #         if "/" in elem:
    #             ingredient_split_list[ingredient_split_list.index(elem)] = float(elem[0])/float(elem[2])


    #     if unit == " ounce" or unit == " ounces":
    #         quantity = float(ingredient_split_list[0])*float(ingredient_split_list[1])

    #         del ingredient_split_list[0]
    #         del ingredient_split_list[0]
    #         ingredient = " ".join(ingredient_split_list)
    #     else:
    #         quantity = float(ingredient_split_list[0])
    #         del ingredient_split_list[0]

    #         ingredient = " ".join(ingredient_split_list)

    #     ingredients.append([ingredient, unit, quantity])

    #     # print("QUANTITY: ", quantity)
    #     # print("UNIT: ", unit)
    #     # print("INGREDIENT: ", ingredient)
    # return(ingredients)   




# for i, li in enumerate(html.find_a)

# Time info
# li class="prepTime__item" 3 of them usually
# They aria-labels which may or may not be an issue

# Time return is in seconds
def get_time_info(html):
    # Need to split into seconds
    total = 0
    raw_time = html.find('span', {"class":"tasty-recipes-total-time"})
    time = raw_time.text.strip()

    if "hours" in time and "minutes" in time:
        hours, mins = time.split("hours ")
        mins = mins[:-1]
        total = (int(hours)*3600 + int(mins)*60)
    elif "hours" in time and "minutes" not in time:
        hours = time.split("hours")
        total = (int(hours)*3600)

    else:
        mins = time.partition("m")[0]
        total = int(mins) * 60

    return total

# Directions
def get_directions(html):
    directions = []
    for i, li in enumerate(html.find_all('div',"tasty-recipe-instructions")):
    #print(html.find_all('li', {"class":"tasty-recipe-instructions"}))
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


# Photo (if we can get into database)
# <div class="hero-photo__wrap">
# some have a video as the main "picture"




get_recipes()


