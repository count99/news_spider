# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from apple_news.items import AppleNewsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class ApplenewsCrawler(CrawlSpider):
    name = 'apple_news'
    start_urls = ['http://tw.appledaily.com/new/realtime/']

    rules = (
        Rule(LinkExtractor(allow=('/new/realtime/[0-9]*$', )), callback='parse_page', follow=True),
    )

    def parse_page(self, response):
        for news in response.selector.css('.rtddt a::attr(href)').extract():
            yield scrapy.Request(news, self.parse_detail)

    def parse_detail(self, response):
        appleitem = AppleNewsItem()
        soup = BeautifulSoup(response.body, 'lxml')
        appleitem['title'] = response.selector.css(".ndArticle hgroup h1::text").extract()[0]
        if soup.select('.ndArticle_content p')[0].text != "":
            appleitem['content'] = soup.select('.ndArticle_content p')[0].text
        else:
            appleitem['content'] = soup.select('.ndArticle_content p')[1].text
        appleitem['time'] = response.selector.css('.ndArticle_creat::text').extract()[0].replace("出版時間：","")
        appleitem['view'] = response.selector.css('.ndArticle_view::text').extract()[0]
        appleitem['url'] = response.url
        return appleitem
