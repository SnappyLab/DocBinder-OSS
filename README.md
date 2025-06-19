# DocBinder OSS

DocBinder OSS is a Python library and CLI tool that provides unified access to multiple cloud storage providers, such as Google Drive and Dropbox. Its goal is to simplify file management and automation across different storage backends with a consistent interface.


## Features

- Unified API for multiple storage providers
- Easy configuration via YAML or CLI
- Extensible provider system
- Command-line interface for common operations

## Installation

You can install DocBinder OSS using pip:

```sh
pip install docbinder-oss
```

## Usage

### CLI

After installation, you can use the `docbinder-oss` CLI:

```sh
docbinder --help
```

### Setup Configuration

You can configure providers using a YAML file:

```sh
docbinder setup --file path/to/config.yaml
```

Or directly via CLI options:

```sh
docbinder setup --provider "google_drive:key1=val1,key2=val2"
```

### List Providers

```sh
docbinder provider list
```

### Get Provider Details

```sh
docbinder procider get --name google_drive
```

### Test Provider Connection

```sh
docbinder provider test google_drive
```

# Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development and contribution guidelines.

## Local Development Setup

This project uses `[uv](https://github.com/astral-sh/uv)` for dependency management:

```sh
uv sync
```

# Contributing

We welcome contributions! Please read our [Code of Conduct](CODE_OF_CONDUCT.md) and [Contributing Guide](CONTRIBUTING.md) before submitting a pull request.

* Fork the repository and create your branch from main.
* Add tests for new features or bug fixes.
* Ensure all tests pass before submitting a pull request.

# License
This project is licensed under the [Apache-2.0 License](LICENSE).

# Security
If you discover a security vulnerability, please see [SECURITY](SECURITY.md) for responsible disclosure guidelines.

___

DocBinder OSS is an open-source project—your feedback and contributions are appreciated! :rocket: