import scrapy
from bs4 import BeautifulSoup
from textblob import TextBlob
import random

class PoemSpider(scrapy.Spider):
    name = "poems"
    counter = 0
    visited_links = []

    def __init__(self, search=''):
        self.start_urls = ["https://www.poetryfoundation.org/search?query=%s" % search]

    def start_requests(self):
        for url in self.start_urls:
             yield scrapy.Request(url=url, callback=self.parse, meta={'nouns': []})

    def validate(self, response):
        print("QUERY")
        links = response.css("ul.c-vList")[0].css("li") 
        link = links[0].css("a::attr(href)").get()
        if link in visited_links and len(links) > 1:
            link = links[1].css("a::attr(href)").get()
        
        yield link

    def parse(self, response):
        links = response.css("ul.c-vList") 
        if len(links) > 0:
            link = links[0].css("li")[0].css("a::attr(href)").get()
            if self.counter == 0:
                link = links[0].css("li")[0].css("a::attr(href)").get()
            print("link", link)
            if link is not None and link not in self.visited_links:
                self.visited_links.append(link)
                yield scrapy.Request(url=link, callback=self.parsePoems)
        nouns = response.meta.get('nouns')
        print(nouns, response.meta.get('search'))
        nouns.remove(response.meta.get('search'))
        search = random.choice(nouns)
        new_search = search.replace(" ", "%20")
        search_url = 'https://www.poetryfoundation.org/search?query=%s&refinement=poems' % new_search
        yield scrapy.Request(url=search_url, callback=self.parse, meta={'nouns': nouns, 'search': search})

    def parsePoems(self, response):
        page = response.url.split("/")[-2]
        filename = 'poems-%s.txt' % page
        poem = response.css("div.o-poem").get()
        soup = BeautifulSoup(poem, 'html.parser').getText(separator=u' ').encode('utf-8')
        blob = TextBlob(soup.decode('utf-8'))
        nouns = blob.noun_phrases
        with open(filename, 'w', encoding="utf-8") as f:
            #f.write(soup.decode('utf-8'))
            #f.write('\n')
            f.write(str(nouns))
            #f.write(nouns)
        self.log('Saved file %s' % filename)
        self.counter += 1
        if self.counter < 0:
            search = random.choice(nouns)
            new_search = search.replace(" ", "%20")
            print("NEW SEARCH", new_search)
            search_url = 'https://www.poetryfoundation.org/search?query=%s&refinement=poems' % new_search
            print("SEARCH", search_url)

            print("COUNTER", self.counter)
            yield scrapy.Request(url=search_url, callback=self.parse, meta={'nouns': nouns, 'search': search})

