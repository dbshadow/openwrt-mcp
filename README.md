# OpenWrt MCP Server

This project provides a Model Context Protocol (MCP) server for managing OpenWrt devices. It allows you to interact with and control an OpenWrt router through a simple API, either by running a Python script directly or by deploying it as a Docker container.

The server utilizes `fastmcp` to expose OpenWrt functionalities as tools that can be called remotely. It also includes a custom LuCI JSON-RPC script (`sys.lua`) to add extra capabilities to the standard OpenWrt RPC interface.

## Features

- **Remote Control**: Manage your OpenWrt device through a simple MCP interface.
- **Extensible Tools**: Easily add new functionalities by defining new tools in `openwrt.py`.
- **Docker Support**: Deploy the server as a lightweight Docker container.
- **Custom LuCI RPC**: Includes `sys.lua` to add the following JSON-RPC methods:
    - `sys.board_info`: Get detailed board and system information.
    - `sys.net.ipaddrs`: Retrieve IP addresses for all network interfaces.
    - `led.set_trigger`: Control the state of system LEDs.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv): An extremely fast Python package installer and resolver.
- [Docker](https://www.docker.com/) (for containerized deployment)

## Setup and Installation

### Install uv

If you don't have `uv` installed, you can install it with the following command:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Usage

### Running Directly

Before running the server, you may need to update the OpenWrt connection details (host, username, and password) in `openwrt.py`.

```python
# openwrt.py
username="root"
password="your_password"
openwrt_host="http://your_openwrt_ip"
```

Start the MCP server. `uv` will automatically create a virtual environment and install the necessary dependencies from `requirements.txt` the first time you run this command.

```sh
uv run python openwrt.py
```

The server will start on `0.0.0.0:8444`.

### Deploying with Docker

You can build and run the MCP server in a Docker container.

1.  **Build the Docker image:**

    ```sh
    docker build -t openwrt-mcp .
    ```

2.  **Run the Docker container:**

    The server inside the container runs on port `8444`. The `Dockerfile` exposes port `8181`, but the application is configured for `8444`. Map the correct port when running the container.

    ```sh
    docker run -d -p 8444:8444 --name openwrt-mcp-server openwrt-mcp
    ```

## LuCI RPC Extension (`sys.lua`)

The `sys.lua` file extends the capabilities of the LuCI JSON-RPC interface on the OpenWrt device. To use the custom tools (`system_status`, `network_status`, `set_led_state`), you must place this file on your OpenWrt router.

1.  **Copy the file to your OpenWrt device:**

    Use `scp` or any other file transfer method to copy `sys.lua` to your router.

    ```sh
    scp sys.lua root@your_openwrt_ip:/usr/lib/lua/luci/sys.lua
    ```

2.  **Verify Permissions:**

    Ensure the file has the correct permissions.

    ```sh
    ssh root@your_openwrt_ip "chmod 644 /usr/lib/lua/luci/sys.lua"
    ```

    The new RPC methods will be available for use by the MCP server immediately.

## Available Tools

The following tools are exposed by the MCP server:

-   `reboot()`: Reboots the OpenWrt device.
-   `system_status()`: Retrieves system and board information.
-   `network_status()`: Gets the status of all network interfaces.
-   `read_log()`: Reads the system log (`logread`).
-   `set_led_state(state: str)`: Sets the state of the "Green" LED. `state` can be `'on'` or `'off'`.
