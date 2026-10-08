"""Prepare browser JPEGs in an explicitly authorized processing directory."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
root=Path(sys.argv[1]).resolve()
manifest=json.loads((root/'textures-interior/manifest.json').read_text(encoding='utf-8'))
dest=root/'textures-browser';dest.mkdir(exist_ok=True)
for item in manifest['images']:
 source=root/'textures-interior'/item['name']
 with source.open('rb') as stream:
  assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256'],item['name']
 with Image.open(source) as im:
  im.draft('RGB',(4096,4096))
  im.thumbnail((4096,4096),Image.Resampling.LANCZOS)
  im.convert('RGB').save(dest/item['name'],quality=90,optimize=True)
print('Prepared',len(manifest['images']),'browser textures')
