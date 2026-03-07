#!/usr/bin/env python3
"""
Browser CDP MCP Server — dev-only tooling for WebUI debugging.

Connects to Chrome DevTools Protocol on localhost:9222 and exposes
browser automation tools for any agent.

Tools:
  browser_navigate(url, wait_ms?)    Navigate to URL, wait for load
  browser_screenshot(full_page?)     Capture screenshot as PNG ImageContent
  browser_evaluate(expression)       Run JS, return result
  browser_click(selector)            Click element by CSS selector
  browser_type(selector, text)       Type text into element
  browser_get_layout(selector)       Bounding rect + computed styles

Prerequisites:
  Chrome running with: --remote-debugging-port=9222

Config in opencode.json:
    "browser": {
      "type": "local",
      "command": ["venv/bin/python3", "mcp_servers/browser_cdp.py"],
      "enabled": true
    }
"""

import asyncio
import base64
import json
import logging
import sys
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import websockets.asyncio.client as ws_client
except ImportError:
    print("ERROR: websockets package required. Install with: pip install websockets", file=sys.stderr)
    sys.exit(1)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import ImageContent, TextContent, Tool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

CDP_HOST = "localhost"
CDP_PORT = 9222
CMD_TIMEOUT = 15  # seconds per CDP command

app = Server("browser-cdp")

# --- CDP Connection (module-level singleton) ---

_ws = None
_msg_id: int = 0
_lock = asyncio.Lock()


def _reset_connection():
    """Reset connection state (for testing)."""
    global _ws, _msg_id
    _ws = None
    _msg_id = 0


async def _get_ws():
    """Return an open WebSocket to the first Chrome tab, reconnecting if needed."""
    global _ws
    if _ws is not None:
        try:
            await asyncio.wait_for(_ws.ping(), timeout=2)
            return _ws
        except Exception:
            logger.warning("CDP connection lost - reconnecting")
            _ws = None

    try:
        raw = urllib.request.urlopen(
            f"http://{CDP_HOST}:{CDP_PORT}/json", timeout=5
        ).read()
    except OSError as e:
        raise RuntimeError(
            f"Cannot reach Chrome on {CDP_HOST}:{CDP_PORT}. "
            "Start Chrome with --remote-debugging-port=9222"
        ) from e

    targets = json.loads(raw)
    page_targets = [t for t in targets if t.get("type") == "page"]
    if not page_targets:
        raise RuntimeError("No page targets found in Chrome. Open a tab first.")

    ws_url = page_targets[0]["webSocketDebuggerUrl"]
    logger.info("Connecting to CDP at %s", ws_url)
    _ws = await ws_client.connect(ws_url, compression=None, max_size=64 * 1024 * 1024)
    return _ws


async def cdp(method: str, params: dict | None = None) -> dict:
    """Send a CDP command and return the result dict."""
    global _msg_id
    async with _lock:
        ws = await _get_ws()
        _msg_id += 1
        cmd_id = _msg_id
        payload = json.dumps({"id": cmd_id, "method": method, "params": params or {}})
        await ws.send(payload)

        deadline = asyncio.get_event_loop().time() + CMD_TIMEOUT
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise TimeoutError(f"CDP command {method!r} timed out")
            msg = json.loads(
                await asyncio.wait_for(ws.recv(), timeout=remaining)
            )
            if msg.get("id") == cmd_id:
                if "error" in msg:
                    raise RuntimeError(f"CDP error: {msg['error']}")
                return msg.get("result", {})


