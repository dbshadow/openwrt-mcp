
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
    登入 OpenWrt 並回傳 token。
    登入失敗則回傳 None。
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
    會自動先登入取得Token再執行重開機。
    """
    token = _login()
    if not token:
        return "登入失敗，無法執行重開機。"

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
            res = "重開機已完成."
        else:
            res = f"重開機失敗: {data.get('error')}"
        return res
    except requests.exceptions.RequestException as e:
        print(f"Reboot request failed: {e}")
        return f"重開機請求失敗: {e}"


@mcp.tool()
def system_status() -> str:
    """
    取得OpenWRT的系統狀態。
    會自動先登入取得Token再執行。
    """
    token = _login()
    if not token:
        return "登入失敗，無法取得版本狀態。"

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
            res = f"取得狀態失敗: {data.get('error')}"
        return str(res)
    except requests.exceptions.RequestException as e:
        print(f"Version status request failed: {e}")
        return f"取得狀態請求失敗: {e}"

@mcp.tool()
def network_status() -> str:
    """
    取得OpenWRT所有網路介面的狀態。
    會自動先登入取得Token再執行。
    """
    token = _login()
    if not token:
        return "登入失敗，無法取得網路狀態。"

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
            res = f"取得狀態失敗: {data.get('error')}"
        return str(res)
    except requests.exceptions.RequestException as e:
        print(f"Network status request failed: {e}")
        return f"取得狀態請求失敗: {e}"

@mcp.tool()
def read_log() -> str:
    """
    讀取OpenWRT的系統日誌 (logread)。
    會自動先登入取得Token再執行。
    """
    token = _login()
    if not token:
        return "登入失敗，無法讀取日誌。"

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
            res = f"讀取日誌失敗: {data.get('error')}"
        return str(res)
    except requests.exceptions.RequestException as e:
        print(f"Log read request failed: {e}")
        return f"讀取日誌請求失敗: {e}"

@mcp.tool()
def set_led_state(state: str) -> str:
    """
    控制 Green LED 燈亮起或熄滅。
    state: 'on' 或 'off'
    """
    token = _login()
    if not token:
        return "登入失敗，無法控制LED。"

    name = "Green" # 固定LED名稱

    # 將 'on'/'off' 狀態轉換為對應的 trigger 值
    trigger = "none"
    if state == "on":
        trigger = "default-on"
    elif state != "off":
        return "無效的狀態，請使用 'on' 或 'off'。"

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
                res = f"成功將LED '{name}' 的狀態設為 {state}。"
            else:
                res = f"設定LED失敗: {result.get('error')}"
        else:
            res = f"控制LED失敗: {data.get('error')}"
        return res
    except requests.exceptions.RequestException as e:
        print(f"LED control request failed: {e}")
        return f"控制LED請求失敗: {e}"

'''
@mcp.resource("resource://greeting")
def get_greeting() -> str:
    """Provides a simple greeting message."""
    return "Hello from FastMCP Resources!"

@mcp.prompt
def ask_about_topic(topic: str) -> str:
    """Generates a user message asking for an explanation of a topic."""
    return f"Can you please explain the concept of '{topic}'?"
'''

@mcp.prompt
def summary_log() -> str:
    """針對工具read_log取得的log，產生一個有條理的格式供AI總結。"""
    summary="\
    1. **「核心與硬體狀態」**: 幫我找出所有與 OpenWRT 核心啟動、驅動程式、CPU、記憶體、PCIe、USB 或網路硬體相關的資訊，特別留意任何 `warn` 或 `err` 等錯誤訊息。這類日誌通常以 `kern.info kernel:`, `kern.warn kernel:`, `kern.err kernel:` 開頭。\n\
        **例如：** `Booting Linux`, `Memory:`, `CPU features:`, `PCIe`, `USB`, `eth`, `mtk-`, `failed to get`.\n\
    2. **「網路服務診斷」**: 幫我分析所有與網路服務（如 DHCP、DNS）、網路介面狀態（例如 WAN/LAN 連線狀態）或防火牆設定變更有關的日誌。這類日誌通常來自 `netifd`, `dnsmasq`, `firewall`, `udhcpc` 等服務。\n\
        **例如：** `netifd: Interface 'wan' is now up`, `dnsmasq: started`, `udhcpc: lease of ... obtained`, `firewall: Reloading firewall`.\n\
    3. **「應用程式事件」**: 幫我列出除了核心和網路服務之外，其他應用程式或系統進程（例如 `procd`, `kmodloader`, `collectd`, `sshd`）的啟動、停止或異常記錄。這類日誌通常來自使用者空間的應用程式。\n\
        **例如：** `init: Console is alive`, `kmodloader: loading kernel modules`, `collectd: Initialization complete`, `sshd: Server listening`.\n\
    4. **「所有異常報告」**: 獨立列出所有日誌中包含 `warn` 或 `err` 關鍵字的訊息，並簡要說明其可能的含義，讓我能快速掌握問題點。"
    return f"使用工具讀取openwrt的log以後，再依照下面的格式總結log的重點：\n{summary}"


#mcp.run(transport='stdio')
#mcp.run(transport="streamable-http",
mcp.run(transport="sse",
            host="0.0.0.0",
            port=8444)
