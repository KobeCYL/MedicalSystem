import json

from .supabase_client import fetch_history


def handler(request):
    try:
        try:
            qp = request.get_query() if hasattr(request, "get_query") else {}
        except Exception:
            qp = {}
        page = int(qp.get("page", 1)) if isinstance(qp, dict) else 1
        ps_val = qp.get("page_size", 20) if isinstance(qp, dict) else 20
        page_size = int(ps_val)
        data = fetch_history(
            page=page,
            page_size=page_size,
        )
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            },
            "body": json.dumps(data, ensure_ascii=False),
        }
    except Exception:
        empty = {"items": [], "page": 1, "page_size": 20, "total": 0}
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
