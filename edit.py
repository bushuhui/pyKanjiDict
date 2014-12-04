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
  <p><input type="submit" value="add" name="action" tabindex="6" accesskey="s">&nbsp; 
     <input type="reset" value="reset" name="reset" tabindex="7">
  </p>
</form>"""


sE = """
<p align="center"><font size="2">Copyright 2004 by
<a href="http://www.adv-ci.com/">Shuhui Bu</a></font></p>

</body>

</html>
"""


import os, sys
import cgi, MySQLdb, cPickle, urllib
import time
import cgitb; cgitb.enable()

try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass

import db, ImExport

################################################################################
# Add or Edit item
# Argument:
#   f       form dic
#   dbcon   data base connection
################################################################################
def AddEditItem(f, dbcon):
    (con, cur) = dbcon
    
    s = 0
    if( f.has_key("id") ):
        id = f["id"].value.strip()
    else:
        id = ""
        
    if( f.has_key("word") ):
        word = f["word"].value.strip()
        s = s + 1
    else:
        word = ""
    
    if( f.has_key("pinyin") ):
        pinyin = f["pinyin"].value.strip()
        s = s + 1
    else:
        pinyin = ""
    
    if( f.has_key("ch_reading") ):
        ch_reading = f["ch_reading"].value.strip()
        s = s + 1
    else:
        ch_reading = ""
        
    if( f.has_key("jp_reading") ):
        jp_reading = f["jp_reading"].value.strip()
        s = s + 1
    else:
        jp_reading = ""
        
    if( f.has_key("meaning") ):
        tmeaning = f["meaning"].value.strip()
        s = s + 1
    else:
        tmeaning = ""
    meaning = tmeaning
    #meaning = cPickle.dumps(tmeaning, 1)
               
    if( s == 0 ):
        return -1
    
    if( f["action"].value == "add" ):
        """ add new item """
        
        # now search wheter word exist   
        s = "SELECT id FROM words WHERE word='%s'" % word
        cur.execute(s)
        res = cur.fetchall()
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        if( len(res) == 0 ):
            #s = """INSERT INTO words (word, pinyin, creading, jreading, meaning, mtime)
            #        VALUES("%s", "%s", "%s", "%s", "%s", "%s");"""
            s = """INSERT INTO words (word, pinyin, creading, jreading, meaning, ctime, mtime)
                    VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s");""" % (word, pinyin, ch_reading, jp_reading, meaning, t, t)
            try:
                #cur.execute(s, (word, pinyin, ch_reading, jp_reading, MySQLdb.escape_string(meaning), t))
                #cur.execute(s, (word, pinyin, ch_reading, jp_reading, meaning, t))
                cur.execute(s)
            except:
                return -1
        else:
            print '''<br><font size="4">Word item exist! Please confirm!</font><br><br>'''
            
            dicWordItem = {}
            dicWordItem["id"] = id
            dicWordItem["word"] = word
            dicWordItem["pinyin"] = pinyin
            dicWordItem["creading"] = ch_reading
            dicWordItem["jreading"] = jp_reading
            dicWordItem["meaning"] = meaning
            
            # print new item
            print '''New item:<br>'''
            PrintForm(f, dbcon, id=res[0][0], type="fedit", dw=dicWordItem)
            
            # print old item
            print '''Old item:<br>'''
            PrintForm(f, dbcon, id=res[0][0], type="edit")
            
            return 1
            
            '''
            #s = """UPDATE words SET pinyin="%s", creading="%s", jreading="%s", meaning="%s", mtime="%s"
            #    WHERE word="%s";"""
            s = """UPDATE words SET pinyin="%s", creading="%s", jreading="%s", meaning="%s", mtime="%s"
                WHERE word="%s";""" % (pinyin, ch_reading, jp_reading, meaning, t, word)
            try:
                #cur.execute(s, (pinyin, ch_reading, jp_reading, MySQLdb.escape_string(meaning), t, word))
                #cur.execute(s, (pinyin, ch_reading, jp_reading, meaning, t, word))
                cur.execute(s)
            except:
                return -1
            '''
    elif( f["action"].value == "edit" ):
        """ edit given item """
        
        if( id == "" ):
            print "No id specified!<br><br>"
            return -1

        # now search wheter word exist   
        s = "SELECT id FROM words WHERE word='%s'" % word
        cur.execute(s)
        res = cur.fetchall()
        
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if( len(res) == 0 ):
            #s = """UPDATE words SET pinyin="%s", creading="%s", jreading="%s", meaning="%s", mtime="%s"
            #    WHERE word="%s";"""
            s = """UPDATE words SET word="%s", pinyin="%s", creading="%s", jreading="%s", meaning="%s", mtime="%s"
                WHERE id="%s";""" % (word, pinyin, ch_reading, jp_reading, meaning, t, id)
            try:
                #cur.execute(s, (pinyin, ch_reading, jp_reading, MySQLdb.escape_string(meaning), t, word))
                #cur.execute(s, (pinyin, ch_reading, jp_reading, meaning, t, word))
                cur.execute(s)
            except:
                return -1
        else:
            if( int(id) == res[0][0] ):
                s = """UPDATE words SET word="%s", pinyin="%s", creading="%s", jreading="%s", meaning="%s", mtime="%s"
                    WHERE id="%s";""" % (word, pinyin, ch_reading, jp_reading, meaning, t, id)
                try:
                    #cur.execute(s, (pinyin, ch_reading, jp_reading, MySQLdb.escape_string(meaning), t, word))
                    #cur.execute(s, (pinyin, ch_reading, jp_reading, meaning, t, word))
                    cur.execute(s)
                except:
                    return -1
            else:
                print '''<br><font size="4">Word item exist! Please confirm!</font><br><br>'''
                
                dicWordItem = {}
                dicWordItem["id"] = id
                dicWordItem["word"] = word
                dicWordItem["pinyin"] = pinyin
                dicWordItem["creading"] = ch_reading
                dicWordItem["jreading"] = jp_reading
                dicWordItem["meaning"] = meaning
                
                # print new word item
                print '''New item:<br>'''
                PrintForm(f, dbcon, id=res[0][0], type="fedit", dw=dicWordItem)
                
                # print old word item
                print '''Old item:<br>'''
                PrintForm(f, dbcon, id=res[0][0], type="edit")
                
                return 1            
    elif( f["action"].value == "fedit" ):
        """ edit given item """
        
        if( id == "" ):
            print "No id specified!<br><br>"
            return -1
       
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        
        #s = """UPDATE words SET pinyin="%s", creading="%s", jreading="%s", meaning="%s", mtime="%s"
        #    WHERE word="%s";"""
        s = """UPDATE words SET word="%s", pinyin="%s", creading="%s", jreading="%s", meaning="%s", mtime="%s"
            WHERE id="%s";""" % (word, pinyin, ch_reading, jp_reading, meaning, t, id)
        try:
            #cur.execute(s, (pinyin, ch_reading, jp_reading, MySQLdb.escape_string(meaning), t, word))
            #cur.execute(s, (pinyin, ch_reading, jp_reading, meaning, t, word))
            cur.execute(s)
        except:
            return -1
    
    return 0    


