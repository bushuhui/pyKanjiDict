#!/usr/bin/env python


""" Modified simple CGI & HTTP server
"""

import os
import sys
import time
import urllib
import BaseHTTPServer
import SimpleHTTPServer
import select
import CGIHTTPServer


import db


class T_CGIHTTPRequestHandler(CGIHTTPServer.CGIHTTPRequestHandler):

	"""Complete HTTP server with GET, HEAD and POST commands.
	GET and HEAD also support running CGI scripts.
	The POST command is *only* implemented for CGI scripts.
	"""
	
	script_type = [".py", ".php"]
	exe_php = r"php.exe"
	
	def do_POST(self):
		"""Serve a POST request.

		This is only implemented for CGI scripts.

		"""
	
		if self.is_cgi():
			self.run_cgi()
		else:
			self.send_error(501, "Can only POST to CGI scripts")

	def send_head(self):
		"""Version of send_head that support CGI scripts"""
		
		#print "send_head"
		#print self.path
				
		if self.is_cgi():
			return self.run_cgi()
		else:
			return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

	def is_cgi(self):
		"""Test whether self.path corresponds to a CGI script.

		Return a tuple (dir, rest) if self.path requires running a
		CGI script, None if not.  Note that rest begins with a
		slash if it is not empty.

		The default implementation tests whether the path
		begins with one of the strings in the list
		self.cgi_directories (and the next character is a '/'
		or the end of the string).
		"""
		
		defaultFile = ["index.py", "index.php", "index.htm", "index.html"]

		path = self.path
		#print "self.path1= '%s'" % path

		# shutdown server
		if( path == "/SHUTDOWN" ):
			db.StopDBServer()

			#time.sleep(1)
			os._exit(0)

		if( path[-1] == '/' ):
			for f in defaultFile:
				tf = path[1:] + f
				#tf = os.path.join(www_root, tf)
				if os.path.exists(tf):
					self.path = path + f

					if ( f.find(".py") > 0 or f.find(".php") > 0):
						return True;
					else:
						return False;
			
			#print "self.path2= '%s'" % self.path
			return False
		else:
			rest = path[1:]
			
			# sepearte the query string & file
			i = rest.rfind('?')
			if i >= 0:
				rest, query = rest[:i], rest[i+1:]
			else:
				query = ''
				
			i = rest.rfind('.py')
			if( i > 0 ):
				return True
				
			i = rest.rfind('.php')
			if( i > 0 ):
				return True
				
			if os.path.isdir(rest):
				self.path = self.path + "/"
				
			return False
	
	def apache_queryformat(self, path):
		#print "path: ", path
		path_info = ""
		
		for st in self.script_type:
			si = path.find(st)
			if( si > 0 ):
				six = si + len(st)
				rest = path[:six]
				
				query = path[six:]
				if( query != "" ):
					if( query[0] == "/" ):
						query = query[1:]
						
					i = query.rfind('?')
					if i >= 0:
						q1 = query[:i]
						q2 = query[i+1:]
						
						query = q2
						path_info = "/" + q1
					else:
						path_info = "/" + query
						query = ""

				return (rest, query, path_info)				
		
		# sepearte the query string & file
		i = rest.rfind('?')
		if i >= 0:
			rest, query = rest[:i], rest[i+1:]
		else:
			query = ''
			
		return (rest, query, path_info)

			
	def run_cgi(self):
		"""Execute a CGI script."""

		#print "run_cgi"
		#dir, rest = self.cgi_info
		
		# the rest is relative path & file name & query string
		#rest = self.path[1:]		
		(rest, query, path_info) = self.apache_queryformat(self.path[1:])
		#print "path     : ", self.path
		#print "rest     : ", rest
		#print "query    : ", query
		#print "path_info: ", path_info
		
		# set script file & name
		#scriptfile = os.path.join(www_root, rest)
		#scriptname = os.path.join(www_root, rest)
		scriptfile = rest
		scriptname = rest
		#print "scriptfile:", scriptfile
		#print "scriptname:", scriptname
		
		# get script file ext name
		scriptext = os.path.splitext(scriptfile)[1]

		if not os.path.exists(scriptfile):
			self.send_error(404, "No such CGI script (%s)" % `scriptname`)
			return
		if not os.path.isfile(scriptfile):
			self.send_error(403, "CGI script is not a plain file (%s)" %
							`scriptname`)
			return
			
		ispy = self.is_python(scriptname)
		isphp = False
		if( scriptext == ".php" ):
			isphp = True
		
		if (not ispy):
			if( not isphp ):
				if not (self.have_fork or self.have_popen2 or self.have_popen3):
					self.send_error(403, "CGI script is not a Python script (%s)" %
								`scriptname`)
					return
				if not self.is_executable(scriptfile):
					self.send_error(403, "CGI script is not executable (%s)" %
								`scriptname`)
					return

		# Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
		# XXX Much of the following could be prepared ahead of time!
		env = {}
		env['SERVER_SOFTWARE'] = self.version_string()
		env['SERVER_NAME'] = self.server.server_name
		env['GATEWAY_INTERFACE'] = 'CGI/1.1'
		env['SERVER_PROTOCOL'] = self.protocol_version
		env['SERVER_PORT'] = str(self.server.server_port)
		env['REQUEST_METHOD'] = self.command
		env['REQUEST_URI'] = self.path
		uqrest = urllib.unquote(rest)
		env['PATH_INFO'] = path_info
		env['PATH_TRANSLATED'] = self.translate_path(uqrest)
		env['SCRIPT_NAME'] = '/' + scriptname
		if query:
			env['QUERY_STRING'] = query
		host = self.address_string()
		if host != self.client_address[0]:
			env['REMOTE_HOST'] = host
		env['REMOTE_ADDR'] = self.client_address[0]
		# XXX AUTH_TYPE
		# XXX REMOTE_USER
		# XXX REMOTE_IDENT
		if self.headers.typeheader is None:
			env['CONTENT_TYPE'] = self.headers.type
		else:
			env['CONTENT_TYPE'] = self.headers.typeheader
		length = self.headers.getheader('content-length')
		if length:
			env['CONTENT_LENGTH'] = length
		accept = []
		for line in self.headers.getallmatchingheaders('accept'):
			if line[:1] in "\t\n\r ":
				accept.append(line.strip())
			else:
				accept = accept + line[7:].split(',')
		env['HTTP_ACCEPT'] = ','.join(accept)
		ua = self.headers.getheader('user-agent')
		if ua:
			env['HTTP_USER_AGENT'] = ua
		co = filter(None, self.headers.getheaders('cookie'))
		if co:
			env['HTTP_COOKIE'] = ', '.join(co)
		# XXX Other HTTP_* headers
		# Since we're setting the env in the parent, provide empty
		# values to override previously set values
		for k in ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH',
				'HTTP_USER_AGENT', 'HTTP_COOKIE'):
			env.setdefault(k, "")
		os.environ.update(env)
		
		self.send_response(200, "Script output follows")
		
		decoded_query = query.replace('+', ' ')

		if self.have_fork:
			# Unix -- fork as we should
			args = [script]
			if '=' not in decoded_query:
				args.append(decoded_query)
			nobody = nobody_uid()
			self.wfile.flush() # Always flush before forking
			pid = os.fork()
			if pid != 0:
				# Parent
				pid, sts = os.waitpid(pid, 0)
				# throw away additional data [see bug #427345]
				while select.select([self.rfile], [], [], 0)[0]:
					if not self.rfile.read(1):
						break
				if sts:
					self.log_error("CGI script exit status %#x", sts)
				return
			# Child
			try:
				try:
					os.setuid(nobody)
				except os.error:
					pass
				os.dup2(self.rfile.fileno(), 0)
				os.dup2(self.wfile.fileno(), 1)
				
				if( ispy ):
					os.execve(scriptfile, args, os.environ)
				elif( isphp ):
					cmdline = "%s %s" % (self.exe_php, scriptfile)
					os.execve(cmdline, args, os.environ)
			except:
				self.server.handle_error(self.request, self.client_address)
				os._exit(127)

		elif self.have_popen2 or self.have_popen3:
			# Windows -- use popen2 or popen3 to create a subprocess
			import shutil
			if self.have_popen3:
				popenx = os.popen3
			else:
				popenx = os.popen2
			cmdline = scriptfile
			if self.is_python(scriptfile):
				interp = sys.executable
				if interp.lower().endswith("w.exe"):
					# On Windows, use python.exe, not pythonw.exe
					interp = interp[:-5] + interp[-4:]
				
				# if current dir have blank char there where be a error
				#
				if( " " in interp ):
					cmdline = '"%s" -u %s' % (interp, cmdline)
				else:
					cmdline = "%s -u %s" % (interp, cmdline)
				
			# split script path
			l_path = os.path.split(scriptfile)	
			c_path = os.getcwd()
			
			# if script is php
			if( isphp ):
				#cmdline = "%s %s" % ( self.exe_php, l_path[1])
				cmdline = "%s %s" % ( self.exe_php, scriptfile)
				
			if '=' not in query and '"' not in query:
				cmdline = '%s "%s"' % (cmdline, query)
			self.log_message("command: %s", cmdline)
			try:
				nbytes = int(length)
			except (TypeError, ValueError):
				nbytes = 0
			
			#if( isphp):
			#	os.chdir(l_path[0])
			
			#print "cmdline: %s" % cmdline	
			files = popenx(cmdline, 'b')
			
			fi = files[0]
			fo = files[1]
			if self.have_popen3:
				fe = files[2]
			if self.command.lower() == "post" and nbytes > 0:
				data = self.rfile.read(nbytes)
				fi.write(data)
			# throw away additional data [see bug #427345]
			while select.select([self.rfile._sock], [], [], 0)[0]:
				if not self.rfile._sock.recv(1):
					break
			fi.close()
			shutil.copyfileobj(fo, self.wfile)
			if self.have_popen3:
				errors = fe.read()
				fe.close()
				if errors:
					self.log_error('%s', errors)
			sts = fo.close()
			if sts:
				self.log_error("CGI script exit status %#x", sts)
			else:
				self.log_message("CGI script exited OK")

		else:
			# Other O.S. -- execute script in this process
			save_argv = sys.argv
			save_stdin = sys.stdin
			save_stdout = sys.stdout
			save_stderr = sys.stderr
			try:
				try:
					sys.argv = [scriptfile]
					if '=' not in decoded_query:
						sys.argv.append(decoded_query)
					sys.stdout = self.wfile
					sys.stdin = self.rfile
					execfile(scriptfile, {"__name__": "__main__"})
				finally:
					sys.argv = save_argv
					sys.stdin = save_stdin
					sys.stdout = save_stdout
					sys.stderr = save_stderr
			except SystemExit, sts:
				self.log_error("CGI script exit status %s", str(sts))
			else:
				self.log_message("CGI script exited OK")
		

def run_httpd(HandlerClass = T_CGIHTTPRequestHandler,
		 ServerClass = BaseHTTPServer.HTTPServer):
	"""Test the HTTP request handler class.

	This runs an HTTP server on port 8000 (or the first command line
	argument).

	"""
	
	protocol = "HTTP/1.0"

	if sys.argv[1:]:
		port = int(sys.argv[1])
	else:
		port = 80
	server_address = ('', port)

	HandlerClass.protocol_version = protocol
	httpd = ServerClass(server_address, HandlerClass)
	HandlerClass.httpd = httpd

	sa = httpd.socket.getsockname()
	print "Serving HTTP on", sa[0], "port", sa[1], "..."
	httpd.serve_forever()

def run():
	# begin the db server process
	db.StartDBServer()
	
	try:
		import webbrowser 
		
		if sys.argv[1:]:
			port = int(sys.argv[1])
			s = "http://localhost:%d/" % port
		else:
			port = 80
			s = "http://localhost/"
		
		webbrowser.open(s)
	except:
		print "ERR: failed to open webbrowser!"

	# begin the http & cgi server
	run_httpd()
	

if __name__ == '__main__':
	run()
	