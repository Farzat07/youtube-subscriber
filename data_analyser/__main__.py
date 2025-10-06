#!/usr/bin/env python

from time import sleep
from .utils import analyse_collection

from components.database import subscriptions

while True:
    analyse_collection(subscriptions)
    sleep(30)
