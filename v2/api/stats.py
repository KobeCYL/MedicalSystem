import json
from typing import List, Dict

from .supabase_client import fetch_status_and_durations


def _calc_stats(items: List[Dict]) -> Dict[str, Dict]:
    normal = malicious = non_medical = 0
    durations: List[float] = []
    for e in items:
        s = e.get("status")
        if s == "success":
            normal += 1
        elif s == "no_match":
            non_medical += 1
        elif s in ("failed", "error"):
            malicious += 1
        d = e.get("total_duration_ms") or e.get("server_duration_ms")
        try:
            if d is not None:
                durations.append(float(d))
        except Exception:
            pass
    durations.sort()
    n = len(durations)
    avg = sum(durations) / n if n else 0.0
    p95 = durations[int(0.95 * (n - 1))] if n else 0.0
    mx = durations[-1] if n else 0.0
    return {
        "counts": {
            "normal": normal,
            "malicious_or_error": malicious,
            "non_medical": non_medical,
            "total": len(items),
        },
        "durations_ms": {
            "count": n,
            "avg": round(avg, 2),
            "p95": round(p95, 2),
            "max": round(mx, 2),
        },
    }


def handler(_request):
    try:
        items = fetch_status_and_durations(limit=1000)
        body = _calc_stats(items)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            },
            "body": json.dumps(body, ensure_ascii=False),
        }
    except Exception:
        empty = {
            "counts": {
                "normal": 0,
                "malicious_or_error": 0,
                "non_medical": 0,
                "total": 0,
            },
            "durations_ms": {"count": 0, "avg": 0.0, "p95": 0.0, "max": 0.0},
        }
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            },
            "body": json.dumps(empty, ensure_ascii=False),
        }