# --- Tool Definitions ---

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="browser_navigate",
            description=(
                "Navigate the browser to a URL and wait for the page to load. "
                "Returns the final URL and page title."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"},
                    "wait_ms": {
                        "type": "integer",
                        "default": 1500,
                        "description": "Extra milliseconds to wait after load event",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="browser_screenshot",
            description=(
                "Capture a full-page screenshot of the current browser tab. "
                "Returns a PNG image."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "full_page": {
                        "type": "boolean",
                        "default": False,
                        "description": "Capture beyond the visible viewport",
                    }
                },
            },
        ),
        Tool(
            name="browser_evaluate",
            description=(
                "Evaluate a JavaScript expression in the browser and return its value. "
                "Use returnByValue=true semantics - complex objects are JSON-serialised."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "JavaScript expression to evaluate",
                    }
                },
                "required": ["expression"],
            },
        ),
        Tool(
            name="browser_click",
            description=(
                "Click an element matched by a CSS selector. "
                "Scrolls the element into view first, then dispatches a mouse click via CDP."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the element to click",
                    }
                },
                "required": ["selector"],
            },
        ),
        Tool(
            name="browser_type",
            description=(
                "Focus an element and type text into it. "
                "Clears existing content first, then dispatches individual keystrokes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the input element",
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type",
                    },
                    "clear_first": {
                        "type": "boolean",
                        "default": True,
                        "description": "Clear existing value before typing",
                    },
                },
                "required": ["selector", "text"],
            },
        ),
        Tool(
            name="browser_get_layout",
            description=(
                "Get the bounding rectangle and key computed CSS properties for an element. "
                "Returns x, y, width, height (viewport-relative) plus display, visibility, "
                "font-size, color, background-color, z-index, position, overflow."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the element",
                    }
                },
                "required": ["selector"],
            },
        ),
    ]


# --- Tool Handlers ---

async def handle_navigate(args: dict) -> dict:
    url: str = args["url"]
    wait_ms: int = args.get("wait_ms", 1500)

    await cdp("Page.enable")
    await cdp("Page.navigate", {"url": url})

    for _ in range(20):
        await asyncio.sleep(0.5)
        result = await cdp(
            "Runtime.evaluate",
            {"expression": "document.readyState", "returnByValue": True},
        )
        if result.get("result", {}).get("value") == "complete":
            break

    if wait_ms > 0:
        await asyncio.sleep(wait_ms / 1000)

    title_result = await cdp(
        "Runtime.evaluate",
        {"expression": "document.title", "returnByValue": True},
    )
    final_url_result = await cdp(
        "Runtime.evaluate",
        {"expression": "location.href", "returnByValue": True},
    )

    return {
        "success": True,
        "url": final_url_result.get("result", {}).get("value", url),
        "title": title_result.get("result", {}).get("value", ""),
    }


async def handle_screenshot(args: dict) -> ImageContent:
    full_page: bool = args.get("full_page", False)

    params: dict[str, Any] = {"format": "png"}
    if full_page:
        dims = await cdp(
            "Runtime.evaluate",
            {
                "expression": (
                    "JSON.stringify({w: document.documentElement.scrollWidth,"
                    " h: document.documentElement.scrollHeight})"
                ),
                "returnByValue": True,
            },
        )
        size = json.loads(dims.get("result", {}).get("value", "{}"))
        if size:
            params["clip"] = {
                "x": 0, "y": 0,
                "width": size["w"], "height": size["h"],
                "scale": 1,
            }
        params["captureBeyondViewport"] = True

    result = await cdp("Page.captureScreenshot", params)
    data_b64: str = result["data"]
    return ImageContent(type="image", data=data_b64, mimeType="image/png")


async def handle_evaluate(args: dict) -> dict:
    expression: str = args["expression"]
    result = await cdp(
        "Runtime.evaluate",
        {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        },
    )
    obj = result.get("result", {})
    exc = result.get("exceptionDetails")
    if exc:
        return {
            "success": False,
            "error": exc.get("exception", {}).get("description", "JS exception"),
        }
    return {
        "success": True,
        "type": obj.get("type"),
        "value": obj.get("value"),
        "description": obj.get("description"),
    }


async def _get_element_center(selector: str) -> tuple[float, float]:
    """Return viewport (x, y) center of element matched by selector."""
    js = f"""
    (() => {{
        const el = document.querySelector({json.dumps(selector)});
        if (!el) return null;
        el.scrollIntoView({{block: 'center', behavior: 'instant'}});
        const r = el.getBoundingClientRect();
        return JSON.stringify({{x: r.left + r.width/2, y: r.top + r.height/2}});
    }})()
    """
    result = await cdp(
        "Runtime.evaluate", {"expression": js, "returnByValue": True}
    )
    val = result.get("result", {}).get("value")
    if val is None:
        raise RuntimeError(f"Element not found: {selector!r}")
    coords = json.loads(val)
    return coords["x"], coords["y"]


