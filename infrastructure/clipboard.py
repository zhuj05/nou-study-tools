"""跨平台剪貼簿服務 (適配 Flet 1.0+、舊版 Flet 與 Pyodide/瀏覽器環境)。"""

import flet as ft


async def set_clipboard_universal(page: ft.Page, text: str) -> bool:
    """全相容跨版本剪貼簿複製常式。"""
    if hasattr(page, "clipboard") and page.clipboard is not None:
        try:
            if hasattr(page.clipboard, "set_async"):
                await page.clipboard.set_async(text)
                return True
            elif hasattr(page.clipboard, "set"):
                page.clipboard.set(text)
                return True
        except Exception:
            pass

    if hasattr(page, "set_clipboard_async"):
        try:
            await page.set_clipboard_async(text)
            return True
        except Exception:
            pass
    if hasattr(page, "set_clipboard"):
        try:
            page.set_clipboard(text)
            return True
        except Exception:
            pass

    try:
        import js

        if hasattr(js, "navigator") and hasattr(js.navigator, "clipboard"):
            #js.navigator.clipboard.writeText(text)
            await js.navigator.clipboard.writeText(text)
            return True
        elif (
            hasattr(js, "window")
            and hasattr(js.window, "navigator")
            and hasattr(js.window.navigator, "clipboard")
        ):
            #js.window.navigator.clipboard.writeText(text)
            await js.window.navigator.clipboard.writeText(text)
            return True
    except Exception:
        pass

    return False