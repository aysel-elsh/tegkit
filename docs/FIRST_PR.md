# Your first open-source pull request

This guide walks you through making a real contribution to tegkit, a Python library for
modelling thermoelectric generators and Peltier coolers. No open-source experience needed.
It takes about an hour.

## What you need

- A free GitHub account
- Python 3.10 or newer
- Git, or just a web browser for small changes (see the shortcut at the end)

## 1. Pick an issue

1. Open the [good first issues](https://github.com/aysel-elsh/tegkit/issues?q=is%3Aopen+label%3A%22good+first+issue%22+no%3Aassignee).
2. Choose one nobody has claimed yet, and read the whole issue.
3. Comment **"I'd like to take this"**. Wait for the maintainer to assign it to you, so two
   people don't do the same work.

One issue per person at a time.

## 2. Get the code

1. Click **Fork** at the top of the [tegkit repo](https://github.com/aysel-elsh/tegkit).
   This makes your own copy.
2. Download your copy and set it up:

```bash
git clone https://github.com/YOUR-USERNAME/tegkit
cd tegkit
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
pytest                           # everything should pass before you start
```

3. Make a branch named after your change:

```bash
git checkout -b fix-array-validation
```

## 3. Make the change

- Keep it to what the issue asks. Small pull requests get merged faster.
- Add or update a test in `tests/` that would fail without your change.
- Run `pytest` again. Everything must pass.
- tegkit uses only the Python standard library, and SI units everywhere (V, A, ohm, W, K).

## 4. Send it

```bash
git add .
git commit -m "Reject non-integer series/parallel in TEGArray"
git push origin fix-array-validation
```

Then open your fork on GitHub and click **Compare & pull request**. In the description:

- Write `Closes #12` (your issue number), so the issue closes when it's merged.
- Say what you changed and how you tested it.
- If you used an AI tool, say so. That's fine, as long as you understand every line and can
  answer questions about it.

## 5. Review

The maintainer will read your pull request and may ask for changes. That's normal, and it's
how everyone learns. Push more commits to the same branch and they'll show up in the pull
request automatically. Once it's approved and merged, you're an open-source contributor.

## Shortcut for small changes (no Git needed)

For documentation or single-file fixes, you can do everything in the browser:

1. Open the file on GitHub and click the pencil icon.
2. Make your edit.
3. Click **Commit changes**, then **Propose changes**. GitHub creates the fork and branch for you.
4. Click **Create pull request** and write the description as in step 4.

## Stuck?

Comment on your issue with what you tried and what happened. Asking is part of the process.
