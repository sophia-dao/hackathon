import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.data_sources import build_features
from app.index_builder import build_gssi

features = build_features()
print("\nFEATURES:")
print(features.head())

gssi = build_gssi(features)

print("\nGSSI:")
print(gssi.head())
print(gssi.describe())