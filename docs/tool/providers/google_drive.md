# Google Drive Configuration Setup

This guide will help you configure Google Drive as a provider for DocBinder.

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- DocBinder installed

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on **Select a project** and then **New Project**.
3. Enter a project name and click **Create**.

## Step 2: Enable Google Drive API

1. In your project dashboard, navigate to **APIs & Services > Library**.
2. Search for **Google Drive API**.
3. Click **Enable**.

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**.
2. Click **+ CREATE CREDENTIALS** and select **OAuth client ID**.
3. Configure the consent screen if prompted.
4. Choose **Desktop app** or **Web application** as the application type.
5. Enter a name and click **Create**.
6. Download the `credentials.json` file.

## Step 4: Configure DocBinder

1. Place your downloaded credentials file somewhere accessible (e.g., ~/gcp_credentials.json).
2. The application will generate a token file (e.g., ~/gcp_token.json) after the first authentication.
   
## Step 5: Edit the Config File

Create the config file, and add a provider entry for Google Drive:
```yaml
providers:
  - type: google_drive
    name: my_gdrive
    gcp_credentials_json: ./gcp_credentials.json
    gcp_token_json: ./gcp_token.json
```

* type: Must be google_drive.
* name: A unique name for this provider.
* gcp_credentials_json: Absolute/relative path to your Google Cloud credentials file.
* gcp_token_json: Absolute/relative path where the token will be stored/generated.

## Step 6: Authenticate and Test

1. Run DocBinder with the Google Drive provider enabled.
2. On first run, follow the authentication prompt to grant access.
3. Verify that DocBinder can access your Google Drive files.

## Troubleshooting

- Ensure your credentials file is in the correct location.
- Check that the Google Drive API is enabled for your project.
- Review the [Google API Console](https://console.developers.google.com/) for error messages.

## References

- [Google Drive API Documentation](https://developers.google.com/drive)
- [DocBinder OSS - GitHub](https://github.com/SnappyLab/DocBinder-OSS)