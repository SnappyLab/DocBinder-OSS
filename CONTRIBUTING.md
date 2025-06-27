# Contributing to DocBinder OSS

Thank you for your interest in contributing! Please follow these guidelines:

- Fork the repository and create your branch from `dev`.
- Write clear, concise commit messages.
- Add tests for new features or bug fixes.
- Ensure all tests pass before submitting a pull request.
- Follow the code style used in the project.
- For major changes, open an issue first to discuss what you would like to change.

## Pull Request Process
1. Ensure your branch is up to date with `dev`.
2. Submit your pull request and fill out the PR template.
3. One or more maintainers will review your code.
4. Address any feedback and update your PR as needed.

Thank you for helping make DocBinder OSS better!

# Local Development
## Managing Dependencies and Environment with `uv`

This project uses [`uv`](https://github.com/astral-sh/uv) for dependency management and environment setup. We do **not** use `requirements.txt`, all dependency management is handled natively by `uv`.

### Setting Up the Environment

To create a virtual environment and install dependencies:

```zsh
uv venv
source .venv/bin/activate
uv sync
```

### Adding or Updating a Dependency

To add or update a package (e.g., `docbinder-oss`):

```zsh
uv add docbinder-oss
```

### Upgrading All Dependencies

To upgrade all dependencies to their latest compatible versions:

```zsh
uv version docbinder-oss --bump minor
uv sync
```

### Generating or Updating `pyproject.toml`

All dependencies are tracked in `pyproject.toml`. Use `uv` commands to keep it up to date.

---

**Note:**  
Always use `uv` commands to manage dependencies and environments to keep `pyproject.toml` in sync.

## Code Style and Linting

This project uses [Black](https://black.readthedocs.io/en/stable/) for code formatting and [Ruff](https://docs.astral.sh/ruff/) for linting. All code should be formatted and linted before committing.

- Run the following before committing code:

```zsh
uv run black .
uv run ruff check .
```

- To automatically format and lint code on every commit, install pre-commit hooks:

```zsh
uv pip install pre-commit
pre-commit install
```

This will ensure Black and Ruff are run on staged files before each commit.

Configuration for Black and Ruff is in `pyproject.toml`. This enforces consistent quotes, spacing, and other style rules for all contributors.