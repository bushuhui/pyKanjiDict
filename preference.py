#!/usr/bin/env python

sH = """Content-type: text/html

<html>

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Web Dictionary</title>
<meta name="keywords" content="hanzi, kanji, chinese, japanese, dictionary">
<meta name="description" content="A web tool for learning hanzi, japanese kanji">
</head>

<body>

<table border="0" style="border-collapse: collapse" width="100%" id="table1">
    <tr>
        <td><a href="display.py" accesskey="d">display</a> |
            <a href="edit.py" accesskey="a">add</a> |
            <a href="preference.py" accesskey="f">preference</a> |
            <a href="edit.py?action=preexport">export</a> |
            <a href="edit.py?action=preimport">import</a>
        </td>
    </tr>
</table><br>"""

sE = """
<p align="center"><font size="2">Copyright 2004 by
<a href="http://www.adv-ci.com/">Shuhui Bu</a></font></p>

</body>

</html>
"""

import os, sys
import cgi, sys, MySQLdb, cPickle, urllib
import time
import cgitb; cgitb.enable()

import db, settings

def EditSettings(f):
    s = settings.ReadSettings()
    
    if( f.has_key("pageitem") ):
        pageitem = f["pageitem"].value.strip()
        try:
            s["cPageItem"] = int(pageitem)
        except:
            s["cPageItem"] = settings.dcPageItem
    
    if( f.has_key("rowcol1") ):
        rowcol1 = f["rowcol1"].value.strip()
        
        if( len(rowcol1) != 7 ):
            s["cRowColor1"] = settings.dcRowColor1
        else:
            s["cRowColor1"] = rowcol1
            
    if( f.has_key("rowcol2") ):
        rowcol2 = f["rowcol2"].value.strip()
        
        if( len(rowcol2) != 7 ):
            s["cRowColor2"] = settings.dcRowColor2
        else:
            s["cRowColor2"] = rowcol2
    
    if( f.has_key("displaymode") ):
        displaymode = f["displaymode"].value.strip()
        
        try:
            s["cDisplayMode"] = int(displaymode)
        except:
            s["cDisplayMode"] = settings.dcDisplayMode
            
    if( f.has_key("displaymeaning") ):
        v = f["displaymeaning"].value.strip()
        
        if( v == "yes" ):
            s["cDisplayMeaning"] = True
        else:
            s["cDisplayMeaning"] = False
            
    if( f.has_key("disppagenum") ):
        v = f["disppagenum"].value.strip()
        
        try:
            s["cDispPageNum"] = int(v)
        except:
            s["cDispPageNum"] = settings.dcDispPageNum
            
    settings.WriteSettings(s)

def PrintForm():
    s = settings.ReadSettings()
    
    if( s["cDisplayMeaning"] ):
        dmY = "checked"
        dmN = ""
    else:
        dmY = ""
        dmN = "checked"
        
    print '''<form method="POST" action="preference.py">
  <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse" bordercolor="#111111" width="100%" id="preference" height="108">
    <tr>
      <td width="25%" height="22" align="right">Page Item Number:</td>
      <td width="75%" height="22"><input type="text" name="pageitem" size="20"''', ''' value="%d"></td>''' % s["cPageItem"], \
    '''</tr>
    <tr>
      <td width="25%" height="28" align="right">Row Color 1:</td>
      <td width="75%" height="28"><input type="text" name="rowcol1" size="20"''', ''' value="%s"></td>''' % s["cRowColor1"], \
    '''</tr>
    <tr>
      <td width="25%" height="21" align="right">Row Color 2:</td>
      <td width="75%" height="21"><input type="text" name="rowcol2" size="20"''', ''' value="%s"></td>''' % s["cRowColor2"], \
    '''</tr>
    <tr>
      <td width="25%" height="30" align="right">Display Mode:</td>
      <td width="75%" height="30"><input type="text" name="displaymode" size="20"''', ''' value="%d"></td>''' % s["cDisplayMode"], \
    '''</tr>
    <tr>
      <td width="25%" height="30" align="right">Display Page Number:</td>
      <td width="75%" height="30"><input type="text" name="disppagenum" size="20"''', ''' value="%d"></td>''' % s["cDispPageNum"], \
    '''</tr>
    <tr>
      <td width="25%" height="30" align="right">Display Meaning:</td>
      <td width="75%" height="30">
      <input type="radio" value="yes" name="displaymeaning" ''', dmY, '''>Yes
      <input type="radio" value="no" name="displaymeaning" ''', dmN, '''>No</td>
    </tr>
  </table>
  <p><input type="submit" value="edit" name="action">&nbsp;
  <input type="reset" value="reset" name="reset"></p>
</form>'''

def DoPreference():
    form = cgi.FieldStorage()
    
    
    if( form.has_key("action") ):
        act = form["action"].value
    else:
        act = ""
        
    # print page header
    print sH

    if( act == "edit" ):
        EditSettings(form)
        print "<br>Edit successful<br>"
        PrintForm()
    else:
        PrintForm()
        
    print sE

if( __name__ == "__main__" ):
    DoPreference()
    
