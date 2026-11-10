from pathlib import Path
import base64
import gzip

BASE_DIR = Path(__file__).resolve().parent
segments = [BASE_DIR / f'app_source_{index:02d}.b64' for index in (1, 2, 3)]
encoded_source = ''.join(part.read_text(encoding='ascii').strip() for part in segments)
source = gzip.decompress(base64.b64decode(encoded_source)).decode('utf-8')
exec(compile(source, str(BASE_DIR / 'planner_source.py'), 'exec'), globals())
