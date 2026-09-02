# router.py - Enrutador genérico LP/MILP
from typing import Dict, Any

def classify_problem(req: dict) -> str:
    has_int = any(v.get("type") in ("integer", "binary") for v in req.get("variables", []))
    return "MILP" if has_int else "LP"

def classify_and_route(req: dict) -> Dict[str, Any]:
    problem_class = req.get("problem_type") if req.get("problem_type") not in (None, "auto") else classify_problem(req)
    routing_map = {
        "LP":   {"solver": "scipy", "options": {"time_limit": req.get("time_limit_sec", 60)}},
        "MILP": {"solver": "scipy", "options": {"time_limit": req.get("time_limit_sec", 120)}}
    }
    if req.get("solver_hint"):
        routing_map[problem_class]["solver"] = req["solver_hint"].lower()
    return {"class": problem_class, "config": routing_map[problem_class]}