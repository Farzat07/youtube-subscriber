#!/usr/bin/env python

from os import getenv
from time import sleep

from dotenv import load_dotenv

from components.database import subscriptions
from .utils import analyse_collection

load_dotenv('.env')

while True:
    analyse_collection(subscriptions, getenv("YOUTUBE_API_KEY") or '')
    sleep(30)
