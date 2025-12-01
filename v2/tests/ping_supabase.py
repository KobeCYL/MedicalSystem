import os
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def run():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("ENV_MISSING")
        return
    base = f"{url}/rest/v1/queries"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    params = {"select": "*", "limit": "1"}
    r = requests.get(base, headers=headers, params=params)
    print("STATUS", r.status_code)
    try:
        data = r.json()
        print("JSON", isinstance(data, list))
    except Exception:
        print("NON_JSON")


if __name__ == "__main__":
    run()
