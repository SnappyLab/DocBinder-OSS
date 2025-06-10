# Contributing to DocBinder OSS

Thank you for your interest in contributing! Please follow these guidelines:

- Fork the repository and create your branch from `main`.
- Write clear, concise commit messages.
- Add tests for new features or bug fixes.
- Ensure all tests pass before submitting a pull request.
- Follow the code style used in the project.
- For major changes, open an issue first to discuss what you would like to change.

## Pull Request Process
1. Ensure your branch is up to date with `main`.
2. Submit your pull request and fill out the PR template.
3. One or more maintainers will review your code.
4. Address any feedback and update your PR as needed.

Thank you for helping make DocBinder OSS better!

# Local Development
## Managing Dependencies and Environment with `uv`

This project uses [`uv`](https://github.com/astral-sh/uv) for dependency management and environment setup.

### Setting Up the Environment

To create a virtual environment and install dependencies:

```zsh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Adding or Updating a Dependency

To add or update a package (e.g., `docbinder-oss`) and update `requirements.txt`:

```zsh
uv pip install docbinder-oss --upgrade --system --sync
```

### Exporting Current Environment

To export your current environment to `requirements.txt`:

```zsh
uv pip freeze > requirements.txt
```

### Generating or Updating `pyproject.toml`

To generate or update `pyproject.toml` with your current dependencies:

```zsh
uv pip compile --generate pyproject.toml
```

---

**Note:**  
Always use `uv` commands to manage dependencies and environments to keep `requirements.txt` and `pyproject.toml` in sync.