async def handle_click(args: dict) -> dict:
    selector: str = args["selector"]

    await asyncio.sleep(0.1)
    x, y = await _get_element_center(selector)

    for event_type in ("mousePressed", "mouseReleased"):
        await cdp(
            "Input.dispatchMouseEvent",
            {
                "type": event_type,
                "x": x, "y": y,
                "button": "left",
                "clickCount": 1,
            },
        )

    return {"success": True, "selector": selector, "clicked_at": {"x": x, "y": y}}


async def handle_type(args: dict) -> dict:
    selector: str = args["selector"]
    text: str = args["text"]
    clear_first: bool = args.get("clear_first", True)

    # Click to focus
    x, y = await _get_element_center(selector)
    for event_type in ("mousePressed", "mouseReleased"):
        await cdp(
            "Input.dispatchMouseEvent",
            {"type": event_type, "x": x, "y": y, "button": "left", "clickCount": 1},
        )

    if clear_first:
        # Select all (Ctrl+A) then delete
        await cdp("Input.dispatchKeyEvent", {
            "type": "keyDown", "key": "a", "code": "KeyA",
            "windowsVirtualKeyCode": 65, "modifiers": 2,  # 2 = Ctrl
        })
        await cdp("Input.dispatchKeyEvent", {
            "type": "keyUp", "key": "a", "code": "KeyA",
            "windowsVirtualKeyCode": 65, "modifiers": 2,
        })
        await cdp("Input.dispatchKeyEvent", {
            "type": "keyDown", "key": "Backspace", "code": "Backspace",
            "windowsVirtualKeyCode": 8,
        })
        await cdp("Input.dispatchKeyEvent", {
            "type": "keyUp", "key": "Backspace", "code": "Backspace",
            "windowsVirtualKeyCode": 8,
        })

    # Type each character
    for char in text:
        await cdp("Input.dispatchKeyEvent", {"type": "char", "text": char})

    return {"success": True, "selector": selector, "typed": len(text)}


async def handle_get_layout(args: dict) -> dict:
    selector: str = args["selector"]

    js = f"""
    (() => {{
        const el = document.querySelector({json.dumps(selector)});
        if (!el) return null;
        const r = el.getBoundingClientRect();
        const st = window.getComputedStyle(el);
        return JSON.stringify({{
            x: r.x, y: r.y, width: r.width, height: r.height,
            top: r.top, right: r.right, bottom: r.bottom, left: r.left,
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            display: st.display,
            visibility: st.visibility,
            fontSize: st.fontSize,
            color: st.color,
            backgroundColor: st.backgroundColor,
            zIndex: st.zIndex,
            position: st.position,
            overflow: st.overflow,
            flexDirection: st.flexDirection,
            flexShrink: st.flexShrink
        }});
    }})()
    """
    result = await cdp(
        "Runtime.evaluate", {"expression": js, "returnByValue": True}
    )
    val = result.get("result", {}).get("value")
    if val is None:
        return {"success": False, "error": f"Element not found: {selector!r}"}

    layout = json.loads(val)
    return {"success": True, "selector": selector, "layout": layout}


# --- MCP Call Dispatcher ---

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent]:
    logger.info("Tool call: %s  args=%s", name, arguments)
    try:
        if name == "browser_navigate":
            result = await handle_navigate(arguments)
        elif name == "browser_screenshot":
            result = await handle_screenshot(arguments)
        elif name == "browser_evaluate":
            result = await handle_evaluate(arguments)
        elif name == "browser_click":
            result = await handle_click(arguments)
        elif name == "browser_type":
            result = await handle_type(arguments)
        elif name == "browser_get_layout":
            result = await handle_get_layout(arguments)
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}

        if isinstance(result, ImageContent):
            return [result]

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        logger.error("Error in %s: %s", name, e, exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2),
        )]


# --- Main ---

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
