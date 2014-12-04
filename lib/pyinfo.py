#!/usr/bin/env python


import os,sys
import cgitb; cgitb.enable()


cgi_header = '''Content-type: text/html

'''

html_header = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "DTD/xhtml1-transitional.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <style type="text/css">
    body {background-color: #ffffff; color: #000000;}
    body, td, th, h1, h2 {font-family: sans-serif;}
    pre {margin: 0px; font-family: monospace;}
    a:link {color: #000099; text-decoration: none; background-color: #ffffff;}
    a:hover {text-decoration: underline;}
    table {border-collapse: collapse;}    
    .center {text-align: center;}
    .center table { margin-left: auto; margin-right: auto; text-align: left;}
    .center th { text-align: center !important; }
    td, th { border: 1px solid #000000; font-size: 100%; vertical-align: baseline;}    
    h1 {font-size: 150%;}
    h2 {font-size: 125%;}
    .p {text-align: left;}
    .e {background-color: #ccccff; font-weight: bold; color: #000000;}
    .h {background-color: #9999cc; font-weight: bold; color: #000000;}
    .v {background-color: #cccccc; color: #000000;}
    .vr {background-color: #cccccc; text-align: right; color: #000000;}
    img {float: right; border: 0px;}
    hr {width: 100%; background-color: #cccccc; border: 0px; height: 1px; color: #000000;}
    </style>
    <title>pyinfo</title>
</head>
<body><div class="center">
'''

html_footer = '''</div></body></html>'''


def output_header():
    print html_header
    
def output_footer():
    print html_footer
    

#
# Print python infos in html format
#
def pyinfo_html():
    # print python version
    print '''<table border="0" cellpadding="3" width="100%">
                <tr class="h"><td>
                    <h1 class="p"><a href="http://www.python.org/">Python</a> Version: </h1><br>'''
    print '''<h2>''', sys.version, '''</h2>
                </td></tr>
            </table><br />'''
            
    # print python library paths
    print '''<table border="0" cellpadding="3" width="100%">
                <tr class="v" height="30"><td>
                    <h2 class="p">Python library paths:</h2>
                </td></tr>
                <tr class="v"><td>
          '''
    for p in sys.path:
        print p, "<br />"
    print '''   </td></tr>'''
    print '''</table><br />'''
    
    # print environment variables
    print '''<table border="0" cellpadding="3" width="100%">
                <tr class="v" height="30"><td>
                    <h2 class="p">Environment variables:</h2>
                </td></tr>
                <tr><td>
                <table border="0" cellpadding="3" width="100%">'''
    for k in os.environ.keys():
        print '''<tr><td width="30%" align=right>'''
        print "<b>", k, "</b>", '''</td><td width="%70">'''
        if( k == "PATH" ):
            for _p in os.environ[k].split(";"):
                print _p, "<br>\n"
        else:
            print os.environ[k]
        print '''</td></tr>'''
    print '''</table> </td></tr></table><br />'''
    


#
# Print python infos in text format
#
def pyinfo_text():
    print "Python version: "
    print "    ", sys.version
    print ""
    
    print "Python library path: "
    for p in sys.path:
        print "    ", p
    print ""
    
    print "Enviroment variables: "
    for k in os.environ.keys():
        print "    %s : %s" % (k, os.environ[k])

#
# Print python infos by given type format
#   Supported format:
#       all     - in full html format
#       body    - in html format by only body
#       text    - in text format
def pyinfo(type):
    if( type == "all" ):
        # output html header
        output_header()
        
        # print python infos
        pyinfo_html()
        
        # print html footer
        output_footer()
    elif( type == "body" ):
        pyinfo_html()
    elif( type == "text" ):
        pyinfo_text()
    
    
if( __name__ == "__main__" ):
    # check if script running under CGI 
    if( os.environ.has_key("GATEWAY_INTERFACE") ):
        print cgi_header
        pyinfo("all")
    else:
        pyinfo("text")
    