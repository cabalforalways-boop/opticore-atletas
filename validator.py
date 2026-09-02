# validator.py — OptiCore Avícola v2.2 (pipeline unificado)
# ✅ coeffs siempre llegan como dict[str, float] (el schema los normaliza).
#    Se conserva compatibilidad legacy con string JSON por si se llama directo.
import json
from typing import Dict, Any


def validate_model(payload: Dict[str, Any]) -> Dict[str, Any]:
    issues, warnings, metrics = [], [], {}
    vars_list  = payload.get("variables", [])
    cons_list  = payload.get("constraints", [])
    obj        = payload.get("objective", {})
    n_vars     = len(vars_list)
    n_cons     = len(cons_list)

    # ── Variables ──────────────────────────────────────────────────────────────
    var_names = [v["name"] for v in vars_list]
    if len(var_names) != len(set(var_names)):
        issues.append("Variables duplicadas.")
    if n_vars == 0:
        issues.append("Sin variables.")
    if not obj or all(v == 0 for v in obj.values()):
        warnings.append("Objetivo nulo: todos los coeficientes son 0.")

    # ── Coeficientes (escala numérica) ─────────────────────────────────────────
    all_coeffs = []
    for v in vars_list:
        vname = v["name"]
        if vname in obj:
            all_coeffs.append(abs(float(obj[vname])))

    for c in cons_list:
        raw = c.get("coeffs", {})
        # Normalizar: aceptar dict o string JSON (compatibilidad)
        if isinstance(raw, str):
            try:
                coeffs = json.loads(raw)
            except Exception:
                coeffs = {}
        else:
            coeffs = raw  # ya es dict

        vals = [abs(float(val)) for val in coeffs.values()]
        all_coeffs.extend(v for v in vals if v > 1e-12)

        rhs = float(c.get("rhs", 0))
        if all(v < 1e-12 for v in vals) and abs(rhs) > 1e-6:
            issues.append(f"Restricción inconsistente (coefs nulos, rhs≠0): {c.get('name')}")

    if all_coeffs:
        mn, mx = min(all_coeffs), max(all_coeffs)
        ratio  = mx / (mn + 1e-12)
        metrics["coef_ratio"] = ratio
        if ratio > 1e6:
            warnings.append("DESESCALA NUMÉRICA: relación máx/mín de coeficientes > 1e6.")

    # ── Densidad (nunca > 100 %) ───────────────────────────────────────────────
    non_zero = 0
    for c in cons_list:
        raw = c.get("coeffs", {})
        coeffs = json.loads(raw) if isinstance(raw, str) else raw
        non_zero += sum(1 for val in coeffs.values() if abs(float(val)) > 1e-12)

    max_possible = n_vars * n_cons if (n_vars and n_cons) else 1
    density = round(min(100.0, (non_zero / max_possible) * 100), 1)
    metrics.update({"n_variables": n_vars, "n_constraints": n_cons, "density": density})

    # ── Status ─────────────────────────────────────────────────────────────────
    if issues:
        status = "❌ INVÁLIDO"
    elif warnings:
        status = "⚠️ ADVERTENCIAS"
    else:
        status = "✅ VÁLIDO"

    return {"status": status, "issues": issues, "warnings": warnings, "metrics": metrics}
