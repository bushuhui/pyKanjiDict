#!/usr/bin/env python

sH = """Content-type: text/html

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja" dir="ltr">

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Web Dictionary</title>
<meta name="keywords" content="hanzi, kanji, chinese, japanese, dictionary">
<meta name="description" content="A web tool for learning hanzi, japanese kanji">
</head>

<body>

"""

sF = """<form method="POST" action="edit.py" enctype="application/x-www-form-urlencoded">
<table cellspacing="0" border="1" style="border-collapse: collapse" bordercolor="#808080" cellpadding="0" width="100%">
    <tr>
      <td width="12%" height="29" align="right">Pinyin:</td>
      <td width="88%" height="29">
      <input type="text" name="pinyin" size="37" style = "width:50%" tabindex="1"></td>
    </tr>
    <tr>
      <td width="12%" height="29" align="right">Word:</td>
      <td width="88%" height="29">
      <input type="text" name="word" size="37" style = "width:50%" tabindex="2"></td>
    </tr>
    <tr>
      <td width="12%" height="31" align="right">Ch-Reading:</td>
      <td width="88%" height="31">
      <input type="text" name="ch_reading" size="37" style = "width:50%" tabindex="3"></td>
    </tr>
    <tr>
      <td width="12%" height="31" align="right">Jp-Reading:</td>
      <td width="88%" height="31">
      <input type="text" name="jp_reading" size="37" style = "width:50%" tabindex="4"></td>
    </tr>
    <tr>
      <td width="12%" height="31" align="right">Meaning:</td>
      <td width="88%" height="31">
      <textarea name="meaning" rows="15" cols="80" style = "width:100%" tabindex="5"></textarea>
      </td>
    </tr>
  </table>
  <p><input type="submit" value="add" name="action" accesskey="s">&nbsp; 
     <input type="reset" value="reset" name="reset">
  </p>
</form>"""

sDT_header = """<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse"
    bordercolor="#111111" width="100%" id="wordtable" height="53">
    <tr>
        <td width="13%" align="center" height="26"><b>Word</b></td>
        <td width="20%" align="center" height="26"><b>Ch-Reading</b></td>
        <td width="20%" align="center" height="26"><b>Jp-Reading</b></td>
        <td width="10%" align="center" height="26"><b>Pinyin</b></td>
        <td width="37%" align="center" height="26"><b>Meaning</b></td>
    </tr>"""
sDT_footer = """</table>"""

sDT_header2 = '''<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse" bordercolor="#111111" width="100%" id="AutoNumber3" height="10">
  <tr>
    <td width="27%" align="center" height="26"><b>Word</b></td>
    <td width="27%" align="center" height="26"><b>Ch-Reading</b></td>
    <td width="27%" align="center" height="26"><b>Jp-Reading</b></td>
    <td width="19%" align="center" height="26"><b>Pinyin</b></td>
  </tr>
'''
sDT_footer2 = """</table>"""


sDT_header3 = '''<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse" bordercolor="#111111" width="100%" id="wordtable3" height="10">
  <tr>
    <td width="25%" align="center" height="26"><b>Word</b></td>
    <td width="30%" align="center" height="26"><b>Reading</b></td>
    <td width="45%" align="center" height="26"><b>Meaning</b></td>
  </tr>'''
  

sDT_row = """<tr>
    <td width="10%" height="26" >%s</td>
    <td width="13%" height="26">
        <a href="%s">%s</a></td>
    <td width="22%" height="26">
        <a href="%s">%s</a></td>
    <td width="18%" height="26">
        <a href="%s">%s</a></td>
    <td width="37%" height="26">%s</td>
  </tr>"""   

