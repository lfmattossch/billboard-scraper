FROM python:2

WORKDIR /home/luiz/Projects/billboard-scraper/billboard

RUN apt-get update
RUN apt-get install libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["scrapy crawl last50weeks"]
