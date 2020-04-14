import scrapy
from asos_scraper.items import EcommerceScraperItem
from scrapy.http import Request
import os
import re
import urllib
import hashlib
#to read from a csv file
import csv

class AsosEcommerceSpider(scrapy.Spider):
    name = 'asos_ecommerce'

    def __init__(self, *args, **kwargs):                    
        super(AsosEcommerceSpider, self).__init__(*args, **kwargs)

        with open(os.path.abspath("../csv_files/asos.csv"), "rU") as f:
            reader = csv.DictReader(f)
            metas = [row for row in reader]
            self._metas = metas

    def start_requests(self):
        request_list = []
        tup_list = []                                                   
        for idx, meta in enumerate(self._metas):                                              
            request_list.append(scrapy.Request(url = meta['url'], meta = {'gender': meta['gender'], 'category': meta['category']}, callback = self.parse, dont_filter=True))
            tup_list.append((meta['url'], meta['gender'], meta['category']))
        print('*'*80)
        print(f'Number of requests is {len(request_list)}')
        print('*'*80)
        return request_list 

    def parse(self, response):
        print(f"STARTING URL: {response.request.url}")
        gender = response.meta['gender']
        category = response.meta['category']
        text = response.xpath('//p[@class="XmcWz6U"]/text()').extract()[0]
        print(text)

        try:
            per_page, total = map(lambda x: int(x), re.findall('\d+', text))
            num_pages = round(total/per_page)
        except:
            print("Trying the 3 way format")
            per_page, total1, total2 = map(lambda x: int(x), re.findall('\d+', text))
            num_pages = round((total1*1000+total2)/per_page)

        link_urls = [response.request.url + '&page={}'.format(i) for i in range(1,num_pages)]
        for link_url in link_urls:
            print(f"DOING URL {link_url}")
            request = Request(link_url, meta = {'gender': gender,'category': category}, callback=self.parse_result_page)
            yield request

    def parse_result_page(self, response):
        products = response.xpath('//article[@class="_2qG85dG"]')  
        gender = response.meta['gender']
        category = response.meta['category']
        print(f'Number of products is {len(products)}')
        for product in products:
            detail_url = product.xpath('.//@href').extract_first()  # We are looking for url of the detail page.
            price = product.xpath('.//p/span[2]/text()').extract_first()
            yield Request(url=detail_url, meta={'price': price, 'product_link': detail_url, 'gender': gender, 'category': category}, callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        product_id = response.xpath('//div[@class="product-code"]/p/text()').extract_first()
        product_name = response.xpath('//div[@class="product-hero"]/h1/text()').extract_first()

        product_details = response.xpath('//div[@class="product-description"]/ul/li/text()').extract()
        additional_details = response.xpath('//div[@class="about-me"]/text()').extract()

        image_urls = []
        image_urls = [image.replace('$S$','$XXL$').replace('wid=40','wid=513') for image in response.xpath('//*/img/@src').extract() if 'product' in image]
        
        # Save results
        item = EcommerceScraperItem()

        item['product_id'] = product_id

        item['product_name'] = product_name
        item['category'] = response.meta['category']
        item['gender'] = response.meta['gender']
        item['price'] = response.meta['price']
        item['brand'] = None

        item['product_details'] = product_details
        item['additional_details'] = additional_details

        item['product_link'] = response.meta['product_link']
        item['source'] = "ASOS"
        item['image_urls'] = image_urls

        yield item