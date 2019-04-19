#!/usr/bin/env python3

import json

from pymongo import MongoClient
from scraperConnection import simple_get
from bs4 import BeautifulSoup


def get_html(page):
    '''
    This function grabs the search html for a recipe search based on name of meal

    :param query:
    :return:
    '''
    #query_url = query.replace(" ", "%20")
 
    search_url = "https://www.epicurious.com/search?content=recipe&page={}&sort=highestRated".format(page)

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
        
    recipes = []
    #for page in range(1, 1994):
    for page in range(1, 3):
        search_html = get_html(page)


        # This is where forks or threads would be great
        # nested findall searching for fixed-recipe-card and pulling url from a href
        for i, article in enumerate(search_html.find_all("article", {"class": "recipe-content-card"})):
            recipe_url = article.find("a")["href"]
            # call a recipe info function
            # place return into a database or what not

            data_to_insert = get_recipe_info("https://www.epicurious.com{}".format(recipe_url))
            #collection.insert_one(data_to_insert)
            #get_recipe_info(recipe_url)
            recipes.append(data_to_insert)
        
       # print("Page: {} visited".format(page))
    print(json.dumps(recipes))



def get_recipe_info(url):
    raw_recipe_html = simple_get(url)
    recipe_html = BeautifulSoup(raw_recipe_html, "html.parser")


    name = get_recipe_name(recipe_html)
    description = get_description(recipe_html)
    rating = get_rating(recipe_html)
    ingredients = get_ingredients(recipe_html)
    directions = get_directions(recipe_html)
    image = get_image(recipe_html)
    data = {"name" : name, "description" : description, "ingredients" : ingredients, "directions" : directions, "rating" : rating, "image" : image}
    
    return(data)    

    #json_data = json.dumps(data)
   #print(json_data)


def get_recipe_name(html):
    #h1 itemprop = "name"

    name = html.find("h1", {"itemprop" : "name"}).text.strip()
    return(name)

def get_rating(html):
    rating = html.find("span", {"class" : "rating"})
    rating = rating.text.strip()
    return(rating)

def get_description(html):
    desc = html.find("div", {"itemprop" : "description"}).find('p').text.strip()
    return(desc)

def get_ingredients(html):
    '''
    good practice :)
    '''
    units = ["pinch", "pint", "pints" ,"tsp.", "teaspoons", "teaspoon", "Tbsp. ", "tablespoons", "tablespoon", "cups ", "cup ", "ounces", "ounce", "pounds ", "pound "]


    # for ingredient groups look for strong tag else default will be ingredients
    ingredient_groups = html.find_all("li", {"class" : "ingredient-group"})

    # continue search for ingredients on default group case
    ingredients = {}
    for group in ingredient_groups:

        # continue search for ingredients on default group case

        group_name = None

        try:
            # more than one group
            group_name = group.find("strong").text.strip()
        except Exception as e:
            group_name = "Ingredients"

        group_ingredients = []
        for i, li in enumerate(group.find_all('li', {"class":"ingredient"})):
            unit_found = False

            ingredient_string = li.text.strip()

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
                    ingredient = ' '.join(ingredient_string)
            else:
                quantity = ingredient_string[0]
                ingredient = ingredient_string[1]


            group_ingredients.append({"ingredient" : ingredient, "quantity" : quantity, "unit" : unit})
        
        ingredients[group_name] = group_ingredients
    return(ingredients)


        


def get_directions(html):
    directions = []
    for i, li in enumerate(html.find_all("li", {"class": "preparation-step"})):
        step = li.text.strip()
        directions.append(step)
    return(directions)


def get_image(html):
    image = html.find("div", {"class" : "recipe-image"}).find('source')['srcset']
    return(image)


# Main here but I'm lazy
get_recipes()