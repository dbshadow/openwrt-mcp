# OpenWrt MCP Controller

This project provides a Model Context Protocol (MCP) server for managing OpenWrt devices. It allows you to interact with and control an OpenWrt router through a simple API.

The server utilizes `fastmcp` to expose OpenWrt functionalities as tools that can be called remotely.

## 1. Prerequisites

For the server to have full functionality, a custom LuCI RPC script must be placed on the target OpenWrt device.

### Install `sys.lua` on OpenWrt

The `sys.lua` file in this repository extends the capabilities of the LuCI JSON-RPC interface. You must copy this file to your OpenWrt router for tools like `system_status`, `network_status`, and `set_led_state` to work.

1.  **Copy the file to your OpenWrt device:**
    Use `scp` or any other file transfer method to copy `sys.lua` to your router.

    ```sh
    scp sys.lua root@<your_openwrt_ip>:/usr/lib/lua/luci/sys.lua
    ```

2.  **Verify Permissions:**
    Ensure the file has the correct permissions.

    ```sh
    ssh root@<your_openwrt_ip> "chmod 644 /usr/lib/lua/luci/sys.lua"
    ```

## 2. Installation

You can install this package directly from PyPI.

```sh
pip install openwrt-mcp
```

## 3. Configuration

The server is configured through environment variables. You must set the following before running the server:

-   `OPENWRT_HOST`: The full URL of your OpenWrt device (e.g., `http://192.168.1.1`).
-   `OPENWRT_PASSWORD`: The login password for your OpenWrt device.
-   `OPENWRT_USERNAME`: (Optional) The login username. Defaults to `root`.

Example:
```sh
export OPENWRT_HOST="http://192.168.1.1"
export OPENWRT_PASSWORD="your_secret_password"
```

## 4. Usage

Once installed and configured, you can start the MCP server with the following configuration:

```sh
{
    "mcpServers":{
        "openwrt-mcp":{
            "command":"uvx",
            "args": [
                "openwrt-mcp"
            ],
            "env":{
                "OPENWRT_HOST":"192.168.0.1",
                "OPENWRT_PASSWORD":"root",
                "OPENWRT_USERNAME":"12345678"
            }
        }
    }
}
```

The server will start and listen for incoming connections via standard I/O.

## Available Tools

The following tools are exposed by the MCP server:

-   `reboot()`: Reboots the OpenWrt device.
-   `system_status()`: Retrieves system and board information.
-   `network_status()`: Gets the status of all network interfaces.
-   `read_log()`: Reads the system log (`logread`).
-   `set_led_state(state: str)`: Sets the state of the "Green" LED. `state` can be `'on'` or `'off'`.
-   `summary_log()`: Provides a structured prompt template for an AI to summarize the output of `read_log()`.
