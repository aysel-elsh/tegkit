# Contributing to tegkit

Thanks for helping! Students, hobbyists and researchers are all welcome.

New to open source? Start with [docs/FIRST_PR.md](docs/FIRST_PR.md), a step-by-step guide to your first pull request.

## Getting set up

```bash
git clone https://github.com/<you>/tegkit
cd tegkit
pip install -e '.[dev]'
pytest
```

## Making a change

1. Pick an issue (or open one first for bigger ideas) and comment that you're on it.
2. Create a branch, make your change, and add or update a test in `tests/`.
3. Run `pytest`. Everything should pass.
4. Open a pull request that says what changed and why. Cite a source for any physics.

## Good first contributions

- Add a preset for a real module from its public datasheet
- Add an example or notebook
- Improve docstrings, or fix a unit or typo
- Add input validation for an edge case

## Ground rules

- Keep the core dependency-free (standard library only).
- SI units everywhere: V, A, ohm, W, K, W/K, K/W.
- Be kind. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
