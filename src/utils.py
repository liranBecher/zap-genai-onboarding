from pathlib import Path
import json


INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")


def ensure_output_dir() -> None:
	OUTPUT_DIR.mkdir(exist_ok=True)


def load_input_files() -> list[dict]:
	files = list(INPUT_DIR.glob("*"))
	assets = []

	for file_path in files:
		if file_path.is_file():
			try:
				content = file_path.read_text(encoding="utf-8")
			except UnicodeDecodeError:
				content = file_path.read_text(encoding="utf-8", errors="ignore")

			assets.append({
				"source_name": file_path.name,
				"content": content,
			})

	return assets


def save_json(filename: str, data) -> None:
	output_path = OUTPUT_DIR / filename
	with open(output_path, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)


def save_markdown(filename: str, content: str) -> None:
	output_path = OUTPUT_DIR / filename
	output_path.write_text(content, encoding="utf-8")
