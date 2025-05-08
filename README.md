# JotForm API - Python Client & MCP Server

This repository contains the Python client for the [JotForm API](https://api.jotform.com/docs/) and an MCP (Model Context Protocol) server built using this client. The MCP server allows interaction with the Jotform API through standardized tools.

### Authentication

JotForm API requires an API key for all user-related calls. You can create your API Keys at the [API section](https://www.jotform.com/myaccount/api) of your JotForm account settings. This key is needed to run the MCP server.

### Setup and Running the MCP Server

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

This project uses `uv` for dependency management. If you don't have `uv`, install it first (within or outside the venv):
```bash
pip install uv
```
Then, install dependencies using the lock file:
```bash
uv pip sync uv.lock
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

### Available Tools

This server exposes all public methods of the original `JotformAPIClient` as MCP tools. Tool names generally follow the client method names (e.g., `get_user`, `get_forms`, `create_form_submission`). Refer to the [JotForm API documentation](https://api.jotform.com/docs/) for details on parameters and return values for the underlying API calls.

**Custom Tools:**

*   **`search_submissions_by_date`**:
    *   Searches submissions across specified forms (or all enabled forms if none specified) based on a date range or a predefined period.
    *   **Arguments:**
        *   `form_ids` (Optional `List[str]`): List of form IDs. Defaults to all enabled forms.
        *   `start_date` (Optional `str`): Start date "YYYY-MM-DD" (inclusive). Use with `end_date`.
        *   `end_date` (Optional `str`): End date "YYYY-MM-DD" (inclusive). Use with `start_date`.
        *   `period` (Optional `str`): Relative period ("last_7_days", "last_30_days", "current_month", "last_month", "current_accounting_month", "last_accounting_month"). Cannot be used with specific dates. Uses `ACCOUNTING_MONTH_START_DAY` from `.env` for accounting periods.
        *   `limit_per_form` (Optional `int`): Max submissions per form (default 1000).
    *   **Returns:** JSON string with a list of submissions and search details.

### Original Python Client Usage

The `jotform.py` file still contains the `JotformAPIClient` class, which provides direct access to JotForm's API methods within Python scripts. You can import and use this class directly if needed, though the primary way to interact with this project is now intended to be through the MCP server. Refer to the original README history or the [JotForm API documentation](https://api.jotform.com/docs/) for examples of direct client usage.
