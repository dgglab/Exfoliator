# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 10:25:08 2022

@author: elijah
"""
def get_externalT():
    return "IN_PV_1"
def get_surfaceT():
    return "IN_PV_2"
def get_transfermediumT():
    return "IN_PV_7"
def get_weight():
    return "IN_PV_90"
def set_externalT(goal):
    return "OUT_SP_1 %s" %goal
def set_surfaceT(goal):
    return "OUT_SP_2 %s" %goal