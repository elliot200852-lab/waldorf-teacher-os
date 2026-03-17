# Google Workspace CLI (gws) Reference for Windows

A concise guide for using the `gws` CLI tool on Windows.

## 🚀 Installation & Execution

You can run the CLI directly using `npx` (no installation required) or install it globally via `npm`.

### Run via npx (Recommended for one-off use)
```powershell
npx -y @googleworkspace/cli <command>
```

### Install Globally
```powershell
npm install -g @googleworkspace/cli
```

---

## 🔐 Authentication

### Initial Setup
If you have the `gcloud` CLI installed, run:
```powershell
gws auth setup
```
This will guide you through creating a Google Cloud project and configuring credentials.

### Manual Setup (Without gcloud)
1.  Create an **OAuth Client ID** (Type: Desktop App) in the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2.  Download the JSON client secret.
3.  Save it to: `C:\Users\<YourUser>\.config\gws\client_secret.json`
4.  Run `gws auth login`.

### Subsequent Login
```powershell
gws auth login
```
*Tip: If you get "Access blocked", ensure your email is added as a **Test User** in the OAuth Consent Screen.*

---

## 📂 Common Commands

### Google Drive
*   **List files:** `gws drive files list`
*   **List top 5 files:** `gws drive files list --params '{"pageSize": 5}'`
*   **Upload a file:** `gws drive +upload .\report.pdf --name "Project Report"`
*   **Create a folder:** `gws drive files create --json '{"name": "New Folder", "mimeType": "application/vnd.google-apps.folder"}'`

### Google Sheets
*   **Create a spreadsheet:** `gws sheets spreadsheets create --json '{"properties": {"title": "New Sheet"}}'`
*   **Append a row:** `gws sheets +append --spreadsheet <ID> --values "Name,Score,Date"`
*   **Read range:** `gws sheets +read --spreadsheet <ID> --range "Sheet1!A1:B10"`

### Calendar & Gmail
*   **Show today's agenda:** `gws calendar +agenda`
*   **Send an email:** `gws gmail +send --to user@example.com --subject "Hello" --body "Message body"`
*   **List recent emails:** `gws gmail users messages list`

---

## ✨ Helper Commands (Easy mode)
Commands starting with `+` are simplified versions of complex API calls:
- `gws drive +upload`
- `gws sheets +append` / `gws sheets +read`
- `gws gmail +send` / `gws gmail +reply`
- `gws calendar +agenda` / `gws calendar +insert`
- `gws workflow +standup-report`

---

## 🛠️ Performance & Debugging Flags

| Flag | Description |
| :--- | :--- |
| `--help` | Detailed documentation for any command (e.g., `gws drive --help`) |
| `--dry-run` | See the exact API request/URL without executing it |
| `--page-all` | Automatically fetch all pages for list commands |
| `--json` | Pass the request body as a JSON string |
| `gws schema <svc>.<method>` | View the Discovery API schema for a specific method |

---

## 📝 Windows Tips
*   **Path Formatting:** Use backslashes (`.\path\to\file`) for local files.
*   **JSON quoting in PowerShell:** If passing complex JSON via `--json`, use single quotes for the parameter and escape double quotes inside if necessary, or use a here-string.
    *   Example: `gws drive files create --json '{"name": "Test"}'`
*   **Shell Escaping:** When using range strings with `!` (e.g., `Sheet1!A1`), PowerShell generally handles this fine, but if you have issues, wrap the whole string in single quotes.
