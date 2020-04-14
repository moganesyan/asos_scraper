# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class EcommerceScraperItem(Item):
    # define the fields for your item here like:
    product_id = Field()

    product_name = Field()
    category = Field()
    gender = Field()
    price = Field()
    brand = Field()

    product_details = Field()
    additional_details = Field()

    product_link = Field()
    source = Field()
    image_urls = Field()
    images = Field()