sFM_Search = '''<form method="POST" action="display.py" enctype="application/x-www-form-urlencoded">
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse" bordercolor="#000000" width="100%" id="searchform" height="4">
  <tr>
    <td width="100%" height="30">
    <font size="2">&nbsp;Search:</font><input type="text" name="search" size="50" tabindex="1" accesskey="s">&nbsp;
    <input type="submit" value="query" name="action" tabindex="2" accesskey="q"><br>&nbsp; <font size=2><b>py</b>: pinyin, <b>word</b>: word, <b>read</b>: reading, <b>cread</b>:Chinese reading, <b>jread</b>:Japanese reading, <b>meaning</b>: explanation</font></td>
  </tr>
</table>
</form>'''


sE = """
<p align="center"><font size="2">Copyright 2007 by
<a href="http://www.adv-ci.com/">Shuhui Bu</a></font></p>

</body>

</html>
"""

import os,sys

import cgi, sys, MySQLdb, cPickle, urllib
import time
import unicodedata
import cgitb; cgitb.enable()

import db, settings

################################################################################
# define const values
################################################################################
tem_setting = settings.ReadSettings()

cPageItem = tem_setting["cPageItem"]
cRowColor1 = tem_setting["cRowColor1"]
cRowColor2 = tem_setting["cRowColor2"]
cDisplayMode = tem_setting["cDisplayMode"]
cDisplayMeaning = tem_setting["cDisplayMeaning"]
cDispPageNum = tem_setting["cDispPageNum"]

def GetWordNum(cur, type="", value=""):
    if( type == "" ):
        s = "SELECT COUNT(id) FROM words;"
    else:
        if( type == "pinyin" ):
            s = '''SELECT COUNT(id) FROM words WHERE %s LIKE "''' % type
            for item in value.split(" "):
                if( item.strip() != "" ):
                    s += "%" + item.strip()
            s += '''%";'''
        else:
            s = """SELECT COUNT(id) FROM words WHERE %s REGEXP '%s'""" % (type, value);
        
    try:
        cur.execute(s)
        qr = cur.fetchall()
        r = qr[0]
        return r[0]
    except:
        return -1
        
################################################################################
# Print the page list table
################################################################################
def PrintPageList(pagenum, qType="", qValue="", p=1, item_num=1):
    print '''<form method="POST" action="display.py">
            <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse" 
                bordercolor="#000000" width="100%" id="pagelist" height="22">
            <tr> <td width="100%" height="22">'''
    
    minPage = p - cDispPageNum
    maxPage = p + cDispPageNum
    if( minPage < 1 ):
        minPage = 1
    if( maxPage > pagenum ):
        maxPage = pagenum+1
    
    if( qType == "" ):
        qStr = ""
    else:
        qStr = "&action=query&%s=" % qType + urllib.quote_plus(qValue)
    
    print '''<font size="2">word: %d, &nbsp;page: %d, &nbsp;current page: %d</font><br>''' % (item_num, pagenum, p)
    
    if( minPage > 1 ):
        print '''<a href="display.py?p=%d%s" accesskey="3"><font size="2">&lt;&lt;&lt;</font></a>&nbsp;&nbsp;&nbsp;''' % (1, qStr)
    if( p > 1 ):
        print '''<a href="display.py?p=%d%s" accesskey="1"><font size="2">&lt;</font></a>&nbsp;&nbsp;&nbsp;''' % (p-1, qStr)
        
    for i in xrange(minPage, maxPage):
        if i == p:
            print '''&nbsp;&gt;<a href="display.py?p=%d%s"><font size="2">%d</font></a>&lt;''' % (i, qStr, i)
        else:
            print '''&nbsp;<a href="display.py?p=%d%s"><font size="2">%d</font></a>''' % (i, qStr, i)
                
    if( p < maxPage-1 ):
        print '''&nbsp;&nbsp;&nbsp;<a href="display.py?p=%d%s" accesskey="2"><font size="2">&gt;</font></a>''' % (p+1, qStr)
    if( maxPage < pagenum+1):
        print '''&nbsp;&nbsp;&nbsp;<a href="display.py?p=%d%s" accesskey="4"><font size="2">&gt;&gt;&gt;</font></a>''' % (pagenum, qStr)
        
    # print go form
    print '''&nbsp;&nbsp;&nbsp;<input type="text" name="p" size="4" accesskey="g">
            <input type="submit" value="go" name="go">'''
    if( qStr != "" ):
        print '''<input type="hidden" name="action" value="query">'''
        print '''<input type="hidden" name="%s" value="%s">''' % (qType, qValue)
        
    print '''</td></tr></table></form>'''
        
    #print "<br>"
    
