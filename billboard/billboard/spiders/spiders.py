import redis
import scrapy


class Top10Spider(scrapy.Spider):
    name = "top10"
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    def start_requests(self):
        urls = [
            "http://www.billboard.com/charts/hot-100"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        list = response.css('#main > div:nth-child(2) > div.chart-data')
        date = list.css('::attr(data-chartdate)').extract_first()
	for item in list.css('div > article.chart-row'):
            container = item.css('div.chart-row__primary > div.chart-row__main-display > div.chart-row__container > div.chart-row__title')
            song = container.css('h2::text').extract_first()
            artist = container.css('a::text').re(r'.+?(?= Featuring|\n)')
            if artist:
                artist = artist[0]
                position = item.css('div.chart-row__primary > div.chart-row__main-display > div.chart-row__rank > span.chart-row__current-week::text').extract_first()
                last_week_position = item.css('div.chart-row__secondary > div > div.chart-row__last-week > span.chart-row__value::text').extract_first()
           
                #stop parsing after position 10
                if position and int(position) > 10:
                    break
           
                if int(position) == 1:
                    #in case user has never been in first place
                    if not self.r.zscore('weeksInFirstPlace', artist):
                        self.r.zadd('weeksInFirstPlace', 0, artist)
                        self.r.zadd('weeksInFirstPlace', 0, artist + ';lastGreatestRun')
                    #if his last week position was not first save in another variable and set score to zero                   
                    elif last_week_position and int(last_week_position) != 1:
                        import pudb; pu.db
                        if self.r.zscore('weeksInFirstPlace', artist + ';lastGreatestRun') <= self.r.zscore('weeksInFirstPlace', artist):
                            self.r.zadd('weeksInFirstPlace', int(self.r.zscore('weeksInFirstPlace', artist)) + 1, artist + ';lastGreatestRun')
                        self.r.zadd('weeksInFirstPlace', -1, artist)
                    self.r.zincrby('weeksInFirstPlace', artist, 1)
          
                #verify if user does not have a score yet, it means it is the first time in the top ten list
                if not self.r.zscore('weeksOnTop10', artist):
                    self.r.zadd('weeksOnTop10', 0, artist)
           
                #verify if user does not have been set for this week already, to prevent counting artist for being twice in the top ten at the same week
                if not self.r.get(artist + date):
                    self.r.set(artist + date, 1)
                    self.r.zincrby('weeksOnTop10', artist, 1)


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

        self.r.zrange('weeksOnTop10', 0, -1, withscores=True)
