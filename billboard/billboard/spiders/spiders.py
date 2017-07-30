import scrapy


class Top10Spider(scrapy.Spider):
    name = "top10"
    top10list = {}

    def start_requests(self):
        urls = [
            "http://www.billboard.com/charts/hot-100"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        list = response.css('#main > div:nth-child(2) > div.chart-data')
        date = list.css('::attr(data-chartdate)').extract_first()
        self.top10list[date] = {}
	for item in list.css('div > article.chart-row'):
            container = item.css('div.chart-row__primary > div.chart-row__main-display > div.chart-row__container > div.chart-row__title')
            song = container.css('h2::text').extract_first()
            artist = container.css('a::text').re(r'.+?(?= Featuring|\n)')
            if artist:
                artist = artist[0]
            position = item.css('div.chart-row__primary > div.chart-row__main-display > div.chart-row__rank > span.chart-row__current-week::text').extract_first()
            last_week_position = item.css('div.chart-row__secondary > div > div.chart-row__last-week > span.chart-row__value::text').extract_first()
            self.top10list[date][position] = {"artist": artist, "song": song, "position": position, "last_week_position": last_week_position}
            if position and int(position) >= 10:
                break
        print self.top10list


class Last50WeeksSpider(Top10Spider):
    name = "last50weeks"
    week = 0

    def parse(self, response):
        super(Last50WeeksSpider, self).parse(response)

        next_page = response.css('#chart-nav > a:nth-child(1)::attr(href)').extract_first()
        if next_page is not None and self.week < 50:
            self.week += 1
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
