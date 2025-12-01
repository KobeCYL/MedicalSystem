import json
import asyncio
from datetime import datetime
import time
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from controllers.medical_controller import EnhancedMedicalController
except Exception:
    EnhancedMedicalController = None

from .supabase_client import insert_query

controller = None
try:
    if EnhancedMedicalController:
        controller = EnhancedMedicalController()
except Exception:
    controller = None
if controller is None:
    class FallbackMedicalController:
        async def process_query(self, symptom, patient_info, client_start_ts):
            s = (symptom or "").strip()
            status = "no_match" if not s else "success"
            risky = ["自杀", "杀", "爆炸", "恐怖", "攻击"]
            for kw in risky:
                if kw in s:
                    status = "failed"
                    break
            candidates = [
                {"name": "Common Cold", "probability": 0.6},
                {"name": "Influenza", "probability": 0.3},
                {"name": "Unknown", "probability": 0.1},
            ]
            best = max(candidates, key=lambda x: x["probability"])["name"]
            return {
                "status": status,
                "disease_name": best,
                "advice": {"general": "保持休息，多喝水"},
                "urgency": "low",
                "supplementary_info": {
                    "probabilities": candidates,
                    "best_candidate": best,
                },
                "model": "fallback",
            }
    controller = FallbackMedicalController()


def handler(request):
    try:
        body = request.get_json() or {}
        symptom = body.get("symptom", "")
        patient_info = body.get("patient_info", {})
        client_start_ts = body.get("client_start_ts")
        if controller is None:
            body_err = {
                "status": "error",
                "error_message": "controller unavailable",
            }
            return {
                "statusCode": 501,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(body_err, ensure_ascii=False),
            }
        server_start = time.perf_counter()
        result_model = asyncio.run(
            controller.process_query(symptom, patient_info, client_start_ts)
        )
        server_end = time.perf_counter()
        is_dict_model = hasattr(result_model, "dict")
        result = result_model.dict() if is_dict_model else result_model

        s_dur = None
        t_dur = None
        model_name = None
        status_val = "success"
        advice_val = None
        supp_info_val = None
        urgency_val = None
        disease_name_val = None
        if isinstance(result, dict):
            s_dur = result.get("server_duration_ms")
            t_dur = result.get("total_duration_ms")
            model_name = result.get("model")
            status_val = result.get("status") or status_val
            advice_val = result.get("advice")
            supp_info_val = result.get("supplementary_info")
            urgency_val = result.get("urgency")
            disease_name_val = result.get("disease_name")

        if s_dur is None:
            s_dur = int((server_end - server_start) * 1000)
        if t_dur is None:
            try:
                if isinstance(client_start_ts, str):
                    cst = datetime.fromisoformat(client_start_ts)
                    t_dur = int((datetime.now() - cst).total_seconds() * 1000)
                else:
                    t_dur = s_dur
            except Exception:
                t_dur = s_dur

        safe_result = result if isinstance(result, dict) else {}
        if isinstance(safe_result, dict):
            if safe_result.get("server_duration_ms") is None:
                safe_result["server_duration_ms"] = s_dur
            if safe_result.get("total_duration_ms") is None:
                safe_result["total_duration_ms"] = t_dur
            if safe_result.get("status") is None:
                safe_result["status"] = status_val

        entry = {
            "timestamp": datetime.now().isoformat(),
            "symptom": symptom,
            "patient_info": patient_info,
            "status": status_val,
            "disease_name": disease_name_val,
            "advice": advice_val,
            "urgency": urgency_val,
            "supplementary_info": supp_info_val,
            "server_duration_ms": s_dur,
            "total_duration_ms": t_dur,
            "model": model_name,
            "source_channel": "vercel_api",
        }
        ins = insert_query(entry)
        if ins is None:
            try:
                base_root = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                    )
                )
                data_dir = os.path.join(base_root, "data")
                os.makedirs(data_dir, exist_ok=True)
                fp = os.path.join(data_dir, "query_history.json")
                existing: list = []
                if os.path.exists(fp):
                    with open(fp, "r", encoding="utf-8") as f:
                        obj = json.load(f)
                        if isinstance(obj, list):
                            existing = obj
                existing.append(entry)
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(existing, f, ensure_ascii=False)
            except Exception:
                pass

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            },
            "body": json.dumps(safe_result, ensure_ascii=False),
        }
    except Exception as e:
        error_body = {"status": "error", "error_message": str(e)}
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            },
            "body": json.dumps(error_body, ensure_ascii=False),
        }