################################################################################
#
################################################################################
def SplitJapString(s):
    cSep = "\xe3\x80\x80"
    tLst = []
    for item in s.split(cSep):
        tLst = tLst + item.split(" ")
        
    return tLst

    #return [s]

def SplitHanzi(s):
    l = len(s)
    
    tLst = []
    tS = ""
    
    i = 0
    while i < l:
        if (ord(s[i]) > 128):
            if( tS != "" ):
                tLst.append(tS)
                
            tLst.append(s[i:i+3])
            
            i = i+3
        else:
            tS = tS + s[i]
            
            i = i+1
        
    return tLst


################################################################################
#
################################################################################
def PrintResultInTable(res):
    if( cDisplayMode == 1 ):
        print sDT_header
    elif( cDisplayMode == 2):
        print sDT_header2
    else:
        print sDT_header3
    
    c = cRowColor1;
    
    for r in res:
        sID = r[0]
        
        sPinyin = r[1]
        qPinyin = ""
        lstPinyin = SplitJapString(sPinyin)
        for s in lstPinyin:
            qPinyin = qPinyin + '''<a href="display.py?action=query&py=%s">%s</a>&nbsp;''' % (urllib.quote_plus(s), s)        
        
        sCRead = r[2]
        qCRead = ""
        lstCRead = SplitJapString(sCRead)
        for s in lstCRead:
            qCRead = qCRead + '''<a href="display.py?action=query&cread=%s">%s</a>&nbsp;''' % (urllib.quote_plus(s), s)

        
        sJRead = r[3]
        qJRead = ""
        lstJRead = SplitJapString(sJRead)
        for s in lstJRead:
            qJRead = qJRead + '''<a href="display.py?action=query&jread=%s">%s</a>&nbsp;''' % (urllib.quote_plus(s), s)
        
        sWord = r[4]
        qWord = ""
        lstWord = SplitJapString(sWord)
        #for s in lstWord:
        #    qWord = qWord + '''&nbsp;<a href="display.py?action=query&word=%s">%s</a>''' % (urllib.quote_plus(s), s)
        for sw in lstWord:
            lstZi = SplitHanzi(sw)
            for s in lstZi:
                qWord = qWord + '''<a href="display.py?action=query&word=%s">%s</a>''' % (urllib.quote_plus(s), s)
                
            qWord = qWord + '''&nbsp;<font size="1">(<a href="display.py?action=query&word=%s">S</a>)</font>&nbsp;''' % urllib.quote_plus(sw)
        
        qWord = qWord + '''&nbsp;<font size="1">(<a href="edit.py?action=preedit&id=%s">E</a> ''' % sID + \
                '''<a href="edit.py?action=predel&id=%s">D</a>)</font>''' % sID
        
        #sMeaning = cPickle.loads(r[5].tostring())
        #sMeaning = r[5]
        sMeaning = r[5].tostring()
        tsM = ""
        for ml in sMeaning.splitlines():
            tsM = tsM + ml + "<br>"
        
        
        #print sID, sPinyin, qPinyin, sCRead, qCRead, sJRead, qJRead, sWord, sMeaning, "<br>"
        #print sDT_row % (sWord, sPinyin, sPinyin, sCRead, sCRead, sJRead, sJRead, sMeaning)
        if( cDisplayMode == 1):
            print '''<tr>
                   <td width="13%" height="26"''', ''' bgcolor="%s">%s</td>''' % (c, qWord), \
                '''<td width="20%" height="26"''', ''' bgcolor="%s">%s</td>''' % (c, qCRead), \
                '''<td width="20%" height="26"''', ''' bgcolor="%s">%s</td>''' % (c, qJRead), \
                '''<td width="10%" height="26"''', ''' bgcolor="%s">%s</td>''' % (c, qPinyin), \
                '''<td width="37%" height="26"''', '''bgcolor="%s">%s</td></tr>''' % (c, tsM)
        elif( cDisplayMode == 2):
            print '''  <tr>
                <td width="27%"''', ''' height="36" bgcolor="%s">%s</td>''' % (c, qWord), \
                '''<td width="27%"''', ''' height="36" bgcolor="%s">%s</td>''' % (c, qCRead), \
                '''<td width="27%"''', ''' height="36" bgcolor="%s">%s</td>''' % (c, qJRead), \
                '''<td width="19%"''', ''' height="36" bgcolor="%s">%s</td>''' % (c, qPinyin), \
                '''</tr>'''
            if( tsM != "" and cDisplayMeaning ):
                print '''<tr><td width="90%" colspan="4" height="36"''', \
                    '''bgcolor="%s"><font size="3">%s</font><br></td></tr>''' % (c, tsM)
        else:
            print '''  <tr>
                <td width="25%"''', ''' align="left" height="26" bgcolor="%s">%s</td>''' % (c, qWord), \
                '''<td width="30%"''', ''' align="left" height="26" bgcolor="%s">%s | %s | %s</td>''' % (c, qCRead, qJRead, qPinyin), \
                '''<td width="45%"''', ''' align="left" height="26" bgcolor="%s">%s</td>''' % (c, tsM), \
                '''</tr>'''
        
    
        if( c == cRowColor1 ):
            c = cRowColor2
        else:
            c = cRowColor1
        
    print sDT_footer
    
