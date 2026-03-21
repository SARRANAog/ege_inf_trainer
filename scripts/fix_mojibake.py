from pathlib import Path

FILES = [
    'backend/server.py',
    'backend/theory_content.py',
    'backend/content_data.py',
    'backend/roadmap_content.py',
    'backend/exercises_content.py',
    'backend/exercises_extra.py',
    'backend/exercises_extra_2.py',
]
MARKERS = ('Ð', 'Ñ', 'â€“', 'â€”', 'â€œ', 'â€', 'â„', 'Ã', 'Р', 'С')

def looks_broken(text: str) -> bool:
    return any(marker in text for marker in MARKERS)

def repair_once(text: str) -> str:
    return text.encode('latin1').decode('utf-8')

def repair_text(text: str) -> str:
    current = text
    for _ in range(3):
        if not looks_broken(current):
            break
        try:
            fixed = repair_once(current)
        except Exception:
            break
        if fixed == current:
            break
        current = fixed
    return current

fixed_any = False
for rel in FILES:
    path = Path(rel)
    if not path.exists():
        print(f'SKIP {rel} (not found)')
        continue
    original = path.read_text(encoding='utf-8-sig')
    repaired = repair_text(original)
    if repaired != original:
        path.write_text(repaired, encoding='utf-8')
        fixed_any = True
        print(f'FIXED {rel}')
    else:
        print(f'OK {rel}')

print('DONE', 'CHANGED' if fixed_any else 'NO_CHANGES')
