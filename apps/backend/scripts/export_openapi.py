# START_MODULE_CONTRACT
#   PURPOSE: Export the FastAPI OpenAPI schema to contracts/openapi.json (the API contract).
#   SCOPE: CLI script; --check exits 1 when the committed contract drifted from code.
#   DEPENDS: M-BACKEND-API
#   LINKS: M-API-CONTRACT, V-M-API-CONTRACT
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   CONTRACT - path to contracts/openapi.json
#   main     - write or --check the contract
# END_MODULE_MAP
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("KEITARO_BASE_URL", "https://example.invalid")
os.environ.setdefault("KEITARO_API_KEY", "contract-export")

from app.main import create_app

CONTRACT = Path(__file__).resolve().parents[3] / "contracts" / "openapi.json"


def main() -> int:
    rendered = json.dumps(create_app().openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        if not CONTRACT.exists() or CONTRACT.read_text(encoding="utf-8") != rendered:
            print(f"API contract drift: run `make openapi` and commit {CONTRACT.name}", file=sys.stderr)
            return 1
        print("API contract is up to date")
        return 0
    CONTRACT.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT.write_text(rendered, encoding="utf-8")
    print(f"wrote {CONTRACT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
