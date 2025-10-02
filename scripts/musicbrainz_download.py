import pandas as pd
import musicbrainzngs
from sqlalchemy import create_engine
from time import sleep
import os
import sys
from urllib.parse import quote_plus
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


musicbrainzngs.set_useragent("Music-Streaming-Analysis", "0.1", "joykissell@gmail.com")
encoded_password = quote_plus(config.DB_PASSWORD)
engine = create_engine(
    f"postgresql://{config.DB_USER}:{encoded_password}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )