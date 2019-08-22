# IMPORTING CONFIGURATIONS
import yaml

try:
    with open('config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)
except:
    with open('../config.yaml', 'r') as configfile:
        cfg = yaml.load(configfile)


def placeholder():
    pass


## EXAMPLE - SENTIMENT ANALYSIS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
def check_sentiment(user_message):
    try:
        sentiment = analyzer.polarity_scores(user_message)
        sentiment = sentiment['compound']
        return sentiment
    except:
        return None



    




