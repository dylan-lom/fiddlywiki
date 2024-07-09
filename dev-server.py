import sys
import os
import time

import http.server
import socketserver
from http import HTTPStatus

SOURCE_WIKI = 'index.html'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

wikis = {}

class Handler(http.server.SimpleHTTPRequestHandler):
	def do_POST(self):
		self.log_request()

		mtime = wikis[self.path][1] if self.path in wikis else time.time()
		length = int(self.headers.get('Content-Length'))
		wikis[self.path] = (self.rfile.read(length), mtime)
		self.send_response(HTTPStatus.OK)
		self.end_headers()

	def do_HEAD(self):
		with open('index.html', 'rb') as fp:
			source_mtime = os.fstat(fp.fileno()).st_mtime
			if self.path not in wikis or wikis[self.path][1] < source_mtime:
				wikis[self.path] = (fp.read(), source_mtime)

		self.send_response(HTTPStatus.OK)
		self.send_header('Content-Type', 'text/html')
		self.send_header('Content-Length', len(wikis[self.path][0]))
		self.end_headers()

	def do_GET(self):
		self.do_HEAD()
		self.wfile.write(wikis[self.path][0])

with socketserver.TCPServer(("", PORT), Handler) as httpd:
	print(f"serving on port: {PORT}")
	httpd.serve_forever()

