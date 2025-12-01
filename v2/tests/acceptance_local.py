import os
import importlib.util

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_module(path, fullname):
    spec = importlib.util.spec_from_file_location(fullname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Req:
    def __init__(self, body=None, query=None):
        self._body = body or {}
        self._query = query or {}

    def get_json(self):
        return self._body

    def get_query(self):
        return self._query


def run():
    import json
    import datetime
    import sys
    root_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    if root_dir not in sys.path:
        sys.path.append(root_dir)
    from v2.api.health import handler as health_handler
    from v2.api.history import handler as history_handler
    from v2.api.stats import handler as stats_handler, _calc_stats
    from v2.api.medical_query import handler as mq_handler
    res_health = health_handler(None)
    print("HEALTH", res_health["statusCode"])

    req_h = Req(query={"page": 1, "page_size": 5})
    res_history = history_handler(req_h)
    body_history = {}
    if isinstance(res_history.get("body"), str):
        body_history = json.loads(res_history["body"])
    print("HISTORY", res_history["statusCode"], body_history.get("total"))

    res_stats = stats_handler(None)
    body_stats = {}
    if isinstance(res_stats.get("body"), str):
        body_stats = json.loads(res_stats["body"])
    total_counts = body_stats.get("counts", {}).get("total")
    print("STATS_HANDLER", res_stats["statusCode"], total_counts)

    items = [
        {"status": "success", "total_duration_ms": 100},
        {"status": "success", "server_duration_ms": 50},
        {"status": "no_match", "total_duration_ms": 200},
        {"status": "failed", "total_duration_ms": 300},
        {"status": "error", "server_duration_ms": 150},
        {"status": "success", "total_duration_ms": None},
    ]
    calc = _calc_stats(items)
    print("STATS_CALC", calc["counts"]["total"], calc["durations_ms"]["count"])

    req_mq = Req(
        body={
            "symptom": "发热咳嗽",
            "patient_info": {"age": 30, "gender": "男"},
            "client_start_ts": datetime.datetime.now().isoformat(),
        }
    )
    res_mq = mq_handler(req_mq)
    body_mq = {}
    if isinstance(res_mq.get("body"), str):
        body_mq = json.loads(res_mq["body"])
    print(
        "MEDICAL_QUERY",
        res_mq["statusCode"],
        body_mq.get("status"),
        body_mq.get("server_duration_ms"),
        body_mq.get("total_duration_ms"),
    )

    res_history_2 = history_handler(Req(query={"page": 1, "page_size": 5}))
    body_history_2 = {}
    if isinstance(res_history_2.get("body"), str):
        body_history_2 = json.loads(res_history_2["body"])
    print(
        "HISTORY_AFTER",
        res_history_2["statusCode"],
        body_history_2.get("total"),
    )

    res_stats_2 = stats_handler(None)
    body_stats_2 = {}
    if isinstance(res_stats_2.get("body"), str):
        body_stats_2 = json.loads(res_stats_2["body"])
    total_counts_2 = body_stats_2.get("counts", {}).get("total")
    print("STATS_AFTER", res_stats_2["statusCode"], total_counts_2)

    req_no_match = Req(
        body={
            "symptom": "",
            "patient_info": {"age": 25, "gender": "女"},
            "client_start_ts": datetime.datetime.now().isoformat(),
        }
    )
    res_nm = mq_handler(req_no_match)
    bm_nm = {}
    if isinstance(res_nm.get("body"), str):
        bm_nm = json.loads(res_nm["body"])
    print("NO_MATCH", res_nm["statusCode"], bm_nm.get("status"))

    req_failed = Req(
        body={
            "symptom": "我有自杀的念头",
            "patient_info": {"age": 20, "gender": "男"},
            "client_start_ts": datetime.datetime.now().isoformat(),
        }
    )
    res_fd = mq_handler(req_failed)
    bm_fd = {}
    if isinstance(res_fd.get("body"), str):
        bm_fd = json.loads(res_fd["body"])
    print("FAILED_CASE", res_fd["statusCode"], bm_fd.get("status"))

    res_history_3 = history_handler(Req(query={"page": 1, "page_size": 10}))
    bh3 = {}
    if isinstance(res_history_3.get("body"), str):
        bh3 = json.loads(res_history_3["body"])
    print("HISTORY_FINAL", res_history_3["statusCode"], bh3.get("total"))

    res_stats_3 = stats_handler(None)
    bs3 = {}
    if isinstance(res_stats_3.get("body"), str):
        bs3 = json.loads(res_stats_3["body"])
    tc3 = bs3.get("counts", {}).get("total")
    print("STATS_FINAL", res_stats_3["statusCode"], tc3)


if __name__ == "__main__":
    run()