def FiltePinyinQuery(lst, qryString, begIndex, endIndex):    
    lstQry = []
    mQry = {} 
    i = 0
    for ti in qryString.strip().split(" "):
        tti = ti.strip()
        if( tti == "" ):
            continue

        if( tti[-1].isdigit() ):
            ttx = tti[:-1]
            if( len(ttx) > 0 ):
                lstQry.append(ttx)
                ttx = str(i) + ttx
                mQry[ttx] = i
        else:
            lstQry.append(tti)
            ttx = str(i) + tti
            mQry[ttx] = i
        
        i += 1

    nQry = len(lstQry)
    
    lstRes = []
    for r in lst:
        pinyin = r[1].strip()
        
        rt = {}
        b = 0
        wi = 0
        
        mI = {}
        tic = 0
        tik = 0
        for mtI in pinyin.split("-"):
            if( mtI.strip() == "" ):
                continue
                
            for m2t in mtI.strip().split(" "):
                if( m2t == "" ):
                    continue
                
                mI[tic] = tik
                tic += 1
            
            tik += 1

        for p in pinyin.split(" "):
            ttp = p.strip()
            if( ttp == "" or ttp == "-" ):
                continue
                
            tp = ttp[:-1]
            i=0
            for st in lstQry:
                if( tp == st ):
                    tst = str(i) + st
                    if( rt.has_key(mQry[tst]) ):
                        rt[mQry[tst]].append(mI[wi])
                    else:
                        rt[mQry[tst]] = [mI[wi]]
                i += 1
            wi += 1

        i = 0
        for st in lstQry:
            tst = str(i) + st
            if( not rt.has_key(mQry[tst]) ):
                b = 1
                break
            i += 1
        
        if( b == 1 ):
            continue

        if( tik  < nQry ):
            continue

        if( nQry > 1 ):            
            for i in range(1, nQry):
                l1 = rt[i-1]
                l2 = rt[i]
                
                b1 = 0
                for t in l2:
                    for k in l1:
                        if( t-k == 1 ):
                            b1 = 1
                            break
                        
                    if( b1 == 1 ):
                        break
                
                if( b1 == 1 ):
                    continue
                else:
                    break
                    
            if( b1 == 1 ):
                lstRes.append(r)
        else:
            lstRes.append(r)
    
    tnum = len(lstRes)
    if( begIndex < 1 ):
        begIndex = 1
    if( begIndex > tnum ):
        begIndex = tnum

    if( endIndex < 1 ):
        endIndex = 1
    if( endIndex > tnum ):
        endIndex = tnum
    
    return (tnum, lstRes[begIndex-1:endIndex])
    
