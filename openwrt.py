
from fastmcp import FastMCP
import requests
import sys

# Create an MCP server
mcp = FastMCP("OpenWrt Controller")

username="root"
password="1234asdf"
openwrt_host="http://192.168.7.153"
rpc_base_url = f"{openwrt_host}/cgi-bin/luci/rpc"

def _login() -> str | None:
    """
    Login to OpenWrt and return token.
    Returns None if login fails.
    """
    auth_url = f"{rpc_base_url}/auth"
    payload = {
        "id": 1,
        "method": "login",
        "params": [username, password]
    }

    try:
        resp = requests.post(auth_url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if "result" in data and data.get("error") is None:
            token = data["result"]
            return token
        else:
            print("Login failed:", data.get("error"))
            return None
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {e}")
        return None


@mcp.tool()
def reboot() -> str:
    """
    Reboot OpenWRT.
    Automatically logs in to get token before executing reboot.
    """
    token = _login()
    if not token:
        return "Login failed, unable to execute reboot."

    sys_url = f"{rpc_base_url}/sys"
    payload = {
        "id": 1,
        "method": "reboot",
        "params": []
    }
    cookies = {"sysauth": token}

    try:
        resp = requests.post(sys_url, json=payload, cookies=cookies)
        resp.raise_for_status()
        data = resp.json()

        if data.get("error") is None:
            res = "Reboot completed."
        else:
            res = f"Reboot failed: {data.get('error')}"
        return res
    except requests.exceptions.RequestException as e:
        print(f"Reboot request failed: {e}")
        return f"Reboot request failed: {e}"


@mcp.tool()
def system_status() -> str:
    """
    Get OpenWRT system status.
    Automatically logs in to get token before execution.
    """
    token = _login()
    if not token:
        return "Login failed, unable to get system status."

    sys_url = f"{rpc_base_url}/sys"
    payload = {
        "id": 1,
        "method": "board_info",
        "params": []
    }
    cookies = {"sysauth": token}

    try:
        resp = requests.post(sys_url, json=payload, cookies=cookies)
        resp.raise_for_status()
        data = resp.json()

        if "result" in data and data.get("error") is None:
            res = data["result"]
            print(res)
        else:
            res = f"Failed to get status: {data.get('error')}"
        return str(res)
    except requests.exceptions.RequestException as e:
        print(f"Version status request failed: {e}")
        return f"Status request failed: {e}"

@mcp.tool()
def network_status() -> str:
    """
    Get status of all OpenWRT network interfaces.
    Automatically logs in to get token before execution.
    """
    token = _login()
    if not token:
        return "Login failed, unable to get network status."

    sys_url = f"{rpc_base_url}/sys"
    payload = {
        "id": 1,
        "method": "net.ipaddrs",
        "params": []
    }
    cookies = {"sysauth": token}

    try:
        resp = requests.post(sys_url, json=payload, cookies=cookies)
        resp.raise_for_status()
        data = resp.json()

        if "result" in data and data.get("error") is None:
            res = data["result"]
            print(res)
        else:
            res = f"Failed to get status: {data.get('error')}"
        return str(res)
    except requests.exceptions.RequestException as e:
        print(f"Network status request failed: {e}")
        return f"Status request failed: {e}"

@mcp.tool()
def read_log() -> str:
    """
    Read OpenWRT system log (logread).
    Automatically logs in to get token before execution.
    """
    token = _login()
    if not token:
        return "Login failed, unable to read log."

    sys_url = f"{rpc_base_url}/sys"
    payload = {
        "id": 1,
        "method": "syslog",
        "params": []
    }
    cookies = {"sysauth": token}

    try:
        resp = requests.post(sys_url, json=payload, cookies=cookies)
        resp.raise_for_status()
        data = resp.json()

        if "result" in data and data.get("error") is None:
            res = data["result"]
        else:
            res = f"Failed to read log: {data.get('error')}"
        return str(res)
    except requests.exceptions.RequestException as e:
        print(f"Log read request failed: {e}")
        return f"Log read request failed: {e}"

@mcp.tool()
def set_led_state(state: str) -> str:
    """
    Control Green LED on or off.
    state: 'on' or 'off'
    """
    token = _login()
    if not token:
        return "Login failed, unable to control LED."

    name = "Green" # Fixed LED name

    # Convert 'on'/'off' state to corresponding trigger value
    trigger = "none"
    if state == "on":
        trigger = "default-on"
    elif state != "off":
        return "Invalid state, please use 'on' or 'off'."

    sys_url = f"{rpc_base_url}/sys"
    payload = {
        "id": 1,
        "method": "led.set_trigger",
        "params": [name, trigger]
    }
    cookies = {"sysauth": token}

    try:
        resp = requests.post(sys_url, json=payload, cookies=cookies)
        resp.raise_for_status()
        data = resp.json()

        if "result" in data and data.get("error") is None:
            result = data["result"]
            if result.get("success"):
                res = f"Successfully set LED '{name}' state to {state}."
            else:
                res = f"Failed to set LED: {result.get('error')}"
        else:
            res = f"Failed to control LED: {data.get('error')}"
        return res
    except requests.exceptions.RequestException as e:
        print(f"LED control request failed: {e}")
        return f"LED control request failed: {e}"

@mcp.resource("file://openwrt-py")
def get_openwrt_py() -> str:
    """Return the content of openwrt.py file."""
    file_path = "/app/openwrt.py"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file not found at {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"

@mcp.prompt
def summary_log() -> str:
    """Generate a structured format for AI to summarize logs obtained from the read_log tool."""
    summary="""\
    1. **"Kernel and Hardware Status"**: Help me find all information related to OpenWRT kernel boot, drivers, CPU, memory, PCIe, USB, or network hardware, paying special attention to any `warn` or `err` error messages. These logs typically start with `kern.info kernel:`, `kern.warn kernel:`, `kern.err kernel:`.\n\
        **Examples:** `Booting Linux`, `Memory:`, `CPU features:`, `PCIe`, `USB`, `eth`, `mtk-`, `failed to get`.\n\
    2. **"Network Service Diagnostics"**: Help me analyze all logs related to network services (such as DHCP, DNS), network interface status (e.g., WAN/LAN connection status), or firewall configuration changes. These logs typically come from services like `netifd`, `dnsmasq`, `firewall`, `udhcpc`.\n\
        **Examples:** `netifd: Interface 'wan' is now up`, `dnsmasq: started`, `udhcpc: lease of ... obtained`, `firewall: Reloading firewall`.\n\
    3. **"Application Events"**: Help me list startup, shutdown, or abnormal records of other applications or system processes (such as `procd`, `kmodloader`, `collectd`, `sshd`) besides kernel and network services. These logs typically come from user-space applications.\n\
        **Examples:** `init: Console is alive`, `kmodloader: loading kernel modules`, `collectd: Initialization complete`, `sshd: Server listening`.\n\
    4. **"All Exception Reports"**: Separately list all messages in the logs containing `warn` or `err` keywords, and briefly explain their possible meanings, allowing me to quickly grasp problem points.
    """
    return f"After using the tool to read OpenWRT logs, summarize the key points of the logs according to the following format:{summary}\n"


#mcp.run(transport='stdio')
#mcp.run(transport="sse",
mcp.run(transport="streamable-http",
            host="127.0.0.1",
            port=8444)
