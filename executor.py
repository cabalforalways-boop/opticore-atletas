# executor.py — OptiCore Avícola v2.2 (pipeline unificado)
# ✅ LP puro → scipy.optimize.linprog  (maneja mejor problemas en el límite de factibilidad)
# ✅ MILP     → scipy.optimize.milp    (compatible SciPy >= 1.11; integrality en milp, no en Bounds)
# ✅ Conversión NumPy→Python nativa     (compatible NumPy >= 2.0)
import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds
import logging

logger = logging.getLogger(__name__)


def convert_to_python(obj):
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_to_python(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_to_python(item) for item in obj]
    if obj is None or isinstance(obj, (str, bool, int, float)):
        return obj
    try:
        return str(obj)
    except Exception:
        return None


def _solve_lp(var_names, c_min, lb_v, ub_v, constraints, time_limit):
    """LP puro via linprog (forma estándar A_eq/A_ub)."""
    A_eq_rows, b_eq = [], []
    A_ub_rows, b_ub = [], []

    for con in constraints:
        coeffs = con.get("coeffs", {})
        sense  = con.get("sense", "<=")
        rhs    = float(con.get("rhs", 0))
        row    = [float(coeffs.get(vn, 0.0)) for vn in var_names]

        if sense == "==":
            A_eq_rows.append(row); b_eq.append(rhs)
        elif sense == "<=":
            A_ub_rows.append(row); b_ub.append(rhs)
        elif sense == ">=":
            A_ub_rows.append([-v for v in row]); b_ub.append(-rhs)

    kwargs = {
        "c":       c_min,
        "bounds":  list(zip(lb_v, [u if u != np.inf else None for u in ub_v])),
        "method":  "highs",
        "options": {"time_limit": time_limit, "presolve": True, "disp": False},
    }
    if A_eq_rows:
        kwargs["A_eq"] = np.array(A_eq_rows, dtype=float)
        kwargs["b_eq"] = np.array(b_eq,      dtype=float)
    if A_ub_rows:
        kwargs["A_ub"] = np.array(A_ub_rows, dtype=float)
        kwargs["b_ub"] = np.array(b_ub,      dtype=float)

    return linprog(**kwargs)


def _solve_milp(var_names, c_min, lb_v, ub_v, integrality, constraints, time_limit):
    """MILP via milp (SciPy >= 1.11; integrality directamente en milp)."""
    A_rows, lb_c, ub_c = [], [], []

    for con in constraints:
        coeffs = con.get("coeffs", {})
        sense  = con.get("sense", "<=")
        rhs    = float(con.get("rhs", 0))
        row    = [float(coeffs.get(vn, 0.0)) for vn in var_names]

        A_rows.append(row)
        if sense == "<=":
            lb_c.append(-np.inf); ub_c.append(rhs)
        elif sense == ">=":
            lb_c.append(rhs);     ub_c.append(np.inf)
        elif sense == "==":
            lb_c.append(rhs);     ub_c.append(rhs)

    bounds = Bounds(lb=lb_v, ub=ub_v)
    lc     = LinearConstraint(np.array(A_rows, dtype=float), lb_c, ub_c)

    return milp(
        c=np.array(c_min, dtype=float),
        constraints=lc,
        bounds=bounds,
        integrality=np.array(integrality, dtype=int),
        options={"time_limit": time_limit, "presolve": True, "disp": False},
    )


def solve_generic_model(req: dict, solver_cfg: dict) -> dict:
    """Resuelve LP o MILP según el tipo de variables."""
    sense       = req.get("sense", "min")
    variables   = req.get("variables", [])
    constraints = req.get("constraints", [])
    obj_coefs   = req.get("objective", {})
    time_limit  = float(req.get("time_limit_sec", 60))

    var_names = [v["name"] for v in variables]
    c_raw     = [float(obj_coefs.get(vn, 0.0)) for vn in var_names]
    c_min     = c_raw if sense == "min" else [-x for x in c_raw]

    lb_v = [float(v.get("lb", 0.0))                               for v in variables]
    ub_v = [float(v["ub"]) if v.get("ub") is not None else np.inf for v in variables]

    integrality, has_int = [], False
    for v in variables:
        vtype = v.get("type", "continuous")
        if vtype == "binary":
            integrality.append(1); has_int = True
        elif vtype == "integer":
            integrality.append(2); has_int = True
        else:
            integrality.append(0)

    try:
        if has_int:
            result     = _solve_milp(var_names, c_min, lb_v, ub_v, integrality, constraints, time_limit)
            solver_tag = "scipy.milp"
        else:
            result     = _solve_lp(var_names, c_min, lb_v, ub_v, constraints, time_limit)
            solver_tag = "scipy.linprog"

        # linprog: status 0=ok,1=inf,2=unbounded,3=iter,4=num  | milp: 0=ok,1=inf,2=unbnd,3=inf_or_unb,4=lim
        status_map = {0: "optimal", 1: "infeasible", 2: "infeasible",
                      3: "infeasible_or_unbounded", 4: "limited"}
        raw_status = int(result.status) if hasattr(result, "status") else -1
        status     = status_map.get(raw_status, "unknown")

        solution: dict = {}
        if result.x is not None:
            for i, vn in enumerate(var_names):
                solution[vn] = convert_to_python(float(result.x[i]))

        obj_val = float(result.fun) if result.fun is not None else 0.0
        if sense == "max":
            obj_val = -obj_val

        response = {
            "status":          status,
            "objective_value": convert_to_python(obj_val),
            "solution":        solution,
            "solver_used":     solver_tag,
            "problem_class":   solver_cfg.get("class", "LP"),
            "diagnostics": {
                "iterations": convert_to_python(getattr(result, "nit", None)),
                "feasible":   convert_to_python(getattr(result, "success", False)),
                "message":    convert_to_python(getattr(result, "message", "")),
            },
        }
        logger.info(f"✅ Resuelto ({solver_tag}): status={status}, obj={obj_val:.4f}")
        return response

    except Exception as exc:
        logger.error(f"❌ Error en solver: {exc}", exc_info=True)
        raise