################################################################################
# begin main function
################################################################################
def Display():
    t1 = time.time()
    form = cgi.FieldStorage()
    
    dbcon = db.ConnDB()
    if( dbcon == -1 ):
        print sH
        print "Failed to connect db<br>"
        print sE
        sys.exit(0)
    else:
        (con, cur) = dbcon
    
    # print page header
    print sH
    
    # print search form
    print '''<br>''', sFM_Search
    
    if( form.has_key("action") ):
        act = form["action"].value
    else:
        act = ""
    
    # page
    if( form.has_key("p") ):
        try:
            p = int(form["p"].value.strip())
            if( p < 1 ): p = 1
        except:
            p = 1
        
        begIndex = (p - 1) * cPageItem
    else:
        p = 1
        begIndex = 0
    
    qType = ""
    qValue = ""
    qGuessType = ""
    qGuessWord = ""

    # get user input search type
    if( form.has_key("search") ):
        search_phase = form["search"].value

        arr_s = search_phase.split(":")
        input_type = arr_s[0].lower()

        if( len(arr_s) > 1 ):
            if(   input_type == "py" ):
                qGuessType = "py"
                qGuessWord = arr_s[1]
            elif( input_type == "word" ):
                qGuessType = "word"
                qGuessWord = arr_s[1]
            elif( input_type == "read" ):
                qGuessType = "read"
                qGuessWord = arr_s[1]
            elif( input_type == "cread" ):
                qGuessType = "cread"
                qGuessWord = arr_s[1]
            elif( input_type == "jread" ):
                qGuessType = "jread"
                qGuessWord = arr_s[1]
            elif( input_type == "meaning" ):
                qGuessType = "meaning"
                qGuessWord = arr_s[1]
        else:
            qGuessType = "py"
            qGuessWord = search_phase

    
    # perform query
    if( act == "query" ):
        if( form.has_key("word") or qGuessType == "word" ):
            qType = "word"

            if( form.has_key("word") ):
                qValue = form["word"].value
            else:
                qValue = qGuessWord
            
            qWord = qValue
            item_num = GetWordNum(cur, "word", qWord)
            
            s = """SELECT * FROM words WHERE word REGEXP '%s' ORDER BY type LIMIT %d,%d;""" % \
                            (qWord, begIndex, cPageItem)

        elif( form.has_key("read") or qGuessType == "read" ):

            if( form.has_key("read") ):
                _qValue = form["read"].value
            else:
                _qValue = qGuessWord
            
            qs = unicode(_qValue, "utf-8")
            uctype = unicodedata.name(qs[0])
            
            if( uctype[:5] == "LATIN" ):
                qType = "py"
                qValue = _qValue
                
                qPinyin = _qValue
                item_num = GetWordNum(cur, "pinyin", qPinyin)
                
                s = '''SELECT * FROM words WHERE pinyin LIKE "'''
                for item in qPinyin.split(" "):
                    if( item.strip() != "" ):
                        s += "%" + item.strip()
                s += '''%"''' + '''ORDER BY id;'''
            elif( uctype[:8] == "KATAKANA" ):
                qType = "cread"
                qValue = _qValue
                
                qCRead = _qValue
                item_num = GetWordNum(cur, "creading", qCRead)
            
                s = """SELECT * FROM words WHERE creading REGEXP '%s' ORDER BY id LIMIT %d,%d;""" % \
                            (qCRead, begIndex, cPageItem)
            elif( uctype[:8] == "HIRAGANA" ):
                qType = "jread"
                qValue = _qValue
                
                #qJRead = urllib.unquote_plus(form["jread"].value)
                qJRead = _qValue
                item_num = GetWordNum(cur, "jreading", qJRead)
                
                s = """SELECT * FROM words WHERE jreading REGEXP '%s' ORDER BY id LIMIT %d,%d;""" % \
                            (qJRead, begIndex, cPageItem)
                
        elif( form.has_key("py") or qGuessType == "py" ):
            qType = "py"

            if( form.has_key("py") ):
                qValue = form["py"].value
            else:
                qValue = qGuessWord

            qPinyin = qValue
            item_num = GetWordNum(cur, "pinyin", qPinyin)
            
            s = '''SELECT * FROM words WHERE pinyin LIKE "'''
            for item in qPinyin.split(" "):
                if( item.strip() != "" ):
                    s += "%" + item.strip()
            s += '''%"''' + '''ORDER BY id;'''        
                
        elif( form.has_key("cread") or qGuessType == "cread" ):
            qType = "cread"

            if( form.has_key("cread") ):
                qValue = form["cread"].value
            else:
                qValue = qGuessWord
            
            #qCRead = urllib.unquote_plus(form["cread"].value)
            qCRead = qValue
            item_num = GetWordNum(cur, "creading", qCRead)
            
            s = """SELECT * FROM words WHERE creading REGEXP '%s' ORDER BY id LIMIT %d,%d;""" % \
                        (qCRead, begIndex, cPageItem)
        elif( form.has_key("jread") or qGuessType == "jread" ):
            qType = "jread"

            if( form.has_key("jread") ):
                qValue = form["jread"].value
            else:
                qValue = qGuessWord
            
            #qJRead = urllib.unquote_plus(form["jread"].value)
            qJRead = qValue
            item_num = GetWordNum(cur, "jreading", qJRead)
            
            s = """SELECT * FROM words WHERE jreading REGEXP '%s' ORDER BY id LIMIT %d,%d;""" % \
                        (qJRead, begIndex, cPageItem)
        elif( form.has_key("meaning") or qGuessType == "meaning" ):
            qType = "meaning"

            if( form.has_key("meaning") ):
                qValue = form["meaning"].value
            else:
                qValue = qGuessWord
            
            qMeaning = qValue
            item_num = GetWordNum(cur, "meaning", qMeaning)
            
            s = """SELECT * FROM words WHERE meaning REGEXP '%s' ORDER BY id LIMIT %d,%d;""" % \
                        (qMeaning, begIndex, cPageItem)
        else:
            # get total item num
            item_num = GetWordNum(cur)
        
            s = """SELECT * FROM words ORDER BY id LIMIT %d,%d;""" % (begIndex, cPageItem)
    else:
        # get total item num
        item_num = GetWordNum(cur)
        
        s = """SELECT * FROM words ORDER BY id LIMIT %d,%d;""" % (begIndex, cPageItem)
    
    # if query pinyin then filter the result
    if( qType == "py" ):
        cur.execute(s)
        tres = cur.fetchall()
        
        (item_num, res) = FiltePinyinQuery(tres, qValue, begIndex, begIndex + cPageItem)
        #res = tres
        
        #item_num = len(res)
    
    if( item_num == -1 ):
        item_num = 0
        print "No words!<br>"
        
        print sF
        print sE
        
    page_num = item_num / cPageItem
    if( item_num % cPageItem != 0 ):
        page_num = page_num + 1
    if( p > page_num ): p = page_num
    
    # print page list    
    PrintPageList(page_num, qType, qValue, p, item_num)
    #print "<br>"
    
    #try:
    if( qType != "py" ):
        cur.execute(s)
        res = cur.fetchall()
    
    PrintResultInTable(res)
    #except:
    #    print "Query db failed<br>"
            
    
    #print "<br>"
    # print page list
    if( p > 0 and item_num - (p-1) * cPageItem > 15 and cPageItem > 15):
        print "<br>"
        PrintPageList(page_num, qType, qValue, p, item_num)
        #print sFM_Search
    
    t2 = time.time() - t1
    
    print '''<br><p align="center"><font size="2">Query time: %s</font></p>''' % str(t2)
    print sE


if( __name__ == "__main__" ):
    Display()