################################################################################
# Print edit form
# Argument:
#   f       form dic
#   dbcon   data base connection
################################################################################
def PrintForm(f, dbcon, id=-1, type="edit",dw={}):
    (con, cur) = dbcon
    
    if( dw.has_key("word") ):
        sID = dw["id"]
        sPinyin = dw["pinyin"]
        sCRead = dw["creading"]
        sJRead = dw["jreading"]
        sWord = dw["word"]
        sMeaning = dw["meaning"]
    else:
        if( id == -1 ):
            if( f.has_key("id") ):
                id = f["id"].value.strip()
            else:
                print "No id specified!<br><br>"
                print sF
                return -1
        
        s  = "SELECT * FROM words WHERE id=%s;" % id
        try:
            cur.execute(s)
        except:
            print "Query db failed!<br><br>"
            print sF
            return -1
        
        res = cur.fetchall()
        if( len(res) < 1 ):
            print "Given id item didnt exist!<br><br>"
            print sF
            return -1
        
        r = res[0]
        
        sID = r[0]
        sPinyin = r[1]
        sCRead = r[2]
        sJRead = r[3]
        sWord = r[4]
        sMeaning = r[5].tostring()
    
    # print caution message
    if( type == "del" ):
        print '''<br><b><font size="5" color="#FF0000">Caution! Permanently delete!</font></b><br>'''
        print '''Click <a href="display.py">here</a> to return.<br>'''
    
    print '''<form method="POST" action="edit.py" enctype="application/x-www-form-urlencoded">
    <table cellspacing="0" border="1" style="border-collapse: collapse" bordercolor="#808080" cellpadding="0" width="100%">
    <tr>
      <td width="12%" height="29" align="right">Pinyin:</td>
      <td width="88%" height="29">
      <input type="text" name="pinyin" size="37" style = "width:50%" tabindex="1"''', \
      '''value="%s"></td>''' % sPinyin, \
    '''</tr>
    <tr>
      <td width="12%" height="29" align="right">Word:</td>
      <td width="88%" height="29">
      <input type="text" name="word" size="37" style = "width:50%" tabindex="2"''', \
      '''value="%s"></td>''' % sWord, \
    '''</tr>
    <tr>
      <td width="12%" height="31" align="right">Ch-Reading:</td>
      <td width="88%" height="31">
      <input type="text" name="ch_reading" size="37" style = "width:50%" tabindex="3"''', \
    '''value="%s"></td>''' % sCRead,  \
    '''</tr>
    <tr>
      <td width="12%" height="31" align="right">Jp-Reading:</td>
      <td width="88%" height="31">
      <input type="text" name="jp_reading" size="37" style = "width:50%" tabindex="4"''', \
      '''value="%s"></td>''' % sJRead, \
    '''</tr>
    <tr>
      <td width="12%" height="31" align="right">Meaning:</td>
      <td width="88%" height="31">
      <textarea name="meaning" rows="15" cols="80" style = "width:100%" tabindex="5">''' + sMeaning + '''</textarea>
      </td>
    </tr>
    </table>''' , \
    '''<p><input type="submit" value="%s" name="action" tabindex="6" accesskey="s">&nbsp; 
     <input type="reset" value="reset" name="reset" tabindex="7"></p>''' % type, \
     '''<input type="hidden" name="id" value="%s"></form>''' % sID
    
    
