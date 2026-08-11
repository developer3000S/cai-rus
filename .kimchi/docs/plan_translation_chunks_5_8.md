# Plan: Project Translation to Russian (Chunks 5-8)

## Goal
Complete the translation of the CAI project into Russian, focusing on tools, prompts, README, examples, and documentation.

## Constraints
- **DO NOT** translate: code (variable names, function names, class names), shell commands, environment variable names (e.g., `CAI_MODEL`), file paths, URLs, product names, technical terms (API, CLI, LLM, SSH, CTF, PCAP, GUI, REPL, JSON, XML, HTML, HTTP, HTTPS, DNS, TCP, IP, PTY, FIFO), or specific command-line flags.
- **DO** translate: docstrings, comments, user-facing strings (`print`, `raise`, `logging`), markdown content, tool descriptions.
- Ensure consistent terminology.
- Preserve all markdown formatting, links, and structure.
- Maintain technical accuracy.

## Implementation Chunks

### Chunk 5: Executor, Container, and Network Tools
- **Files**:
    - `src/cai/tools/executor.py`
    - `src/cai/tools/container.py`
    - `src/cai/tools/network/capture_traffic.py`
- **Task**: Translate all remaining English strings in docstrings, comments, and user-facing output.
- **Verification**: `ruff check src/cai`, ensure no syntax errors.

### Chunk 6: Prompt Templates and Tool Descriptions
- **Files**:
    - `src/cai/prompts/core/*.md`
    - `src/cai/prompts/micro/*.md`
    - `src/cai/prompts/*.md` (top level)
- **Task**: Translate all markdown content into Russian. Keep "IMPORTANT: Answer only in Russian language" and similar technical instructions if required by the system.
- **Verification**: Check for missing translations using `grep`.

### Chunk 7: README.md
- **Files**:
    - `README.md`
- **Task**: Bring the main README to full Russian, ensuring all sections are translated.
- **Verification**: Visual review.

### Chunk 8: Examples and Documentation
- **Files**:
    - `docs/**/*.md`
    - `examples/**/*.md`
    - Other `README.md` files (e.g., in `tests/`, `benchmarks/`, `src/cai/tui/`).
- **Task**: Translate all markdown content.
- **Sub-chunks**:
    - 8.1: `docs/cai/**/*.md`
    - 8.2: `docs/tui/**/*.md` and `docs/mui/**/*.md`
    - 8.3: `docs/benchmarking/**/*.md`, `docs/providers/**/*.md`, `docs/voice/**/*.md`, `docs/other_cli/**/*.md`
    - 8.4: General `docs/*.md` and `docs/ref/**/*.md`
    - 8.5: `examples/**/*.md`
    - 8.6: Remaining `README.md` files.
- **Verification**: `mkdocs build` (if possible) or manual check of links.

## Final Verification
- Run `ruff check src/cai tests`.
- Run `pytest tests/ -x --timeout 30`.
- Confirm that no critical regressions were introduced by translation (e.g., broken tests expecting specific English output).

## Decision Log
- Decided to use Builder agents for translation to ensure high quality and consistency across many files.
- Decided to group files by directory/function to avoid overloading agents.
