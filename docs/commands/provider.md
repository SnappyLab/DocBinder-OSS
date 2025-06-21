# Provider Commands

These commands are available under the `docbinder provider` group.

---

## `docbinder provider list`
**Description:** List all configured providers.

**Usage:**
```sh
docbinder provider list
```

---

## `docbinder provider get`
**Description:** Get connection information for a specific provider.

**Options:**
- `--type, -t <type>`: The type of the provider to get
- `--name, -n <name>`: The name of the provider to get

**Usage:**
```sh
docbinder provider get --name google_drive
docbinder provider get --type dropbox
```

---

## `docbinder provider test <name>`
**Description:** Test the connection to a specific provider by name.

**Usage:**
```sh
docbinder provider test google_drive
```

---

For top-level commands, see [Main CLI Commands](main.md).
