# Main CLI Commands

This page documents the top-level commands available in the DocBinder OSS CLI.

---

## `docbinder hello`
**Description:** Print a friendly greeting.

**Usage:**
```sh
docbinder hello
```

---

## `docbinder setup`
**Description:** Setup DocBinder configuration via YAML file or provider key-value pairs.

**Options:**
- `--file <path>`: Path to YAML config file
- `--provider <provider:key1=val1,key2=val2>`: Provider config as key-value pairs (can be repeated)

**Usage:**
```sh
docbinder setup --file path/to/config.yaml
docbinder setup --provider "google_drive:key1=val1,key2=val2"
```

---

For provider-related commands, see [Provider Commands](provider.md).
