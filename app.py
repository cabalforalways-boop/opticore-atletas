# app.py - API de Optimización para Consultoría
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ← Agregar esto
from schemas import OptimizationRequest, OptimizationResponse
from router import classify_and_route
from executor import solve_generic_model
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OptiCore | Motor de Optimización Consultiva", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:42000",  # Flutter Web default
        "http://127.0.0.1:42000",
        "http://localhost:*",       # Cualquier puerto localhost (desarrollo)
        "*",                        # Permite todos los orígenes (solo desarrollo)
    ],
    allow_credentials=True,
    allow_methods=["*"],            # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],            # Permite todos los headers
)

@app.get("/health")
def health():
    return {"status": "ok", "engine": "scipy.optimize.milp"}

@app.post("/optimize", response_model=OptimizationResponse)
def optimize(req: OptimizationRequest):
    try:
        req_dict = req.model_dump()
        solver_cfg = classify_and_route(req_dict)
        logger.info(f"Recibido: clase={solver_cfg['class']}, vars={len(req.variables)}, constraints={len(req.constraints)}")
        
        result = solve_generic_model(req_dict, solver_cfg)
        return OptimizationResponse(**result)
    except Exception as e:
        logger.error(f"Error en /optimize: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error de optimización: {str(e)}")