################################################################################
#
################################################################################
def DeleteWord(f, dbcon):
    (con, cur) = dbcon
    
    if( f.has_key("id") ):
        id = f["id"].value.strip()
    else:
        print "No id specified!<br><br>"
        print sF
        return -1
    
    s  = "DELETE FROM words WHERE id=%s;" % id
    try:
        cur.execute(s)
    except:
        print "Query db failed!<br><br>"
        return -1
    
    return 0
    

    
################################################################################
# Print form contents
# Argument:
#   f       form dic
################################################################################
def PrintFormContents(f):
    print "form len: ", len(f), "<br>"
    for item in f:
        print "[", item, "] ", len(item), "<br>"


def PrintImExportForm(form, dbcon, type):
    if( type == "import" ):
        szInputName = "uploadfile"
        szInputType = "file"
        szInputValue = ""
    else:
        szInputName = "filename"
        szInputType = "text"
        szInputValue = "%s.db" % time.strftime("%Y-%m-%d")
        
    print '''<form method="POST" action="edit.py" enctype="multipart/form-data">
    Filename: <input type="%s" name="%s" size="37"''' % (szInputType, szInputName), \
    '''value="%s" tabindex="1"><p>''' % szInputValue, \
    '''<input type="submit" value="%s" name="action">&nbsp; ''' % type, \
    '''<input type="reset" value="reset" name="B2"></p></form>'''

