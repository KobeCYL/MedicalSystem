import os
import json
from typing import Any, Dict, List, Optional
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def _headers() -> Dict[str, str]:
    key = SUPABASE_SERVICE_ROLE_KEY or ""
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation,count=exact",
    }


def insert_query(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            return None
        base = f"{SUPABASE_URL}/rest/v1/queries"
        resp = requests.post(base, headers=_headers(), data=json.dumps(record))
        if resp.status_code in (200, 201):
            data = resp.json()
            return data[0] if isinstance(data, list) and data else data
        return None
    except Exception:
        return None


def fetch_history(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    try:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            empty = {
                "items": [],
                "page": page,
                "page_size": page_size,
                "total": 0,
            }
            return empty
        offset = max(0, (page - 1) * page_size)
        params = {
            "select": "*",
            "order": "timestamp.desc",
        }
        base = f"{SUPABASE_URL}/rest/v1/queries"
        headers = _headers()
        headers["Range"] = f"{offset}-{offset + page_size - 1}"
        resp = requests.get(
            base,
            headers=headers,
            params=params,
        )
        items: List[Dict[str, Any]] = []
        if resp.status_code == 200:
            raw = resp.json()
            if isinstance(raw, list):
                items = raw
        else:
            try:
                base_dir = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "..")
                )
                fp = os.path.join(base_dir, "data", "query_history.json")
                fallback_items: List[Dict[str, Any]] = []
                if os.path.exists(fp):
                    with open(fp, "r", encoding="utf-8") as f:
                        obj = json.load(f)
                        if isinstance(obj, list):
                            fallback_items = obj
                total_fb = len(fallback_items)
                end = offset + page_size
                items = fallback_items[offset:end]
                total = total_fb
                return {
                    "items": items,
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                }
            except Exception:
                pass
        total = len(items)
        try:
            cr = resp.headers.get("Content-Range")
            if isinstance(cr, str) and "/" in cr:
                total = int(cr.split("/")[-1])
        except Exception:
            pass
        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
        }
    except Exception:
        return {"items": [], "page": page, "page_size": page_size, "total": 0}


def fetch_status_and_durations(limit: int = 1000) -> List[Dict[str, Any]]:
    try:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            return []
        select = "status,total_duration_ms,server_duration_ms"
        params = {
            "select": select,
            "order": "timestamp.desc",
        }
        base = f"{SUPABASE_URL}/rest/v1/queries"
        headers = _headers()
        headers["Range"] = f"0-{max(0, limit - 1)}"
        resp = requests.get(
            base,
            headers=headers,
            params=params,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data if isinstance(data, list) else []
        try:
            base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..")
            )
            fp = os.path.join(base_dir, "data", "query_history.json")
            if os.path.exists(fp):
                with open(fp, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                    if isinstance(obj, list):
                        mapped: List[Dict[str, Any]] = []
                        for e in obj[:limit]:
                            if isinstance(e, dict):
                                mapped.append(
                                    {
                                        "status": e.get("status"),
                                        "total_duration_ms": e.get(
                                            "total_duration_ms"
                                        ),
                                        "server_duration_ms": e.get(
                                            "server_duration_ms"
                                        ),
                                    }
                                )
                        return mapped
        except Exception:
            pass
        return []
    except Exception:
        return []
