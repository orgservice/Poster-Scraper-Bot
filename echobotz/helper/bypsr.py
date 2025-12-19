import json
from urllib.parse import urlparse, quote_plus
import requests

from .. import LOGGER
from .utils.xtra import _sync_to_async

class EchoBypass:
    def __init__(self, key, endpoint, method="GET", norm=None):
        self.key = key
        self.endpoint = endpoint
        self.method = method
        self.norm = norm or self._norm

    async def fetch(self, url):
        api_url = self.endpoint if self.method == "POST" else f"{self.endpoint}{quote_plus(url)}"
        LOGGER.info(f"EchoBypass: [{self.key}] API URL: {api_url}")
        try:
            if self.method == "POST":
                resp = await _sync_to_async(requests.post, api_url, json={"url": url}, timeout=30)
            else:
                resp = await _sync_to_async(requests.get, api_url, timeout=30)
            LOGGER.info(f"EchoBypass: [{self.key}] Got response code: {resp.status_code}")
        except Exception as e:
            LOGGER.error(f"EchoBypass: [{self.key}] HTTP error: {e}", exc_info=True)
            return None, "Failed to reach bypass service."
        if resp.status_code != 200:
            LOGGER.error(f"EchoBypass: [{self.key}] API error: {resp.status_code}, body: {resp.text[:200]}")
            return None, "Bypass service error."
        try:
            data = resp.json()
        except Exception as e:
            LOGGER.error(f"EchoBypass: [{self.key}] JSON parse error: {e}")
            return None, "Invalid response from bypass service."
        if not isinstance(data, dict):
            LOGGER.error(f"EchoBypass: [{self.key}] Unexpected JSON structure from API.")
            return None, "Unexpected response from bypass service."
        if "success" in data and not data.get("success"):
            LOGGER.error(f"EchoBypass: [{self.key}] API failure, message: {data.get('message')}")
            return None, data.get("message") or "Bypass failed."
        LOGGER.info(f"EchoBypass: [{self.key}] Response normalization step.")
        return self.norm(data)

    def _norm(self, data):
        LOGGER.info(f"EchoBypass: [{self.key}] Running default normalization.")
        root = data.get("final", data)
        title = root.get("title") or root.get("file_name") or "N/A"
        filesize = root.get("filesize") or root.get("file_size") or "N/A"
        file_format = root.get("format") or root.get("file_format") or "N/A"
        links_clean = _xlnk(root)
        return {
            "title": str(title),
            "filesize": str(filesize),
            "format": str(file_format),
            "links": links_clean,
            "service": self.key,
        }, None

def _xlnk(root):
    links_clean = {}
    raw_links = root.get("links")
    if isinstance(raw_links, list):
        for item in raw_links:
            url = item.get("url") or item.get("link")
            typ = item.get("type") or item.get("name") or "Link"
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                links_clean[typ] = url
    elif isinstance(raw_links, dict):
        for k, v in raw_links.items():
            url = v if isinstance(v, str) else v.get("url") or v.get("link")
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                links_clean[k] = url
    return links_clean

def _hbpack_norm(data):
    if data.get("pack") and isinstance(data.get("results"), list):
        LOGGER.info(f"Normalization: hubcloud pack detected, formatting pack response.")
        return {
            "hc_pack_results": data.get("results"),
            "hc_pack": True,
            "total_files": data.get("total_files", len(data.get("results") or [])),
            "service": "hubcloud"
        }, None
    return EchoByRegistry["hubcloud"]._norm(data)

def _trfit_norm(data):
    direct = data.get("url")
    if not direct:
        LOGGER.error(f"Normalization: transfer_it missing url, possible file expired.")
        return None, "File Expired or File Not Found"
    LOGGER.info(f"Normalization: transfer_it direct link found.")
    return {
        "title": "N/A",
        "filesize": "N/A",
        "format": "N/A",
        "links": {"Direct Link": str(direct)},
        "service": "transfer_it"
    }, None

def _hbl_norm(data):
    direct = data.get("url")
    if not direct:
        LOGGER.error(f"Normalization: hblinks missing url, possible file expired.")
        return None, "File Expired or Link Not Found"
    LOGGER.info(f"Normalization: hblinks direct link found.")
    return {
        "title": "N/A",
        "filesize": "N/A",
        "format": "N/A",
        "links": {data.get("provider", "Direct Link"): str(direct)},
        "service": "hblinks"
    }, None

