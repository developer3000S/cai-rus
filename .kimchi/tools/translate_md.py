#!/usr/bin/env python3
"""Translate remaining markdown files to Russian via local Ollama gemma4."""
import json
import os
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path("/root/soft/cairus")
LIST_FILE = ROOT / "md_english_files.txt"
LOG_FILE = ROOT / ".kimchi/docs/translation-log.md"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:31b-cloud"
MIN_CYR_RATIO = 0.30
MIN_CYR_CHARS = 1000

def cyr_ratio(text: str) -> float:
    total = len(text)
    if total == 0:
        return 0.0, 0
    cyr = sum(1 for ch in text if "\u0400" <= ch <= "\u04FF")
    return cyr / total, cyr

def ollama_translate(text: str) -> str:
    system = (
        "Translate the following Markdown document from English to Russian. "
        "Preserve all Markdown syntax, code blocks, inline code, shell commands, "
        "file paths, URLs, variable names, badge URLs, and Mako/Jinja template syntax "
        "(`<% ... %>`, `${...}`). Translate only natural language prose such as "
        "headings, paragraphs, list items, and descriptions. Do not translate code, "
        "commands, identifiers, or literal values. Output only the translated document "
        "content, without any additional commentary. Do not wrap the whole output in "
        "triple backticks."
    )
    prompt = f"{system}\n\n---START OF DOCUMENT---\n{text}\n---END OF DOCUMENT---"
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_ctx": 131072, "temperature": 0.1},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result.get("response", "").strip()

def clean_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        # Remove first fenced code block wrapper if it wraps the whole content.
        lines = text.splitlines()
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text

def translate_file(path: Path, log_lines: list) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    ratio, cyr = cyr_ratio(text)
    if ratio >= MIN_CYR_RATIO and cyr >= MIN_CYR_CHARS:
        log_lines.append(f"- SKIP `{path}` (cyr ratio {ratio:.2%}, chars {cyr})")
        return "skipped"
    for attempt in range(1, 4):
        try:
            translated = ollama_translate(text)
            translated = clean_response(translated)
            if not translated:
                raise ValueError("empty response")
            ratio2, cyr2 = cyr_ratio(translated)
            if cyr2 < max(100, len(translated) * 0.05):
                raise ValueError(f"too few cyrillic chars ({cyr2})")
            path.write_text(translated, encoding="utf-8")
            log_lines.append(
                f"- OK `{path}` (attempt {attempt}, cyr {cyr2}, ratio {ratio2:.2%})"
            )
            return "translated"
        except Exception as e:
            log_lines.append(f"- ATTEMPT {attempt} FAIL `{path}`: {e}")
            time.sleep(2)
    log_lines.append(f"- FAIL `{path}`")
    return "failed"

def main():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LIST_FILE.exists():
        print(f"List file {LIST_FILE} not found")
        return
    files = [
        line.strip()
        for line in LIST_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    log_lines = [f"# Translation log ({time.strftime('%Y-%m-%d %H:%M:%S')})", ""]
    counts = {"translated": 0, "skipped": 0, "failed": 0, "missing": 0}
    # Test Ollama availability once.
    try:
        urllib.request.urlopen(OLLAMA_URL.replace("/api/generate", "/api/tags"), timeout=10).read()
    except Exception as e:
        log_lines.append(f"ERROR: Ollama unreachable: {e}")
        LOG_FILE.write_text("\n".join(log_lines), encoding="utf-8")
        print("Ollama unreachable")
        return
    for idx, rel in enumerate(files, 1):
        path = ROOT / rel
        if not path.exists():
            log_lines.append(f"- MISSING `{rel}`")
            counts["missing"] += 1
            continue
        print(f"[{idx}/{len(files)}] {rel} ...")
        status = translate_file(path, log_lines)
        counts[status] += 1
    log_lines.append("")
    log_lines.append(f"Summary: {counts}")
    LOG_FILE.write_text("\n".join(log_lines), encoding="utf-8")
    print("Done", counts)

if __name__ == "__main__":
    main()