def save_uploaded_file (form, form_field, upload_dir):
    """This saves a file uploaded by an HTML form.
       The form_field is the name of the file input field from the form.
       For example, the following form_field would be "file_1":
           <input name="file_1" type="file">
       The upload_dir is the directory where the file will be written.
       If no file was uploaded or if the field does not exist then
       this does nothing.
    """
    #form = cgi.FieldStorage()
    if not form.has_key(form_field):
        return -1
    fileitem = form[form_field]
    if not fileitem.file:
        return -2
    
    # retrive the file name
    if( fileitem.filename.find("\\") > 0 ):
        lstFileName = fileitem.filename.split("\\")
    if( lstFileName[-1].find("/") > 0 ):
        lstFileName = lstFileName[-1].split("/")
        
    #lstFileName = os.path.split(fileitem.filename)
    fn = os.path.join(upload_dir, lstFileName[-1])
    fout = file (fn, 'wb')
    while 1:
        chunk = fileitem.file.read(100000)
        if not chunk: break
        fout.write (chunk)
    fout.close()
    
    #print fn
    #return 0
    return fn


 

################################################################################
# Main function
################################################################################
def EditWord():
    form = cgi.FieldStorage()
    
    
    if( form.has_key("action") ):
        act = form["action"].value
    else:
        act = ""
        
    # print page header
    print sH
    
    # connect to db server
    dbcon = db.ConnDB()
    if( dbcon == -1 ):
        print sH
        print "Connect db failed!<br>"
        print sE
        sys.exit(0)
    
        
    # if debug print form contents
    #PrintFormContents(form)
    #print "<br><br>"
    
    # add or update item
    if( (act == "add") | (act == "edit") | (act == "fedit") ):
        r = AddEditItem(form, dbcon)
        
        if( r == 0 ):
            print "<br>%s success!<br>" % act
        elif( r == 1 ):
            print sE
            return
        else:
            print "<br>Insert failed!<br>"
    elif( act == "del" ):
        r = DeleteWord(form, dbcon)
        
        if( r == 0 ):
            print "<br>Delete given item success!<br>"
        else:
            print "<br>Delete given item failed!<br>"
    elif( act == "export" ):
        if( form.has_key("filename") ):
            filename = form["filename"].value
        else:
            filename = "export.db"
            
        if( filename == "" ):
            filename = "export.db"
            
        f2 = os.path.join("tmp", filename)
        
        r = ImExport.ExportToFile(f2)
        if( r == 0 ):
            print '''<br> Export: Export to file <a href="tmp/%s">%s</a> successful!<br>''' % (filename, filename)
        elif( r == -1 ):
            print "<br> Export: Connect db server failed!<br>"
        elif( r == -2 ):
            print "<br> Export: Open export file failed!<br>"
        elif( r == -3 or r == -4 ):
            print "<br> Export: Query db failed!<br>"
        elif( r == -5 ):
            print "<br> Export: Save export to disk failed<br>"
        else:
            print "<br> Export: Unknow error!<br>"
    elif( act == "import" ):
        #PrintFormContents(form)
        
        r = save_uploaded_file(form, "uploadfile", "tmp")
        if type(r).__name__ == "int":
            print "<br> Import: Upload file error! %d<br>" % r
        else:
            filename = r
        
            r = ImExport.ImportFromFile(filename)
            if( r == 0 ):
                print "<br> Import: Import from file '%s' successful!<br>" % filename
            elif( r == -1 ):
                print "<br> Import: Connect db server failed!<br>"
            elif( r == -2 ):
                print "<br> Import: Open export file failed!<br>"
            elif( r == -3 or r == -4):
                print "<br> Import: Backup data file error!<br>"
            elif( r == -5 ):
                print "<br> Import: Query db failed!<br>"
            else:
                print "<br> Import: Unknow error!<br>"
            
            # remove tem file
            os.remove(filename)
    
    # if in edit mode then print form with contents
    if( act == "preedit" ):
        PrintForm(form, dbcon)
    elif( act == "predel" ):
        PrintForm(form, dbcon, -1, "del")
    elif( act == "preimport" ):
        PrintImExportForm(form, dbcon, "import")
    elif( act == "preexport" ):
        PrintImExportForm(form, dbcon, "export")
    else:
        # print default form
        print sF
    
    # print html footer
    print sE


if( __name__ == "__main__" ):
    EditWord()
