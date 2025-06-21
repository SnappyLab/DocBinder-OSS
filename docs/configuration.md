# Configuration

DocBinder OSS supports configuration via YAML files or CLI options.

## Providers

DocBinder OSS supports multiple cloud storage providers. Currently supported:

- Google Drive
- Dropbox

## Adding a Provider

YAML Configuration Example

```yaml
providers:
  - type: google_drive
    name: my_google_drive
    gcp_credentials_json: gcp_credentials.json
  - type: dropbox
    name: my_dropbox
    api_key: dropbox-api-key
```

Configure using the CLI:

```sh
docbinder setup --file path/to/config.yaml
docbinder setup --provider "google_drive:key1=val1,key2=val2"
```

## Extending Providers

DocBinder OSS is designed to be extensible. You can add new providers by implementing the required interfaces in the `src/docbinder_oss/services/` directory.

