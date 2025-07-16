# Project Agents.md Guide for OpenAI Codex

This Agents.md file provides guidance for OpenAI Codex and other AI agents working with this Python-based stock signal project.

## Project Structure for OpenAI Codex Navigation

- Root Python modules: `app.py`, `data.py`, `indicators.py`, `scrape.py`, `signals.py`, etc.
- `/tests`: Unit tests that Codex should maintain and extend.
- `config.yaml`: Configuration options used by the app.

## Coding Conventions for OpenAI Codex

- Use Python 3.11 features and type hints for all new code.
- Follow PEP 8 style and keep functions small and focused.
- Include meaningful variable and function names.
- Add docstrings and inline comments for complex logic.

## Testing Requirements for OpenAI Codex

Run unit tests before creating a pull request:

```bash
python3 -m unittest
```

All tests must pass.

## Pull Request Guidelines for OpenAI Codex

1. Provide a clear description of the changes.
2. Reference any related issues or tasks.
3. Ensure tests pass.
4. Keep PRs focused on a single concern.

## Programmatic Checks for OpenAI Codex

This repository does not include lint or type-check scripts, but tests should be run as above. The development environment lacks internet access, so ensure dependencies are installed locally via `setup.sh`.
