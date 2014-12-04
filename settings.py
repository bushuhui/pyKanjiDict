#!/usr/bin/env python

import os, sys, shelve, types

dcPageItem = 100
dcRowColor1 = "#E8E8E8"
dcRowColor2 = "#FDFDFD"
dcDisplayMode = 3
dcDisplayMeaning = True
dcDispPageNum = 10

dcSetting = {"cPageItem":dcPageItem, \
            "cRowColor1":dcRowColor1, \
            "cRowColor2":dcRowColor2, \
            "cDisplayMode":dcDisplayMode, \
            "cDisplayMeaning":dcDisplayMeaning, \
            "cDispPageNum":dcDispPageNum}
            
FileName = "settings.cfg"

def ReadSettings():
    if( not os.path.isfile(FileName) ):
        return dcSetting
    
    try:
        dbase = shelve.open(FileName)
        
        s = dbase["setting"]
        return s

        dbase.close()
    except:
        return dcSetting


def WriteSettings(s):
    # delete exist file
    if( os.path.isfile(FileName) ):
        os.remove(FileName)

    try:
        dbase = shelve.open(FileName)
        dbase.clear()
    except:
        return -1

    dbase["setting"] = s
    
    dbase.close()
    
    return 0

if( __name__ == "__main__" ):
    WriteSettings(dcSetting)
    ReadSettings()
