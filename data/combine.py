import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from requests.exceptions import RequestException
import pickle
import numpy as np

# Load stance and topic datasets
df_stance = pd.read_csv("df_stance.csv")
df_topics = pd.read_csv("df_topics.csv")

# Select relevant columns
df_stance_data = df_stance[["billID", "title", "summary", "topic", "nominate_mid_1"]]
df_topics_data = df_topics[["billID", "Title", "summary", "Minor", "nominate_dim1"]]

# Merge and deduplicate by billID
combined = pd.concat([df_topics_data, df_stance_data])
combined.drop_duplicates(subset="billID", keep="first", inplace=True)
combined.reset_index(drop=True, inplace=True)

# Save combined data
combined.to_csv("combined.csv")
