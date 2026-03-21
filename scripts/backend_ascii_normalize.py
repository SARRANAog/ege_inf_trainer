from pathlib import Path
import re

root = Path("backend")
files = [
    p for p in root.rglob("*.py")
    if ".venv" not in p.parts and "__pycache__" not in p.parts
]

coding_re = re.compile(r"(?im)^#.*coding[:=]\s*[-\w.]+.*\n?")

for path in files:
    text = path.read_text(encoding="utf-8-sig")
    text = coding_re.sub("", text, count=1)

    # Делаем файл ASCII-only: все не-ASCII символы превращаем в \uXXXX
    ascii_text = text.encode("ascii", "backslashreplace").decode("ascii")

    # Нормализуем переводы строк
    ascii_text = ascii_text.replace("\r\n", "\n").replace("\r", "\n")

    path.write_text(ascii_text, encoding="ascii", newline="\n")
    print(f"normalized: {path}")

print("DONE")
