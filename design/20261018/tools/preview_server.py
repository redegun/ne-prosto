from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlsplit
import json
R=Path(__file__).resolve().parent.parent
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  path=urlsplit(path).path
  if path.startswith('/_design/'):return str(R/'assets'/Path(path).name)
  routes=json.loads((R/'preview/routes.json').read_text())
  return str(R/'preview'/routes.get(path,'missing.html'))
 def end_headers(self):
  self.send_header('Cache-Control','no-store');super().end_headers()
ThreadingHTTPServer(('127.0.0.1',8767),Handler).serve_forever()