def _veg_norm(data):
    results = data.get("results")
    if not isinstance(results, list) or not results:
        LOGGER.error(f"Normalization: vegamovies no files found in response.")
        return None, "No files found."
    links_clean = {}
    for item in results:
        fname = item.get("file_name", "File")
        fsize = item.get("file_size", "N/A")
        label_base = f"{fname} ({fsize})" if fsize != "N/A" else fname
        for link in item.get("links", []):
            url = link.get("url")
            tag = link.get("tag") or "Link"
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                label = f"{label_base} | {tag}"
                links_clean[label] = url
    if not links_clean:
        LOGGER.error(f"Normalization: vegamovies no direct links in response.")
        return None, "No direct links found."
    LOGGER.info(f"Normalization: vegamovies multiple files packed.")
    return {
        "title": "Vegamovies Files",
        "filesize": "Multiple",
        "format": "MKV",
        "links": links_clean,
        "service": "vegamovies"
    }, None

EchoByRegistry = {
    "gdflix":       EchoBypass("gdflix", "https://hgbots.vercel.app/bypaas/gd.php?url="),
    "hubdrive":     EchoBypass("hubdrive", "https://hgbots.vercel.app/bypaas/hubdrive.php?url="),
    "extraflix":    EchoBypass("extraflix", "https://pbx1botapi.vercel.app/api/extraflix?url="),
    "hubcloud":     EchoBypass("hubcloud", "https://pbx1botapi.vercel.app/api/hubcloud?url=", norm=_hbpack_norm),
    "vcloud":       EchoBypass("vcloud", "https://pbx1botapi.vercel.app/api/vcloud?url="),
    "hubcdn":       EchoBypass("hubcdn", "https://pbx1botapi.vercel.app/api/hubcdn?url="),
    "driveleech":   EchoBypass("driveleech", "https://pbx1botapi.vercel.app/api/driveleech?url="),
    "neo":          EchoBypass("neo", "https://pbx1botapi.vercel.app/api/neo?url="),
    "gdrex":        EchoBypass("gdrex", "https://pbx1botapi.vercel.app/api/gdrex?url="),
    "pixelcdn":     EchoBypass("pixelcdn", "https://pbx1botapi.vercel.app/api/pixelcdn?url="),
    "extralink":    EchoBypass("extralink", "https://pbx1botapi.vercel.app/api/extralink?url="),
    "luxdrive":     EchoBypass("luxdrive", "https://pbx1botapi.vercel.app/api/luxdrive?url="),
    "nexdrive":     EchoBypass("nexdrive", "https://pbx1botsapi2.vercel.app/api/nexdrive?url="),
    "transfer_it":  EchoBypass("transfer_it", "https://transfer-it-henna.vercel.app/post", method="POST", norm=_trfit_norm),
    "hblinks":      EchoBypass("hblinks", "https://pbx1botsapi2.vercel.app/api/hblinks?url=", norm=_hbl_norm),
    "vegamovies":   EchoBypass("vegamovies", "https://pbx1botsapi2.vercel.app/api/vega?url=", norm=_veg_norm),
}

_cmd_aliases = {
    "gdflix": ["gdflix", "gdf"],
    "hubdrive": ["hubdrive", "hd"],
    "extraflix": ["extraflix"],
    "hubcloud": ["hubcloud", "hc"],
    "vcloud": ["vcloud", "vc"],
    "hubcdn": ["hubcdn", "hcdn"],
    "driveleech": ["driveleech", "dleech"],
    "neo": ["neo", "neolinks"],
    "gdrex": ["gdrex", "gdex"],
    "pixelcdn": ["pixelcdn", "pcdn"],
    "extralink": ["extralink"],
    "luxdrive": ["luxdrive"],
    "nexdrive": ["nexdrive", "nd"],
    "transfer_it": ["transfer_it", "ti"],
    "hblinks": ["hblinks", "hbl"],
    "vegamovies": ["vegamovies", "vega"]
}

CMD_TO_KEY = {alias: key for key, aliases in _cmd_aliases.items() for alias in aliases}

