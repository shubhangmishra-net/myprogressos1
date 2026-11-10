from pathlib import Path
import base64
import gzip

BASE_DIR = Path(__file__).resolve().parent
encoded_source = (BASE_DIR / 'app_source.py.gz.b64').read_text(encoding='ascii')
source = gzip.decompress(base64.b64decode(encoded_source)).decode('utf-8')
exec(compile(source, str(BASE_DIR / 'planner_source.py'), 'exec'), globals())
