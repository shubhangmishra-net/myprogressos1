from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
parts = sorted(BASE_DIR.glob('app_src_*.txt'))
if not parts:
    raise RuntimeError('Planner source files are missing.')
source = ''.join(part.read_text(encoding='utf-8') for part in parts)
exec(compile(source, str(BASE_DIR / 'planner_source.py'), 'exec'), globals())
