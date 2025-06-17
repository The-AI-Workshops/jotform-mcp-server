[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/the-ai-workshops-jotform-mcp-server-badge.png)](https://mseep.ai/app/the-ai-workshops-jotform-mcp-server)
[![Verified on MseeP](https://mseep.ai/badge.svg)](https://mseep.ai/app/ee46503f-99e6-49d7-9427-9703a1672779)

# JotForm API - Python Client & MCP Server

[![smithery badge](https://smithery.ai/badge/@The-AI-Workshops/jotform-mcp-server)](https://smithery.ai/server/@The-AI-Workshops/jotform-mcp-server)

This repository contains the Python client for the [JotForm API](https://api.jotform.com/docs/) and an MCP (Model Context Protocol) server built using this client. The MCP server allows interaction with the Jotform API through standardized tools.

### Installation via Smithery (Recommended for MCP Clients)

This server is available on Smithery. You can easily install and configure it within compatible MCP clients (like Windsurf):

1.  **Search:** In your MCP client's server management interface, search for servers.
2.  **Find:** Look for **`JotForm API Server`** or use the ID **`@The-AI-Workshops/jotform-mcp-server`**.
3.  **Install:** Select the server and click "Install".
4.  **Configure:** After installation, you will be prompted to configure the required environment variables. The most important one is:
    *   `JOTFORM_API_KEY`: Your Jotform API key.

Smithery handles the underlying setup (Docker or Python environment) based on the server's configuration.

### Authentication

JotForm API requires an API key for all user-related calls. You can create your API Keys at the [API section](https://www.jotform.com/myaccount/api) of your JotForm account settings. This key is needed to run the MCP server, whether installed manually or via Smithery.

### Manual Setup and Running (for Development or Non-Smithery Use)

### Installing via Smithery

To install JotForm API Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@The-AI-Workshops/jotform-mcp-server):

```bash
npx -y @smithery/cli install @The-AI-Workshops/jotform-mcp-server --client claude
```

**1. Clone the Repository:**

```bash
git clone https://github.com/The-AI-Workshops/jotform-mcp-server.git
cd jotform-mcp-server
```

**2. Create Virtual Environment (Recommended):**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

**3. Install Dependencies:**

Choose **one** of the following methods:

*   **Using `uv` (Recommended):**
    *   If you don't have `uv`, install it: `pip install uv`
    *   Install dependencies using the lock file for reproducibility:
        ```bash
        uv pip sync uv.lock
        ```

*   **Using `pip`:**
    *   Install dependencies using the `requirements.txt` file:
        ```bash
        pip install -r requirements.txt
        ```

**4. Configure API Key:**

*   Rename the `.env.example` file to `.env`.
*   Open the `.env` file and replace `"YOUR_JOTFORM_API_KEY_HERE"` with your actual Jotform API key.
*   You can also adjust other settings like `MCP_PORT` or `JOTFORM_BASE_URL` if needed.

```dotenv
# .env
JOTFORM_API_KEY="YOUR_ACTUAL_JOTFORM_API_KEY"
MCP_HOST="0.0.0.0"
MCP_PORT="8067"
MCP_TRANSPORT="sse"
JOTFORM_BASE_URL="https://api.jotform.com/"
JOTFORM_OUTPUT_TYPE="json"
JOTFORM_DEBUG_MODE="False"

# Custom Search Settings
ACCOUNTING_MONTH_START_DAY="1" # Day of the month the accounting period starts (e.g., 1, 15)
```

**5. Run the Server:**

Make sure your virtual environment is activated.

```bash
python jotform_mcp_server.py
```

The server will start, typically listening on `http://0.0.0.0:8067`. You can then connect to it using an MCP client. All public methods of the `JotformAPIClient` are exposed as tools.

### Running with Docker

A `Dockerfile` is provided for containerizing the MCP server.

**1. Build the Docker Image:**

Make sure you are in the project's root directory (where the `Dockerfile` is located).

```bash
docker build -t jotform-mcp-server .
```

**2. Run the Docker Container:**

You **must** provide your Jotform API key as an environment variable when running the container.

```bash
docker run -d -p 8067:8067 -e JOTFORM_API_KEY="YOUR_ACTUAL_JOTFORM_API_KEY" --name jotform-server jotform-mcp-server
```

*   `-d`: Run the container in detached mode (in the background).
*   `-p 8067:8067`: Map port 8067 on your host to port 8067 in the container.
*   `-e JOTFORM_API_KEY="..."`: **Crucially**, pass your API key here.
*   `--name jotform-server`: Assign a name to the container for easier management.
*   `jotform-mcp-server`: The name of the image you built.

The MCP server will be running inside the container and accessible on port 8067 of your host machine.

To view logs:
```bash
docker logs jotform-server
```

To stop the container:
```bash
docker stop jotform-server
```

To remove the container:
```bash
docker rm jotform-server
```

### Integration with MCP Clients

You can connect to this server using any MCP-compatible client (like Windsurf, Claude Desktop, n8n, etc.). Here are example configurations for different transport methods:

**SSE Configuration**

If you run the server directly (`python jotform_mcp_server.py`) or using Docker with port mapping (as shown above), you can connect via SSE. Ensure `TRANSPORT=sse` is set in your `.env` file or passed to the Docker container.

*Standard MCP Configuration:*
```json
{
  "mcpServers": {
    "jotform": {
      "transport": "sse",
      "url": "http://localhost:8067/sse"
    }
  }
}
```

*Windsurf Configuration:*
```json
{
  "mcpServers": {
    "jotform": {
      "transport": "sse",
      "serverUrl": "http://localhost:8067/sse"
    }
  }
}
```
*(Note: If connecting from another Docker container, like n8n, replace `localhost` with `host.docker.internal`)*

**Python with Stdio Configuration**

This allows the MCP client to manage the server process directly using your local Python environment. Replace `your/path/to/` with the actual absolute path to the project directory.

```json
{
  "mcpServers": {
    "jotform": {
      // Ensure this points to the python executable within the venv created by uv/pip
      "command": "your/path/to/jotform-mcp-server/venv/bin/python", // Use venv\Scripts\python.exe on Windows
      "args": ["your/path/to/jotform-mcp-server/jotform_mcp_server.py"],
      "env": {
        "TRANSPORT": "stdio",
        "JOTFORM_API_KEY": "YOUR_ACTUAL_JOTFORM_API_KEY",
        // Optional: Override other .env settings if needed
        "JOTFORM_BASE_URL": "https://api.jotform.com/",
        "JOTFORM_OUTPUT_TYPE": "json",
        "JOTFORM_DEBUG_MODE": "False"
      }
    }
  }
}
```

**Docker with Stdio Configuration**

This allows the MCP client to manage the server process running inside a Docker container. Ensure you have built the image (`docker build -t jotform-mcp-server .`).

```json
{
  "mcpServers": {
    "jotform": {
      "command": "docker",
      "args": ["run", "--rm", "-i",
               "-e", "TRANSPORT=stdio",
               "-e", "JOTFORM_API_KEY", // Will be inherited from the 'env' section below
               "-e", "JOTFORM_BASE_URL",
               "-e", "JOTFORM_OUTPUT_TYPE",
               "-e", "JOTFORM_DEBUG_MODE",
               "jotform-mcp-server:latest" // Use the image tag you built
              ],
      "env": {
        "TRANSPORT": "stdio", // Required by the server script
        "JOTFORM_API_KEY": "YOUR_ACTUAL_JOTFORM_API_KEY",
        // Optional: Override other defaults if needed
        "JOTFORM_BASE_URL": "https://api.jotform.com/",
        "JOTFORM_OUTPUT_TYPE": "json",
        "JOTFORM_DEBUG_MODE": "False"
      }
    }
  }
}
```

### Quick Run (npx-like)

If you want to run the server quickly without a full local setup (similar to how `npx` works for Node.js packages), you can combine the steps. This is useful for temporary execution or testing.

**Make sure you have Python 3.11+ and `git` installed.**

```bash
# 1. Clone the repository
git clone https://github.com/The-AI-Workshops/jotform-mcp-server.git
cd jotform-mcp-server

# 2. Create a temporary .env file with your API key
echo "JOTFORM_API_KEY=YOUR_ACTUAL_JOTFORM_API_KEY" > .env
# Optional: Add other ENV VARS like MCP_PORT=8067 if needed

# 3. Install dependencies and run (choose one method):

# Method A: Using pip (installs dependencies globally if not in a venv)
pip install -r requirements.txt && python jotform_mcp_server.py

# Method B: Using uv (installs uv then dependencies globally if not in a venv)
# pip install uv && uv pip sync uv.lock && python jotform_mcp_server.py

# 4. Stop the server with CTRL+C when done.
# 5. Remove the directory if you don't need it anymore: cd .. && rm -rf jotform-mcp-server
```
**Note:** This method might install dependencies globally if you are not inside an activated virtual environment. Using a dedicated virtual environment (Steps 2 & 3 in the main setup) or Docker is recommended for better project isolation.

### Available Tools

This server exposes the following tools, derived from the `JotformAPIClient` methods and custom additions. Refer to the [JotForm API documentation](https://api.jotform.com/docs/) for details on parameters and return values for the underlying API calls, unless otherwise specified for custom tools.

**User Tools:**
*   `get_user`: Get user account details.
*   `get_usage`: Get monthly usage stats (submissions, uploads).
*   `get_submissions`: Get a list of submissions for the account (paginated, filterable).
*   `get_subusers`: Get a list of sub users.
*   `get_settings`: Get user's settings (timezone, language).
*   `update_settings`: Update user's settings.
*   `get_history`: Get user activity log.
*   `register_user`: Register a new user (use with caution).
*   `login_user`: Login user (use with caution).
*   `logout_user`: Logout user.

**Form Tools:**
*   `get_forms`: Get a list of forms for the account (paginated, filterable).
*   `get_form`: Get basic information about a specific form.
*   `get_form_questions`: Get a list of all questions on a form.
*   `get_form_question`: Get details about a specific question.
*   `create_form`: Create a new form.
*   `create_forms`: Create multiple new forms (PUT).
*   `delete_form`: Delete a specific form.
*   `clone_form`: Clone a single form.
*   `delete_form_question`: Delete a single form question.
*   `create_form_question`: Add a new question to a form.
*   `create_form_questions`: Add multiple new questions to a form (PUT).
*   `edit_form_question`: Add or edit properties of a single question.
*   `get_form_properties`: Get all properties of a form.
*   `get_form_property`: Get a specific property of a form.
*   `set_form_properties`: Add or edit properties of a form (POST).
*   `set_multiple_form_properties`: Add or edit multiple properties of a form (PUT).
*   `get_form_files`: List files uploaded to a form.
*   `get_form_webhooks`: Get list of webhooks for a form.
*   `create_form_webhook`: Add a new webhook to a form.
*   `delete_form_webhook`: Delete a specific webhook from a form.
*   `get_form_reports`: Get all reports associated with a form.
*   `create_report`: Create a new report for a form.

**Submission Tools:**
*   `get_form_submissions`: List submissions for a specific form (paginated, filterable).
*   `create_form_submission`: Submit data to a specific form.
*   `create_form_submissions`: Submit multiple data entries to a form (PUT).
*   `get_submission`: Get data for a specific submission.
*   `delete_submission`: Delete a single submission.
*   `edit_submission`: Edit a single submission.

**Folder Tools:**
*   `get_folders`: Get a list of form folders.
*   `get_folder`: Get details of a specific folder.
*   `create_folder`: Create a new folder.
*   `delete_folder`: Delete a specific folder and its subfolders.
*   `update_folder`: Update properties of a specific folder.
*   `add_forms_to_folder`: Add multiple forms to a folder.
*   `add_form_to_folder`: Add a specific form to a folder.

**Report Tools:**
*   `get_reports`: List all reports for the account.
*   `get_report`: Get details of a specific report.
*   `delete_report`: Delete a specific report.
*   *(Note: `create_report` is listed under Form Tools)*

**System Tools:**
*   `get_plan`: Get details of a specific Jotform plan (e.g., FREE, PREMIUM).

**Custom Tools:**
*   **`search_submissions_by_date`**:
    *   Searches submissions across specified forms (or all enabled forms if none specified) based on a date range or a predefined period.
    *   **Arguments:**
        *   `form_ids` (Optional `List[str]`): List of form IDs. Defaults to all enabled forms.
        *   `start_date` (Optional `str`): Start date "YYYY-MM-DD" (inclusive). Use with `end_date`.
        *   `end_date` (Optional `str`): End date "YYYY-MM-DD" (inclusive). Use with `start_date`.
        *   `period` (Optional `str`): Relative period ("today", "last_7_days", "last_30_days", "current_month", "last_month", "current_accounting_month", "last_accounting_month"). Cannot be used with specific dates. Uses `ACCOUNTING_MONTH_START_DAY` from `.env` for accounting periods.
        *   `limit_per_form` (Optional `int`): Max submissions per form (default 1000).
    *   **Returns:** JSON string with a list of submissions and search details.

### Original Python Client Usage

The `jotform.py` file still contains the `JotformAPIClient` class, which provides direct access to JotForm's API methods within Python scripts. You can import and use this class directly if needed, though the primary way to interact with this project is now intended to be through the MCP server. Refer to the original README history or the [JotForm API documentation](https://api.jotform.com/docs/) for examples of direct client usage.
