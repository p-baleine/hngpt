import os
from joblib import Memory

CACHE_DIR = os.environ.get(
    "METAANALYSER_CACHE_DIR",
    os.path.join("..", ".cache")
)

memory = Memory(CACHE_DIR, verbose=0)
