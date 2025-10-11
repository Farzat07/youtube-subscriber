#!/usr/bin/env python

from time import sleep
from components.database import subscriptions

from .utils import collect_data

while True:
    collect_data(subscriptions)
    sleep(60)
