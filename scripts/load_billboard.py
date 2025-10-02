import pandas as pd
from sqlalchemy import create_engine
import os
import sys
from urllib.parse import quote_plus
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

df = pd.read_csv("data/charts.csv")

#to match database schema
df = df.rename(columns = {
    "song": "song_title",
    "date": "week"
})
df = df[["song_title", "artist", "week", "rank"]]
#connect to postgres
# URL encode the password to handle special characters like %
encoded_password = quote_plus(config.DB_PASSWORD)
engine = create_engine(
    f"postgresql://{config.DB_USER}:{encoded_password}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )

#write to table
df.to_sql("billboard100", engine, if_exists = "append", index = False)