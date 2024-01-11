import random
import time
import csv

import requests
from bs4 import BeautifulSoup

import setting


class Article:
    min = 0
    max = 0

    @classmethod
    def export_csv(cls, titles):
        header = setting.RAW_DATA_HEADER
        path = setting.RAW_DATA_FILE_PATH_FOR_SCRAPING + str(cls.min) + "-" + str(cls.max) + ".csv"
        with open(path, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(titles)

    @classmethod
    def get_all_titles(cls):
        title_list = []
        min_page = cls.min
        max_page = cls.max

        for i in range(max_page):
            page = i + 1
            if page >= min_page:
                result = Article.get_titles_from_one_page(page)
                title_list.extend(result)

                if page != max_page:
                    sec = random.randint(50, 150)
                    print(sec)
                    time.sleep(sec)

        return title_list

    @classmethod
    def get_titles_from_one_page(cls, page: int):
        title_list = []
        url = setting.REQUEST_URL + str(page) + "/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        contents = soup.select(".content")

        for content in contents:
            strong_tag = content.select(".has-text-weight-bold strong")
            if not strong_tag:
                continue
            title = strong_tag[0].text
            datetime_tag = content.select(".article-list-item-date time")
            datetime = datetime_tag[0]["datetime"]
            new_list = [
                title,
                datetime
            ]
            title_list.append(new_list)

        return title_list


if __name__ == "__main__":
    Article.min = 71
    Article.max = 100
    result = Article.get_all_titles()
    Article.export_csv(result)
