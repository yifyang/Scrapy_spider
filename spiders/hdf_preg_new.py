# -*- coding: utf-8 -*-
import scrapy
import csv
from bs4 import BeautifulSoup

class PediatricSpider(scrapy.Spider):
    name = "hdf_preg"
    count = 0

    def start_requests(self):
        urls = {
            '科室列表': 'http://www.haodf.com/keshi/list.htm',
        }
        for (level_0_tag, url) in urls.items():
            request = scrapy.Request(url=url, callback=self.parse_pediatric_level_2_tags)
            print (level_0_tag)
            yield request

    def parse_pediatric_level_2_tags(self, response):
        for anchor in response.xpath('//*[@id="el_result_content"]/div/div[3]/div/div[26]/ul/li'):
            next_url = 'http://www.haodf.com' + anchor.xpath ('a/@href').extract_first ()
            request = scrapy.Request (next_url, callback=self.parse_pediatric_level_3_tags)
            request.meta['level_2_tag'] = anchor.xpath ('a/text()').extract_first ()
            request.meta['level_1_tag'] = "皮肤美容"
            yield request

    def parse_pediatric_level_3_tags(self, response):
        anchor = response.xpath ('//table[@class="hzdp"]')[0]
        request = scrapy.Request (anchor.xpath ('tr/td[@align="right"]/a/@href').extract_first (),
                                  callback=self.parse_pediatric_level_4_tags)
        request.meta['level_2_tag'] = response.meta['level_2_tag']
        request.meta['level_1_tag'] = response.meta['level_1_tag']
        yield request

    def parse_pediatric_level_4_tags(self, response):
        for anchor in response.xpath('//table[@class="hplb blueg"]/tr'):
            if len(anchor.xpath('td')) != 2:
                continue
            else:
                request = scrapy.Request(anchor.xpath('td[1]/a[1]/@href').extract_first(),
                                         callback=self.parse_pediatric_descript_tags)
                request.meta['level_3_tag'] = anchor.xpath('td[1]/a[2]/text()').extract_first()
                request.meta['level_4_tag'] = anchor.xpath('td[1]/a[1]/@title').extract_first()
                request.meta['level_2_tag'] = response.meta['level_2_tag']
                request.meta['level_1_tag'] = response.meta['level_1_tag']
                yield request


        next_page = self.find_next_page_anchor_on_level_4_page(response.xpath('//div[@class="p_bar"]/a'))
        if next_page is not None:
            url = 'http://www.haodf.com' + next_page.css('::attr(href)').extract_first()
            request = scrapy.Request(url, callback=self.parse_pediatric_level_4_tags)
            request.meta['level_2_tag'] = response.meta['level_2_tag']
            request.meta['level_1_tag'] = response.meta['level_1_tag']
            yield request

    def parse_pediatric_descript_tags(self, response):
        disease = response.xpath('//div[@class="h_s_info_cons"]/h2[1]/a/text()').extract_first()
        disease_discript = response.xpath('//div[@class="h_s_info_cons"]/div[1]/text()[3]').extract_first()
        if disease_discript is not None:
            disease_discript = disease_discript.replace('\r', '')
            disease_discript = disease_discript.replace('\n', '')
            disease_discript = disease_discript.replace('\u3000', '')
            disease_discript = disease_discript.replace('\n', '')
            disease_discript = disease_discript.replace(' ', '')
            disease_discript = disease_discript.replace('"', '')
        else:
            disease_discript = ''
        with open('result_skin.csv', 'a', newline='', encoding='utf8') as txtfile:
            if response.meta['level_1_tag'] is None:
                response.meta['level_1_tag'] = ''
            if response.meta['level_2_tag'] is None:
                response.meta['level_2_tag'] = ''
            if response.meta['level_3_tag'] is None:
                response.meta['level_3_tag'] = ''
            else:
                response.meta['level_3_tag'] = response.meta['level_3_tag'].replace('\n', '')
                response.meta['level_3_tag'] = response.meta['level_3_tag'].replace('\r', '')
            if response.meta['level_4_tag'] is None:
                response.meta['level_4_tag'] = ''
            else:
                response.meta['level_4_tag'] = response.meta['level_4_tag'].replace('\n', '')
                response.meta['level_4_tag'] = response.meta['level_4_tag'].replace('\r', '')
            if disease is None:
                disease = ''
            else:
                disease = disease.replace('\n', '')
                disease = disease.replace('\r', '')
            line = "%s\t%s\t%s\t%s\t%s\t%s\n" % (
            response.meta['level_1_tag'], response.meta['level_2_tag'], response.meta['level_3_tag'],
            response.meta['level_4_tag'], disease, disease_discript)
            txtfile.write(line)


    def find_next_page_anchor_on_level_4_page(self, anchors):
        for anchor in anchors:
            if anchor.xpath('text()').extract_first() == '下一页':
                return anchor
        return None
