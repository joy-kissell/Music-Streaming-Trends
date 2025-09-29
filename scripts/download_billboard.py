import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KAGGLE_CONFIG_DIR
# Make sure the environment variable points to your kaggle.json (or ~/.kaggle/kaggle.json)
os.environ['KAGGLE_CONFIG_DIR'] = KAGGLE_CONFIG_DIR 

# Use the Kaggle API to download & unzip the dataset
os.system("kaggle datasets download -d dhruvildave/billboard-the-hot-100-songs -p data --unzip")

# Verify files
import os
print("Files in data folder:", os.listdir("data"))
