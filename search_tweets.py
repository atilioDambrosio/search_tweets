import json
import sys
import threading
from datetime import datetime

import snscrape.modules.twitter as sntwitter
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import pathlib


class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.current_path = str(pathlib.Path(__file__).parent.absolute())
        self.load_ui()

    def load_ui(self):
        uic.loadUi("assets/searchTweets.ui",self)
        self.start_button.clicked.connect(self.start_search)
        self.start_manual_query.clicked.connect(self.start_manual_search)
        self.limit = int(self.line_limit.text())

    def start_manual_search(self):
        self.query = self.line_manual_query.text()
        self.start_thread()

    def start_thread(self):
        search_tweets_text = threading.Thread(target=self.search_tweets)
        search_tweets_text.daemon = True
        search_tweets_text.start()

    def start_search(self):
        self.query = self.build_query()
        self.start_thread()

    def search_tweets(self):
        tweets = []
        i = 0
        for tweet in sntwitter.TwitterSearchScraper(self.query).get_items():
            # break
            if len(tweets) == self.limit:
                break
            else:
                tweets.append([tweet.date, tweet.user, tweet.content])
                self.label_loading.setText(str(tweet.date))

            i = i + 1
        df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet'])
        now = datetime.now()
        date_time = now.strftime("%m_%d_%Y_%H_%M_%S")
        name_file = "tweets_" + date_time + ".csv"
        df.to_csv(name_file)
        file_name = "finish, csv in: " + name_file
        self.label_loading.setText(file_name)

    def build_query(self):
        search_word = self.get_words(self.line_words.text())
        search_hastag = self.get_words(self.line_hastags.text())
        search_user = self.get_users(self.line_users.text())
        search_language = self.get_language(self.line_language.text())
        search_date = self.get_dates(self.line_until.text(), self.line_since.text())
        query_list = [search_word, search_hastag, search_user, search_language, search_date]
        query = ""
        for qy in query_list:
            query = query + qy + " "
        return query[:-1]

    def get_dates(self, text_until, text_since):
        date_until = "until:" + text_until
        date_since = "since:" + text_since
        date = "(" + date_until + " " + date_since + ")"
        return date

    def get_words(self, text_string):
        replace_string = text_string.replace(" ", " OR ")
        new_query = "(" + replace_string + ")"
        return new_query

    def get_language(self, text_language):
        return "lang:" + text_language

    def get_users(self, text_string):
        replace_string = text_string.replace(" ", " OR from:")
        __replace_string = "from:" + replace_string
        new_query = "(" + __replace_string + ")"
        return new_query


if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())