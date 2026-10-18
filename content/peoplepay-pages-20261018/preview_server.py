from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
import mimetypes,requests
P=Path(__file__).resolve().parent/'preview'
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  path=urlsplit(self.path).path
  if path=='/' or path.startswith('/blog/peoplepay-'):f=P/'index.html'
  else:f=(P/path.lstrip('/')).resolve()
  if not f.is_relative_to(P.resolve()):self.send_error(403);return
  if f.is_file():
   data=f.read_bytes();kind=mimetypes.guess_type(f.name)[0] or 'application/octet-stream'
  elif path.startswith(('/assets/','/fonts/','/images/')):
   try:
    r=requests.get('https://ne-prosto.ru'+self.path,timeout=25);r.raise_for_status();data=r.content;kind=r.headers.get('Content-Type','application/octet-stream')
   except Exception:self.send_error(404);return
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('X-Robots-Tag','noindex,nofollow');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
 def log_message(self,*a):pass
ThreadingHTTPServer(('127.0.0.1',8773),H).serve_forever()
