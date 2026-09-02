# schemas.py — OptiCore Avícola v2.2 (pipeline unificado)
# ✅ Tipos y estructuras canónicos para todo el flujo UI → API → Solver → Validador
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Any


class Variable(BaseModel):
    name: str
    type: Literal["continuous", "integer", "binary"]
    lb: float = 0.0
    ub: Optional[float] = None          # None → sin límite superior (np.inf en el solver)
    obj_coef: float                      # coeficiente de costo / contribución al objetivo


class Constraint(BaseModel):
    name: str
    sense: Literal["<=", ">=", "=="]
    rhs: float
    coeffs: dict[str, float]            # ✅ siempre dict[str, float]; nunca string JSON

    @field_validator("coeffs", mode="before")
    @classmethod
    def parse_coeffs(cls, v):
        """Acepta string JSON legacy del editor Streamlit y lo convierte a dict."""
        import json
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return {str(k): float(val) for k, val in parsed.items()}
            except Exception as exc:
                raise ValueError(f"coeffs no es JSON válido: {exc}") from exc
        if isinstance(v, dict):
            return {str(k): float(val) for k, val in v.items()}
        raise ValueError(f"coeffs debe ser dict o string JSON, no {type(v)}")


class OptimizationRequest(BaseModel):
    sense: Literal["min", "max"]
    objective: dict[str, float]         # {nombre_var: coeficiente_objetivo}
    variables: list[Variable]
    constraints: list[Constraint]
    time_limit_sec: Optional[int] = 60
    metadata: Optional[dict[str, Any]] = None


class OptimizationResponse(BaseModel):
    status: str
    objective_value: float
    solution: dict[str, float]
    solver_used: str
    problem_class: str
    diagnostics: dict[str, Any]
