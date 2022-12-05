# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 12:10:06 2022

@author: GGG-EXFOLIATOR
"""

import time
from threading import Thread
import numpy as np
class worker(Thread):
    def run(self):
        for x in np.arange(0,11,1):
            print (x)
            time.sleep(1)

class waiter(Thread):
    def run(self):
        for x in np.arange(100,103,1):
            print (x)
            time.sleep(5)

def run():
    worker().start()
    waiter().start()
    
run()