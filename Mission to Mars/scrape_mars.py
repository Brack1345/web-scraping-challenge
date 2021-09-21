from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import pymongo

#DB Setup

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars

def init_browser():
    executable_path = {"executable_path": "../chromedriver"}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()
    collection.drop()

    #Nasa Mars News
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = BeautifulSoup(news_html, 'html.parser')
    news_title = news_soup.find("div",class_="content_title").text
    news_para = news_soup.find("div", class_="rollover_description_inner").text

    #Featured Image
    image_home_url = 'https://spaceimages-mars.com/'
    browser.visit(image_home_url)
    image_html = browser.html
    image_soup = BeautifulSoup(image_html, 'html.parser')
    image_url = image_soup.find('a',class_='showimg fancybox-thumbs')['href']
    featured_image_url = image_home_url + image_url

    #Mars Facts
    mars_url = 'https://galaxyfacts-mars.com/'
    facts_table = pd.read_html(mars_url)
    facts_df = facts_table[0]
    facts_df

    #Mars Hemisphers
    hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemi_url)
    hemi_html = browser.html
    hemi_soup = BeautifulSoup(hemi_html, 'html.parser')
    results = hemi_soup.find_all("div",class_='item')
    hemisphere_image_urls = []
    for result in results:
        product_dict = {}
        titles = result.find('h3').text
        end_link = result.find("a")["href"]
        image_link = "https://astrogeology.usgs.gov/" + end_link    
        browser.visit(image_link)
        html = browser.html
        soup= BeautifulSoup(html, "html.parser")
        downloads = soup.find("div", class_="downloads")
        image_url = downloads.find("a")["href"]
        print(titles)
        print(image_url)
        product_dict['title']= titles
        product_dict['image_url']= image_url
        hemisphere_image_urls.append(product_dict)

    #Close Browser
    browser.quit()

    #Return Results
    mars_data = {'news_title': news_title,
                'summary': news_para,
                'featured_image': featured_image_url,
                'fact_table': facts_df,
                'hemisphere_image_url': hemisphere_image_urls,
                'news_url': news_url,
                'facts_url': mars_url,
                'hemisphere_url': hemi_url}
    collection.insert(mars_data)


