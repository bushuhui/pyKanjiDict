#!/usr/bin/env python

import os, sys
import shelve, types

import db

def ExportToFile(FileName):
    # delete exist file
    if( os.path.isfile(FileName) ):
        os.remove(FileName)
    
    # connect db
    dbcon = db.ConnDB()
    
    if( dbcon == -1 ):
        return -1
    else:
        (con, cur) = dbcon
    
    try:
        dbase = shelve.open(FileName)
        dbase.clear()
    except:
        return -2
    
    # save db setting
    s = db.GetDBSetting()
    dbase["dbsetting"] = s
    
    # save table structure
    s = "SHOW FULL COLUMNS FROM words;";
    try:
        cur.execute(s)
        
        res = cur.fetchall()
        dbase["tablestruct"] = res
    except:
        dbase["tablestruct"] = []
    
    s = "SELECT COUNT(id) FROM words;"
    try:
        cur.execute(s)
        res = cur.fetchall()
        
        tres = res[0]
        ln = tres[0]
    except:
        return -3
    
    bc = 100
    bn = ln / 100
    if( ln % 100 != 0 ):
        bn = bn + 1
    
    lstTable = []
    for i in range(0, bn):
        ibegin = i * bc
        
        s = "SELECT * FROM words LIMIT %d,%d;" % (ibegin, bc)
        
        try:
            cur.execute(s)
            
            res = cur.fetchall()
            
            for l in res:
                lt = []
                
                for item in l:
                    if( type(item).__name__ == "array" ):
                        tb = item.tostring()
                        
                        lt.append(tb)
                    else:
                        lt.append(item)
                
                lstTable.append(tuple(lt))
        except:
            return -4
        
    try:
        dbase["table_words"] = lstTable
    except:
        return -5
        
    # close file
    dbase.close()
    
    return 0

def ImportFromFile(FileName):
    dbcon = db.ConnDB()
    
    if( dbcon == -1 ):
        return -1
    else:
        (con, cur) = dbcon
        
    try:
        dbase = shelve.open(FileName)
    except:
        return -2
    
    if( not dbase.has_key("tablestruct") ):
        return -3
    else:
        tablestruct = dbase["tablestruct"]
        cm = {}
        i = 0
        for colitem in tablestruct:
            cm[colitem[0]] = i
            i = i + 1
            
    if( not dbase.has_key("table_words") ):
        return -4
    
    lstTable = dbase["table_words"]
    for ln in lstTable:
        s = '''SELECT word, pinyin, creading, jreading, meaning, ctime, mtime, level, bookmark
                FROM words WHERE word="%s";''' % ln[cm["word"]]
        
        try:
            r = cur.execute(s)
            if( r == 0 ):
                ct = ln[cm["ctime"]].strftime("%Y-%m-%d %H:%M:%S")
                mt = ln[cm["mtime"]].strftime("%Y-%m-%d %H:%M:%S")
                s = '''INSERT INTO words (word, pinyin, creading, jreading, meaning, ctime, mtime, level, bookmark)
                        VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s", %d, %d);''' % \
                        (ln[cm["word"]], ln[cm["pinyin"]], ln[cm["creading"]], ln[cm["jreading"]], \
                         ln[cm["meaning"]], ct, mt, ln[cm["level"]], ln[cm["bookmark"]])
                r = cur.execute(s)
            else:
                res = cur.fetchall()
                
                if( res[0][6] < ln[cm["mtime"]] ):
                    s = '''UPDATE words SET pinyin="%s", creading="%s", jreading="%s", meaning="%s",
                                            mtime="%s", level="%s", bookmark="%s" WHERE word="%s";''' %\
                        (ln[cm["pinyin"]], ln[cm["creading"]], ln[cm["jreading"]], ln[cm["meaning"]],
                         ln[cm["mtime"]], ln[cm["level"]], ln[cm["bookmark"]], ln[cm["word"]])
                    
                    r = cur.execute(s)
        except:
            return -5
                
            
    return 0
    
if( __name__ == "__main__" ):
    #print ExportToFile("test.db")
    print ImportFromFile("test.db")