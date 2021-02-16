import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from castletrust.items import Article


class CastleSpider(scrapy.Spider):
    name = 'castle'
    start_urls = ['https://www.castletrust.co.uk/group-news-about-us']

    def parse(self, response):
        articles = response.xpath('//ul[@class="sfpostsList sfpostListTitleDateSummary sflist u--m-"]/li')
        for article in articles:
            date = article.xpath('.//div[@class="sfdate u-ph- u-pt-- u-pb-"]//text()').get().split()[0]
            link = article.xpath('.//a[@class="sfpostFullStory sffullstory u-ph-- u-pb--"]/@href').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = datetime.strptime(date.strip(), '%d/%m/%Y')
        date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="sfpostContent sfcontent"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