def _bysrv(cmd):
    key = CMD_TO_KEY.get(str(cmd).lower().lstrip("/"))
    LOGGER.info(f"_bysrv: resolving command '{cmd}' to service key '{key}'")
    return EchoByRegistry.get(key)

async def _bpinfo(cmd_name, target_url):
    service = _bysrv(cmd_name)
    if not service:
        LOGGER.error(f"_bpinfo: Unknown platform for command '{cmd_name}'.")
        return None, "Unknown platform for this command."
    try:
        parsed = urlparse(target_url)
        if not parsed.scheme or not parsed.netloc:
            LOGGER.error(f"_bpinfo: Invalid URL '{target_url}'")
            return None, "Invalid URL."
    except Exception:
        LOGGER.error(f"_bpinfo: URL parsing failed for '{target_url}'")
        return None, "Invalid URL."
    LOGGER.info(f"_bpinfo: Initiating bypass for service '{service.key}' and URL '{target_url}'")
    return await service.fetch(target_url)

def _lbl_key(key):
    mapping = {
        "instant_final": "Instant",
        "cloud_r2": "Cloud R2",
        "zip_final": "ZIP",
        "pixeldrain": "Pixeldrain",
        "telegram_file": "Telegram",
        "gofile_final": "Gofile",
    }
    if key in mapping:
        return mapping[key]
    return key.replace("_", " ").title()

def _lbl_name(name):
    s = str(name).strip()
    low = s.lower()
    if "[" in s and "]" in s and "download" in low:
        i1 = s.find("[")
        i2 = s.rfind("]")
        if i1 != -1 and i2 != -1 and i2 > i1:
            inner = s[i1 + 1 : i2].strip()
            if inner:
                return inner
    if low.startswith("download "):
        return s[8:].strip() or s
    return s

def _pack_html(results, page=1, per_page=10):
    total = len(results)
    max_page = (total - 1) // per_page + 1
    page = max(1, min(page, max_page))
    start = (page - 1) * per_page
    end = min(total, page * per_page)
    out = []
    for i, item in enumerate(results[start:end], start=1+start):
        name = item.get("file_name") or "File"
        sz = item.get("file_size") or "N/A"
        src = item.get("source") or ""
        out.append(f"<b>{i}. {name}</b> <code>({sz})</code>")
        links = item.get("links") or []
        for li in links:
            typ = li.get("type") or "Link"
            url = li.get("url")
            if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                continue
            out.append(f'   ╞ <b>{typ}</b>: <a href="{url}">Click Here</a>')
        out.append("")
    txt = "\n".join(out).strip()
    nav = f"<b>Page: {page}/{max_page}</b> | <b>Total Files: {total}</b>"
    LOGGER.info(f"_pack_html: Packed results for page {page}/{max_page}")
    return (txt, nav, page, max_page)
    
def _bylinks(links):
    if not isinstance(links, dict) or not links:
        LOGGER.info(f"_bylinks: No direct links found in results.")
        return "╰╴ No direct links found."
    grouped = any("|" in str(k) for k in links)
    out = []
    if not grouped:
        items = [
            (str(k).strip() or "Link", v.strip())
            for k, v in links.items()
            if isinstance(v, str) and v.strip().startswith(("http://", "https://"))
        ]
        for i, (k, v) in enumerate(items):
            out.append(
                f'{"╰╴" if i == len(items)-1 else "╞╴"} <b>{k}:</b> <a href="{v}">Click Here</a>'
            )
        return "\n".join(out) if out else "╰╴ No direct links found."
    groups = {}
    for k, v in links.items():
        if not isinstance(v, str):
            continue
        u = v.strip()
        if not u.startswith(("http://", "https://")):
            continue
        a, b = str(k).split("|", 1)
        groups.setdefault(a.strip(), []).append((b.strip(), u))
    for g, items in groups.items():
        out.append(f"\n<b>{g}</b>")
        for i, (k, v) in enumerate(items):
            out.append(
                f'{"╰╴" if i == len(items)-1 else "╞╴"} <b>{k}:</b> <a href="{v}">Click Here</a>'
            )
    LOGGER.info(f"_bylinks: Packed possibly grouped results for output.")
    return "\n".join(out).strip()
