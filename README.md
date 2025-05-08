# JotForm API - Python Client & MCP Server

This repository contains the Python client for the [JotForm API](https://api.jotform.com/docs/) and an MCP (Model Context Protocol) server built using this client. The MCP server allows interaction with the Jotform API through standardized tools.

### Authentication

JotForm API requires an API key for all user-related calls. You can create your API Keys at the [API section](https://www.jotform.com/myaccount/api) of your JotForm account settings. This key is needed to run the MCP server.

### Setup and Running the MCP Server

**1. Clone the Repository:**

```bash
git clone https://github.com/YOUR_USERNAME/jotform-api-python.git # Replace YOUR_USERNAME
cd jotform-api-python
```

**2. Create Virtual Environment (Recommended):**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

**3. Install Dependencies:**

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

### Original Python Client Usage

The `jotform.py` file still contains the `JotformAPIClient` class, which provides direct access to JotForm's API methods within Python scripts. You can import and use this class directly if needed, though the primary way to interact with this project is now intended to be through the MCP server. Refer to the original README history or the [JotForm API documentation](https://api.jotform.com/docs/) for examples of direct client usage.
