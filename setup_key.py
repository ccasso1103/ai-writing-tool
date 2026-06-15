import sys, pathlib
key = sys.argv[1].strip()
path = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"
path.write_text(f'GEMINI_API_KEY = "{key}"\n', encoding="utf-8")
print(f"保存完了: {key[:8]}...")
