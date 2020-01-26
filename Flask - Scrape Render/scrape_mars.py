from bs4 import BeautifulSoup
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from selenium import webdriver
import time
import requests
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    mars = {}

    #-----------------------------------------------------------------------
    #Part 1: NASA Mars News
    url_news = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'

    browser_sele = webdriver.Chrome()
    browser_sele.get(url_news)
    soup_selenium = BeautifulSoup(browser_sele.page_source, "html.parser")

    mars["news_title"] = soup_selenium.find('div', class_="content_title").text.strip()
    time.sleep(2)
    mars["news_p"] = soup_selenium.find('div', class_="article_teaser_body").text.strip()

    print("---------------------------------------------------------------------------------------")
    print("Part 1: NASA Mars News Complete! Next: Part 3: Mars Weather ")

    browser_sele.quit()

    #-----------------------------------------------------------------------
    #Part 3: Mars Weather
    url_twit = 'https://twitter.com/marswxreport?lang=en'
    response_tw = requests.get(url_twit)
    soup_tw = BeautifulSoup(response_tw.text, 'html.parser')
    last_twit = (soup_tw.find('div', class_="js-tweet-text-container")).find('p')
    split = last_twit.get_text().split(last_twit.find('a').text.strip()) 
    mars["mars_weather"] = split[0].replace('\n', ', ')
    print("---------------------------------------------------------------------------------------")
    print("Part 3: Mars Weather Complete! Next: Part 4: Mars Facts")
    
    #-----------------------------------------------------------------------
    #Part 4: Mars Facts
    url_facts = 'https://space-facts.com/mars/'
    tables = pd.read_html(url_facts)
    df = tables[0]
    df.columns = ['Description', 'Value']
    df.set_index('Description', inplace=True)
    html_table = df.to_html()
    html_table.replace('\n', '')
    mars["mars_facts"]= html_table
    print("---------------------------------------------------------------------------------------")
    print("Part 4: Mars Facts Complete! Next: Part 2: JPL Mars Space Images - Featured Image")

    #-----------------------------------------------------------------------
    #Part 2: JPL Mars Space Images - Featured Image

    browser = init_browser()
    url_pic = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_pic)

    browser.links.find_by_partial_text('FULL IMAGE')
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(3)

    html = browser.html
    soup_pic = BeautifulSoup(html, 'html.parser')

    featured_image_url = "http://www.jpl.nasa.gov" + soup_pic.find('img', class_='fancybox-image')['src']
    mars["featured_image_url"] = featured_image_url
    print("---------------------------------------------------------------------------------------")
    print("Part 2: JPL Mars Space Images - Featured Image Complete! Next: Part 5: Mars Hemispheres")

    #-----------------------------------------------------------------------
    #Part 5 Mars Hemispheres
    url_hemisphere = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url_hemisphere)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    print("---------------------------------------------------------------------------------------")
    print("Compiling Hemisphere List")

    results_hemisphere = soup.find('div', class_='full-content')
    titles_hemisphere = results_hemisphere.find_all('h3')

    title_list = []
    for title in titles_hemisphere:
        clean_title = str.strip(title.text)
        title_list.append(clean_title)
       
    print("Hemisphere List Complete! Next: Scraping Hemisphere Pic Url")
       
    hemisphere_image_urls = []
    for x in range(len(title_list)):
        
        try:
            url_hemisphere = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
            browser.visit(url_hemisphere)
            time.sleep(1)
            
            browser.links.find_by_partial_text(title_list[x])
            browser.click_link_by_partial_text(title_list[x])
                    
            html = browser.html
            soup_pic = BeautifulSoup(html, 'html.parser')
            
            eachpic_hemisphere = soup_pic.find('div', class_='downloads')
            eachpic_link = eachpic_hemisphere.find('a')['href']
            
            pics_dict = {}
            pics_dict["title"] = title_list[x]
            pics_dict["img_url"] = eachpic_link
            hemisphere_image_urls.append(pics_dict)
            
            time.sleep(2)
            
        except ElementDoesNotExist:
            print("Scraping Complete")

    mars["hemisphere_image_urls"] = hemisphere_image_urls    
    print("Part 5: Mars Hemispheres Complete! Next: Compiling into one dictionary")
    browser.quit()

    #-----------------------------------------------------------------------
    print("---------------------------------------------------------------------------------------")
    print("Complete Mars Data")
    print(mars)
    return mars
