import json
from .preprocess import inspect

if __name__ == "__main__":
    print(json.dumps(inspect(), indent=2))
