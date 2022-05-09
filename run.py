#! /usr/bin/env python
# import os
# print(os.environ)
from flaskr import create_app
from prediction.predict import cv_silhouette_scorer

if __name__ == "__main__":
    create_app().run(port=5001, debug=True)

