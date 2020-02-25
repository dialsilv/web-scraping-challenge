import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
from splinter import Browser
import time


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():

    # 01 - Get most recent news and paragraph from mars.nasa.gov
    browser = init_browser()

    # get url connection
    url_mars_nasa = 'https://mars.nasa.gov/news/'
    browser.visit(url_mars_nasa)

    time.sleep(5)

    # scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')  

    # find all content titles and the most recent one on page
    title_block = soup.find_all('div', class_='content_title')
    news_title = title_block[0].find('a').get_text()

    # find all paragraphs and the most recent one on the page
    paragraph_block = soup.find_all('div', class_='article_teaser_body')
    news_p = paragraph_block[0].get_text()
    browser.quit()

    # 02 - Get image url from www.jpl.nasa.gov
    browser = init_browser()

    # get url connection
    url_jpl_nasa_route = 'https://www.jpl.nasa.gov'
    url_jpl_nasa_mars = '/spaceimages/?search=&category=Mars'
    browser.visit(url_jpl_nasa_route + url_jpl_nasa_mars)

    time.sleep(5)

    # scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')  

    # find part of image in html and get the url
    image_block = soup.find('div', class_='carousel_items')
    featured_image_url= url_jpl_nasa_route + image_block.article['style'].split("url('")[1].split("')")[0]
    browser.quit()

    # 03 - Get last tweet with the last weather information
    browser = init_browser()

    # get url connection
    url_twitter = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url_twitter)

    time.sleep(5)

    # scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')  

    # find all tweets and the most recent one on page
    weather_block = soup.find_all('div', class_='css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0')
    mars_weather = weather_block[0].find('span', class_='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0').text
    mars_weather = mars_weather.replace('\n', ' ')
    browser.quit()

    # 04 - Get table with mars information from space-facts.com/mars/
    # get url connection
    url_mars_facts = 'https://space-facts.com/mars/'

    # look for all the tables in the url and get the first one
    tables = pd.read_html(url_mars_facts)
    table_facts_mars = tables[0]
    table_facts_mars.columns = ['description', 'value']
    table_facts_mars = table_facts_mars.set_index('description')

    # Convert table into html
    table_facts_mars_html = table_facts_mars.to_html()

    # 05 - Get hemisphere images of mars from astrogeology.usgs.gov
    browser = init_browser()

    # get url connection
    url_hemispheres_route = 'https://astrogeology.usgs.gov'
    url_hemispheres_mars = '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url_hemispheres_route + url_hemispheres_mars)

    time.sleep(5)

    # scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')  

    # Retrieve the parent divs for all articles
    results = soup.find_all('div', class_='item')

    hemisphere_image_urls = []

    # loop over results to get title and picture url
    for result in results:
        
        # scrape the title of the hemisphere 
        title = result.find('h3').text 

        # click the title of the hemisphere to get the full size image 
        browser.click_link_by_partial_text(title)

        # parse the new page to get the url of the image 
        time.sleep(5)

        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')

        block_image = soup.find_all('img', class_='wide-image')
        image_url = block_image[0]['src']
        
        # add results into a dictionary
        dict_result = {"title": title.split(" Enhanced")[0], "img_url": url_hemispheres_route + image_url }
        
        # append the current dictionary to the list
        hemisphere_image_urls.append(dict_result)
        
        browser.back()

    browser.quit()

    # Store all data in a dictionary
    scraped_data = {
        "news_title": news_title,
        "news_p": news_p,
        "image_url": featured_image_url,
        "mars_weather": mars_weather,
        "table_facts_mars": table_facts_mars_html,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return scraped_data
