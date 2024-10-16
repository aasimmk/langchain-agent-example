import os
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent
DB_PATH = os.path.join(ROOT_DIR, "database", "northwind.db")
print(ROOT_DIR)
print(DB_PATH)
