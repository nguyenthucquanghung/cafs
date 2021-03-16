import scrapy

BAOMOI_BASE_URL = 'https://baomoi.com'
detecting_keywords = ['covid-19', 'corona', 'sars-cov-2']


class LegitTimelineNewsSpider(scrapy.Spider):
    name = 'legit_timeline_news'
    start_urls = ['https://ncov.moh.gov.vn/web/guest/dong-thoi-gian']

    def parse(self, response):
        for timeline_new in response.css('div.timeline-detail'):
            yield {
                'time_tag': timeline_new.css('h3::text').get(),
                'content': '\n'.join(timeline_new.css('p::text').getall())
            }

        next_page = response.xpath("//a[contains(@href, 'https://ncov.moh.gov.vn/web/guest/dong')]")[-1].attrib['href']

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


class LegitNewsSpider(scrapy.Spider):
    name = 'legit_news'
    start_urls = ['https://ncov.moh.gov.vn/vi/web/guest/tin-tuc']

    def parse(self, response):
        for legit_new in response.xpath(
                "//div[@class='portlet-body']//a[contains(@href, 'https://ncov.moh.gov.vn/vi/web/guest/-/')]"):
            try:
                yield {
                    'title': legit_new.xpath('text()').get(),
                    'link': legit_new.attrib['href']
                }
            except:
                yield {
                    'title': legit_new.css('h2.mt-3::text').get(),
                    'link': legit_new.attrib['href']
                }
        next_page = response.xpath("//a[contains(@href, 'https://ncov.moh.gov.vn/vi/web/guest/tin')]")[-1].attrib[
            'href']

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


class BaomoiTimelineNewsSpider(scrapy.Spider):
    name = 'baomoi_timeline_news'
    start_urls = 'https://baomoi.com/cac-ca-nhiem-sars-cov-2-o-ha-noi/t/18644984.epi'
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls,
            headers=self.headers,
            callback=self.parse_cards
        )

    def parse_cards(self, response):
        for card in response.css('div[class="story"]'):
            features = {
                'title': card.xpath('h4/a//text()').get(),
                'source': card.css('a[class="source"]').attrib['href'].split('/')[1],
                'published_date': card.css('time').attrib['datetime'],
                'article_link': BAOMOI_BASE_URL + card.css('a[class="cache"]').attrib['href'],
                'article_content': ''
            }

            yield response.follow(
                url=features['article_link'],
                headers=self.headers,
                meta={
                    'article': features
                },
                callback=self.parse_article
            )

        next_page_url = BAOMOI_BASE_URL + response.css('a[class="btn btn-sm btn-primary"]').attrib['href']
        if next_page_url is not None:
            yield response.follow(
                url=next_page_url,
                headers=self.headers,
                callback=self.parse_cards
            )

    def parse_article(self, response):
        article = response.meta.get('article')
        article['article_content'] = '\n'.join(response.css('div[class="article__body"] *::text').getall())

        yield article


class BaomoiNewsSpider(scrapy.Spider):
    name = 'uncertain_news'
    start_urls = 'https://baomoi.com/phong-chong-dich-covid-19/top/328.epi'
    # start_urls = 'https://baomoi.com/suc-khoe-y-te.epi'
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls,
            headers=self.headers,
            callback=self.parse_cards
        )

    def parse_cards(self, response):
        for card in response.css('div[class="story"]'):
            features = {
                'title': card.xpath('h4/a//text()').get(),
                'source': card.css('a[class="source"]').attrib['href'].split('/')[1],
                'published_date': card.css('time').attrib['datetime'],
                'article_link': BAOMOI_BASE_URL + card.css('a[class="cache"]').attrib['href'],
                'article_content': ''
            }
            yield response.follow(
                url=features['article_link'],
                headers=self.headers,
                meta={
                    'article': features
                },
                callback=self.parse_article
            )
            # for keyword in detecting_keywords:
            #     if keyword in features['title'].lower():
            #         yield response.follow (
            #             url=features['article_link'],
            #             headers=self.headers,
            #             meta={
            #                 'article': features
            #             },
            #             callback=self.parse_article
            #         )
            #         break
        next_page_url = BAOMOI_BASE_URL + response.css('a[class="btn btn-sm btn-primary"]').attrib['href']
        if next_page_url is not None:
            yield response.follow(
                url=next_page_url,
                headers=self.headers,
                callback=self.parse_cards
            )

    def parse_article(self, response):
        article = response.meta.get('article')
        article['article_content'] = '\n'.join(response.css('div[class="article__body"] *::text').getall())

        yield article
