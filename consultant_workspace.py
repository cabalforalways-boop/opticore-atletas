# consultant_workspace.py — OptiCore Atletas v1.0
# Dieta personalizada para atletas: 4 perfiles (Fuerza, Resistencia, Definición, Recuperación)
# ✅ Base científica: ISSN Position Stand 2017, ACSM 2016, Thomas et al. 2016
# ✅ Unidad del modelo: 1 kg de alimento diario (misma mecánica LP que módulo avícola)
# ✅ Todos los widgets con key= único → sin Network issue en sidebar
# ✅ Compatible 100% con app.py (claves en inglés, payload estándar OptiCore)

import streamlit as st
import requests
import pandas as pd
import json
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from validator import validate_model

API_URL = "http://127.0.0.1:8000/optimize"

st.set_page_config(
    page_title="OptiCore Atletas | Dieta de Precisión",
    layout="wide",
    page_icon="🏋️"
)
st.title("🏋️ OptiCore Atletas — Formulación de Dietas de Precisión")
st.caption(
    "Optimización matemática para 4 perfiles deportivos: "
    "Fuerza/Volumen · Resistencia/Cardio · Definición/Corte · Recuperación Post-Entrenamiento"
)

# =============================================================================
# 🔹 BASE NUTRICIONAL DE ALIMENTOS
# Fuente: USDA FoodData Central + literatura de nutrición deportiva
# Unidad de coeficientes: por kg de alimento crudo/preparado
# =============================================================================
# Columnas: kcal/kg  prot_g/kg  cho_g/kg  grasa_g/kg  fibra_g/kg  omega3_g/kg  costo_USD/kg
ALIMENTOS_DB = {
    # ── CARBOHIDRATOS COMPLEJOS ───────────────────────────────────────────────
    "Avena":           {"kcal": 3890, "prot": 131, "cho": 668, "grasa":  66, "fibra": 100, "omega3":  1.0, "costo":  1.50, "grupo": "CHO", "emoji": "🌾"},
    "Arroz_Blanco":    {"kcal": 3640, "prot":  71, "cho": 800, "grasa":   6, "fibra":   2, "omega3":  0.1, "costo":  1.20, "grupo": "CHO", "emoji": "🍚"},
    "Batata":          {"kcal":  860, "prot":  16, "cho": 201, "grasa":   1, "fibra":  30, "omega3":  0.1, "costo":  1.80, "grupo": "CHO", "emoji": "🍠"},
    "Quinoa":          {"kcal": 3680, "prot": 141, "cho": 640, "grasa":  60, "fibra":  70, "omega3":  0.8, "costo":  8.00, "grupo": "CHO", "emoji": "🌿"},
    "Pan_Integral":    {"kcal": 2470, "prot":  90, "cho": 461, "grasa":  31, "fibra":  60, "omega3":  0.5, "costo":  3.00, "grupo": "CHO", "emoji": "🍞"},
    "Platano":         {"kcal":  890, "prot":  11, "cho": 229, "grasa":   3, "fibra":  26, "omega3":  0.3, "costo":  1.50, "grupo": "CHO", "emoji": "🍌"},
    # ── PROTEÍNAS MAGRAS ─────────────────────────────────────────────────────
    "Pechuga_Pollo":   {"kcal": 1650, "prot": 310, "cho":   0, "grasa":  36, "fibra":   0, "omega3":  0.2, "costo":  8.00, "grupo": "PROT", "emoji": "🍗"},
    "Atun_Lata":       {"kcal": 1160, "prot": 260, "cho":   0, "grasa":  13, "fibra":   0, "omega3":  5.5, "costo":  6.00, "grupo": "PROT", "emoji": "🐟"},
    "Salmon":          {"kcal": 2080, "prot": 200, "cho":   0, "grasa": 130, "fibra":   0, "omega3": 22.0, "costo": 18.00, "grupo": "PROT", "emoji": "🐠"},
    "Huevo_Entero":    {"kcal": 1430, "prot": 126, "cho":   7, "grasa":  97, "fibra":   0, "omega3":  1.0, "costo":  4.00, "grupo": "PROT", "emoji": "🥚"},
    "Claras_Huevo":    {"kcal":  520, "prot": 109, "cho":   7, "grasa":   2, "fibra":   0, "omega3":  0.1, "costo":  5.00, "grupo": "PROT", "emoji": "🥛"},
    "Proteina_Whey":   {"kcal": 3600, "prot": 800, "cho":  75, "grasa":  30, "fibra":   0, "omega3":  1.0, "costo": 25.00, "grupo": "PROT", "emoji": "🥤"},
    "Caseina":         {"kcal": 3600, "prot": 800, "cho":  30, "grasa":  10, "fibra":   0, "omega3":  1.0, "costo": 28.00, "grupo": "PROT", "emoji": "🧪"},
    # ── LÁCTEOS ──────────────────────────────────────────────────────────────
    "Leche_Descremada":{"kcal":  350, "prot":  35, "cho":  51, "grasa":   1, "fibra":   0, "omega3":  0.1, "costo":  1.00, "grupo": "LACT", "emoji": "🥛"},
    "Yogur_Griego":    {"kcal":  590, "prot": 100, "cho":  38, "grasa":   9, "fibra":   0, "omega3":  0.2, "costo":  5.00, "grupo": "LACT", "emoji": "🫙"},
    # ── GRASAS SALUDABLES ────────────────────────────────────────────────────
    "Aceite_Oliva":    {"kcal": 8840, "prot":   0, "cho":   0, "grasa":1000, "fibra":   0, "omega3":  1.0, "costo": 12.00, "grupo": "GRASA", "emoji": "🫒"},
    "Almendras":       {"kcal": 5780, "prot": 213, "cho": 216, "grasa": 500, "fibra": 125, "omega3":  0.4, "costo": 14.00, "grupo": "GRASA", "emoji": "🥜"},
    # ── VEGETALES ────────────────────────────────────────────────────────────
    "Brocoli":         {"kcal":  340, "prot":  28, "cho":  66, "grasa":   4, "fibra":  26, "omega3":  0.2, "costo":  3.00, "grupo": "VEG", "emoji": "🥦"},
    "Espinaca":        {"kcal":  230, "prot":  29, "cho":  36, "grasa":   4, "fibra":  22, "omega3":  0.5, "costo":  4.00, "grupo": "VEG", "emoji": "🥬"},
    "Manzana":         {"kcal":  520, "prot":   3, "cho": 138, "grasa":   2, "fibra":  24, "omega3":  0.1, "costo":  2.00, "grupo": "VEG", "emoji": "🍎"},
}

def _var(name, ub, costo):
    """Construye una variable continua estándar."""
    a = ALIMENTOS_DB[name]
    return {
        "name":     name,
        "type":     "continuous",
        "lb":       0.0,
        "ub":       ub,
        "obj_coef": costo if costo is not None else a["costo"],
    }

def _coeffs(nutriente, nombres):
    """Devuelve dict de coeficientes de un nutriente para los alimentos dados."""
    factor = {"kcal": 1/1000, "prot": 1/1000, "cho": 1/1000,
              "grasa": 1/1000, "fibra": 1/1000, "omega3": 1/1000}[nutriente]
    return {n: ALIMENTOS_DB[n][nutriente] * factor for n in nombres
            if ALIMENTOS_DB[n][nutriente] > 0}

# =============================================================================
# 🔹 PLANTILLAS DE ATLETAS
# Base = 1 kg de alimento total (fracción decimals de kg por alimento)
# Requerimientos por kg de dieta diaria (atleta referencia 75-85 kg, 2-3 kg/día)
#
# Conversión: atleta fuerza 80 kg come ~2.5 kg/día
#   Proteína target: 2.0 g/kg_corporal = 160 g/día ÷ 2500 g = 0.064 fracción/kg dieta
#   Energía: 3200 kcal ÷ 2500 g = 1.28 Mcal/kg dieta
# =============================================================================
TEMPLATES = {

    # ── PERFIL 1: FUERZA Y VOLUMEN ────────────────────────────────────────────
    "fuerza_volumen": {
        "name": "💪 Fuerza y Volumen Muscular",
        "sense": "min",
        "description": (
            "Atleta de fuerza (powerlifting, halterofilia, rugby) en fase de ganancia muscular. "
            "Alta proteína (1.8-2.2 g/kg/día) + CHO moderado-alto para síntesis proteica. "
            "Base científica: ISSN 2017 — Jäger et al."
        ),
        "perfil": {
            "objetivo": "Maximizar síntesis proteica con costo mínimo",
            "peso_referencia": "80 kg",
            "kcal_dia": "3,200 kcal",
            "prot_dia": "160 g (2.0 g/kg/día)",
            "cho_dia": "400 g (5.0 g/kg/día)",
            "grasa_dia": "96 g (1.2 g/kg/día)",
        },
        "variables": [
            _var("Avena",          0.40,  None),
            _var("Arroz_Blanco",   0.35,  None),
            _var("Batata",         0.30,  None),
            _var("Quinoa",         0.20,  None),
            _var("Pechuga_Pollo",  0.40,  None),
            _var("Huevo_Entero",   0.25,  None),
            _var("Claras_Huevo",   0.30,  None),
            _var("Proteina_Whey",  0.10,  None),
            _var("Yogur_Griego",   0.30,  None),
            _var("Leche_Descremada",0.30, None),
            _var("Salmon",         0.15,  None),
            _var("Almendras",      0.08,  None),
            _var("Brocoli",        0.20,  None),
            _var("Platano",        0.20,  None),
        ],
        "constraints": [
            # Peso total = 1 kg de dieta diaria (base normalizada)
            {"name": "Peso_Total",    "sense": "==", "rhs": 1.0,
             "coeffs": {n: 1.0 for n in ["Avena","Arroz_Blanco","Batata","Quinoa",
                        "Pechuga_Pollo","Huevo_Entero","Claras_Huevo","Proteina_Whey",
                        "Yogur_Griego","Leche_Descremada","Salmon","Almendras","Brocoli","Platano"]}},
            # Energía mínima: 3200 kcal/día ÷ 2500 g/día = 1.28 Mcal/kg dieta
            {"name": "Energia_Min",   "sense": ">=", "rhs": 1.28,
             "coeffs": _coeffs("kcal", ["Avena","Arroz_Blanco","Batata","Quinoa",
                        "Pechuga_Pollo","Huevo_Entero","Claras_Huevo","Proteina_Whey",
                        "Yogur_Griego","Leche_Descremada","Salmon","Almendras","Brocoli","Platano"])},
            # Proteína mínima: 160 g/día ÷ 2500 g = 0.064 g_prot/g_dieta
            {"name": "Proteina_Min",  "sense": ">=", "rhs": 0.064,
             "coeffs": _coeffs("prot", ["Avena","Arroz_Blanco","Batata","Quinoa",
                        "Pechuga_Pollo","Huevo_Entero","Claras_Huevo","Proteina_Whey",
                        "Yogur_Griego","Leche_Descremada","Salmon","Almendras","Brocoli","Platano"])},
            # CHO mínimo: 400 g/día ÷ 2500 g = 0.160
            {"name": "CHO_Min",       "sense": ">=", "rhs": 0.160,
             "coeffs": _coeffs("cho", ["Avena","Arroz_Blanco","Batata","Quinoa",
                        "Pechuga_Pollo","Huevo_Entero","Claras_Huevo","Proteina_Whey",
                        "Yogur_Griego","Leche_Descremada","Salmon","Almendras","Brocoli","Platano"])},
            # Grasa mínima: 96 g/día ÷ 2500 g = 0.038 (al menos 30% de kcal de grasas saludables)
            {"name": "Grasa_Min",     "sense": ">=", "rhs": 0.030,
             "coeffs": _coeffs("grasa", ["Avena","Arroz_Blanco","Batata","Quinoa",
                        "Pechuga_Pollo","Huevo_Entero","Claras_Huevo","Proteina_Whey",
                        "Yogur_Griego","Leche_Descremada","Salmon","Almendras","Brocoli","Platano"])},
            # Fibra mínima: 35 g/día ÷ 2500 g = 0.014 (salud intestinal)
            {"name": "Fibra_Min",     "sense": ">=", "rhs": 0.014,
             "coeffs": _coeffs("fibra", ["Avena","Arroz_Blanco","Batata","Quinoa",
                        "Almendras","Brocoli","Platano"])},
            # Control de grasas totales (máx 120 g/día ÷ 2500 = 0.048)
            {"name": "Grasa_Max",     "sense": "<=", "rhs": 0.048,
             "coeffs": _coeffs("grasa", ["Avena","Arroz_Blanco","Batata","Quinoa",
                        "Pechuga_Pollo","Huevo_Entero","Claras_Huevo","Proteina_Whey",
                        "Yogur_Griego","Leche_Descremada","Salmon","Almendras","Brocoli","Platano"])},
            # Diversidad: al menos un alimento del grupo proteico magro
            {"name": "Min_Proteina_Magra", "sense": ">=", "rhs": 0.10,
             "coeffs": {"Pechuga_Pollo": 1.0, "Claras_Huevo": 1.0, "Salmon": 1.0}},
            # Max suplemento (whey ≤ 10% de la dieta total)
            {"name": "Max_Whey",      "sense": "<=", "rhs": 0.10,
             "coeffs": {"Proteina_Whey": 1.0}},
            # Verduras mínimo (micronutrientes y fibra)
            {"name": "Min_Verduras",  "sense": ">=", "rhs": 0.08,
             "coeffs": {"Brocoli": 1.0}},
        ],
    },

    # ── PERFIL 2: RESISTENCIA Y CARDIO ────────────────────────────────────────
    "resistencia_cardio": {
        "name": "🏃 Resistencia y Cardio (Fondo)",
        "sense": "min",
        "description": (
            "Atleta de resistencia (maratón, ciclismo, triatlón) en fase de entrenamiento de base. "
            "Alta carga de CHO (6-8 g/kg/día) para glucógeno muscular. "
            "Base científica: Burke et al. 2011, Thomas et al. 2016."
        ),
        "perfil": {
            "objetivo": "Maximizar depósitos de glucógeno con costo mínimo",
            "peso_referencia": "65 kg",
            "kcal_dia": "3,900 kcal",
            "prot_dia": "104 g (1.6 g/kg/día)",
            "cho_dia":  "520 g (8.0 g/kg/día)",
            "grasa_dia": "78 g (1.2 g/kg/día)",
        },
        "variables": [
            _var("Avena",          0.45,  None),
            _var("Arroz_Blanco",   0.45,  None),
            _var("Batata",         0.40,  None),
            _var("Pan_Integral",   0.30,  None),
            _var("Platano",        0.30,  None),
            _var("Pechuga_Pollo",  0.30,  None),
            _var("Atun_Lata",      0.20,  None),
            _var("Huevo_Entero",   0.20,  None),
            _var("Proteina_Whey",  0.08,  None),
            _var("Leche_Descremada",0.35, None),
            _var("Yogur_Griego",   0.25,  None),
            _var("Aceite_Oliva",   0.04,  None),
            _var("Manzana",        0.25,  None),
            _var("Brocoli",        0.20,  None),
        ],
        "constraints": [
            {"name": "Peso_Total",    "sense": "==", "rhs": 1.0,
             "coeffs": {n: 1.0 for n in ["Avena","Arroz_Blanco","Batata","Pan_Integral","Platano",
                        "Pechuga_Pollo","Atun_Lata","Huevo_Entero","Proteina_Whey",
                        "Leche_Descremada","Yogur_Griego","Aceite_Oliva","Manzana","Brocoli"]}},
            # Energía alta: 3900 kcal/día ÷ 3000 g/día = 1.30 Mcal/kg
            {"name": "Energia_Min",   "sense": ">=", "rhs": 1.30,
             "coeffs": _coeffs("kcal", ["Avena","Arroz_Blanco","Batata","Pan_Integral","Platano",
                        "Pechuga_Pollo","Atun_Lata","Huevo_Entero","Proteina_Whey",
                        "Leche_Descremada","Yogur_Griego","Aceite_Oliva","Manzana","Brocoli"])},
            # Proteína moderada: 104 g ÷ 3000 g = 0.035
            {"name": "Proteina_Min",  "sense": ">=", "rhs": 0.035,
             "coeffs": _coeffs("prot", ["Avena","Arroz_Blanco","Batata","Pan_Integral","Platano",
                        "Pechuga_Pollo","Atun_Lata","Huevo_Entero","Proteina_Whey",
                        "Leche_Descremada","Yogur_Griego","Aceite_Oliva","Manzana","Brocoli"])},
            # CHO alto: 520 g ÷ 3000 g = 0.173
            {"name": "CHO_Min",       "sense": ">=", "rhs": 0.173,
             "coeffs": _coeffs("cho", ["Avena","Arroz_Blanco","Batata","Pan_Integral","Platano",
                        "Pechuga_Pollo","Atun_Lata","Huevo_Entero","Proteina_Whey",
                        "Leche_Descremada","Yogur_Griego","Aceite_Oliva","Manzana","Brocoli"])},
            # Grasas saludables mínimo: 78 g ÷ 3000 = 0.026
            {"name": "Grasa_Min",     "sense": ">=", "rhs": 0.020,
             "coeffs": _coeffs("grasa", ["Avena","Arroz_Blanco","Batata","Pan_Integral","Platano",
                        "Pechuga_Pollo","Atun_Lata","Huevo_Entero","Proteina_Whey",
                        "Leche_Descremada","Yogur_Griego","Aceite_Oliva","Manzana","Brocoli"])},
            # Omega-3 mínimo (antiinflamatorio, recuperación muscular): 2 g/día ÷ 3000 g = 0.00067
            {"name": "Omega3_Min",    "sense": ">=", "rhs": 0.00067,
             "coeffs": _coeffs("omega3", ["Atun_Lata","Huevo_Entero","Proteina_Whey",
                        "Leche_Descremada","Yogur_Griego","Aceite_Oliva","Brocoli"])},
            # Fibra: 38 g/día ÷ 3000 g = 0.013
            {"name": "Fibra_Min",     "sense": ">=", "rhs": 0.013,
             "coeffs": _coeffs("fibra", ["Avena","Batata","Pan_Integral","Platano","Manzana","Brocoli"])},
            # Diversidad de CHO (al menos 2 fuentes): arroz+avena juntos ≥ 30%
            {"name": "Min_CHO_Complejos", "sense": ">=", "rhs": 0.25,
             "coeffs": {"Avena": 1.0, "Arroz_Blanco": 1.0, "Batata": 1.0}},
            # Aceite oliva: pequeña cantidad pero presente (grasas monoinsaturadas)
            {"name": "Min_AceiteOliva", "sense": ">=", "rhs": 0.01,
             "coeffs": {"Aceite_Oliva": 1.0}},
            {"name": "Max_AceiteOliva", "sense": "<=", "rhs": 0.04,
             "coeffs": {"Aceite_Oliva": 1.0}},
            # Max whey
            {"name": "Max_Whey",      "sense": "<=", "rhs": 0.08,
             "coeffs": {"Proteina_Whey": 1.0}},
        ],
    },

    # ── PERFIL 3: DEFINICIÓN Y CORTE ──────────────────────────────────────────
    "definicion_corte": {
        "name": "🔥 Definición y Reducción de Grasa Corporal",
        "sense": "min",
        "description": (
            "Atleta en fase de corte (culturismo, artes marciales, deportes de peso). "
            "Alta proteína para preservar masa muscular en déficit calórico. "
            "CHO bajo-moderado, grasas saludables controladas. "
            "Base: Helms et al. 2014 — 2.3-3.1 g/kg de masa magra."
        ),
        "perfil": {
            "objetivo": "Mínimo costo con máxima preservación muscular en déficit",
            "peso_referencia": "80 kg (15% grasa → 68 kg masa magra)",
            "kcal_dia": "2,200 kcal (déficit ~500 kcal)",
            "prot_dia": "190 g (2.8 g/kg masa magra)",
            "cho_dia":  "200 g (2.5 g/kg/día)",
            "grasa_dia": "55 g (0.7 g/kg/día)",
        },
        "variables": [
            _var("Avena",          0.25,  None),
            _var("Batata",         0.25,  None),
            _var("Quinoa",         0.20,  None),
            _var("Pechuga_Pollo",  0.45,  None),
            _var("Claras_Huevo",   0.40,  None),
            _var("Atun_Lata",      0.30,  None),
            _var("Salmon",         0.15,  None),
            _var("Proteina_Whey",  0.10,  None),
            _var("Caseina",        0.08,  None),
            _var("Yogur_Griego",   0.25,  None),
            _var("Brocoli",        0.35,  None),
            _var("Espinaca",       0.25,  None),
            _var("Manzana",        0.20,  None),
            _var("Almendras",      0.05,  None),
        ],
        "constraints": [
            {"name": "Peso_Total",    "sense": "==", "rhs": 1.0,
             "coeffs": {n: 1.0 for n in ["Avena","Batata","Quinoa","Pechuga_Pollo","Claras_Huevo",
                        "Atun_Lata","Salmon","Proteina_Whey","Caseina","Yogur_Griego",
                        "Brocoli","Espinaca","Manzana","Almendras"]}},
            # Energía controlada: 2200 kcal ÷ 2000 g/día = 1.10 Mcal/kg
            {"name": "Energia_Min",   "sense": ">=", "rhs": 0.90,
             "coeffs": _coeffs("kcal", ["Avena","Batata","Quinoa","Pechuga_Pollo","Claras_Huevo",
                        "Atun_Lata","Salmon","Proteina_Whey","Caseina","Yogur_Griego",
                        "Brocoli","Espinaca","Manzana","Almendras"])},
            # Energía máxima (déficit): 2400 kcal ÷ 2000 g = 1.20
            {"name": "Energia_Max",   "sense": "<=", "rhs": 1.20,
             "coeffs": _coeffs("kcal", ["Avena","Batata","Quinoa","Pechuga_Pollo","Claras_Huevo",
                        "Atun_Lata","Salmon","Proteina_Whey","Caseina","Yogur_Griego",
                        "Brocoli","Espinaca","Manzana","Almendras"])},
            # Proteína alta: 190 g ÷ 2000 g = 0.095
            {"name": "Proteina_Min",  "sense": ">=", "rhs": 0.095,
             "coeffs": _coeffs("prot", ["Avena","Batata","Quinoa","Pechuga_Pollo","Claras_Huevo",
                        "Atun_Lata","Salmon","Proteina_Whey","Caseina","Yogur_Griego",
                        "Brocoli","Espinaca","Manzana","Almendras"])},
            # CHO moderado bajo: 200 g ÷ 2000 g = 0.10
            {"name": "CHO_Min",       "sense": ">=", "rhs": 0.080,
             "coeffs": _coeffs("cho", ["Avena","Batata","Quinoa","Pechuga_Pollo","Claras_Huevo",
                        "Atun_Lata","Salmon","Proteina_Whey","Caseina","Yogur_Griego",
                        "Brocoli","Espinaca","Manzana","Almendras"])},
            # CHO máximo (control glucémico): 0.130
            {"name": "CHO_Max",       "sense": "<=", "rhs": 0.130,
             "coeffs": _coeffs("cho", ["Avena","Batata","Quinoa","Pechuga_Pollo","Claras_Huevo",
                        "Atun_Lata","Salmon","Proteina_Whey","Caseina","Yogur_Griego",
                        "Brocoli","Espinaca","Manzana","Almendras"])},
            # Grasas controladas: 55 g ÷ 2000 g = 0.028 máximo
            {"name": "Grasa_Max",     "sense": "<=", "rhs": 0.035,
             "coeffs": _coeffs("grasa", ["Avena","Batata","Quinoa","Pechuga_Pollo","Claras_Huevo",
                        "Atun_Lata","Salmon","Proteina_Whey","Caseina","Yogur_Griego",
                        "Brocoli","Espinaca","Manzana","Almendras"])},
            # Omega-3 (antiinflamatorio en déficit): 2 g ÷ 2000 g = 0.001
            {"name": "Omega3_Min",    "sense": ">=", "rhs": 0.001,
             "coeffs": _coeffs("omega3", ["Atun_Lata","Salmon","Almendras","Espinaca"])},
            # Fibra alta (saciedad): 30 g ÷ 2000 g = 0.015
            {"name": "Fibra_Min",     "sense": ">=", "rhs": 0.015,
             "coeffs": _coeffs("fibra", ["Avena","Batata","Quinoa","Brocoli","Espinaca","Manzana","Almendras"])},
            # Verduras mínimo (volumen, micronutrientes): 25% de la dieta
            {"name": "Min_Verduras",  "sense": ">=", "rhs": 0.20,
             "coeffs": {"Brocoli": 1.0, "Espinaca": 1.0}},
            # Caseína presente (absorción lenta, protege músculo nocturno)
            {"name": "Min_Caseina",   "sense": ">=", "rhs": 0.03,
             "coeffs": {"Caseina": 1.0}},
            # Almendras limitadas (calorías densas)
            {"name": "Max_Almendras", "sense": "<=", "rhs": 0.05,
             "coeffs": {"Almendras": 1.0}},
            # Max salmon (costo alto, pero necesario por omega-3)
            {"name": "Max_Salmon",    "sense": "<=", "rhs": 0.15,
             "coeffs": {"Salmon": 1.0}},
        ],
    },

    # ── PERFIL 4: RECUPERACIÓN POST-ENTRENAMIENTO ─────────────────────────────
    "recuperacion_post": {
        "name": "⚡ Recuperación Post-Entrenamiento",
        "sense": "min",
        "description": (
            "Ventana anabólica: 0-2 horas tras sesión intensa. "
            "Ratio CHO:Proteína 3:1 para reposición de glucógeno + síntesis proteica. "
            "Baja grasa para acelerar absorción. Proteínas de rápida digestión. "
            "Base: Ivy & Portman 2004, ISSN 2017."
        ),
        "perfil": {
            "objetivo": "Máxima velocidad de recuperación con costo mínimo",
            "contexto": "Comida post-entrenamiento (0-2h) — porción única ~600-800 g",
            "kcal_porcion": "600-800 kcal",
            "prot_porcion": "35-40 g (absorción rápida)",
            "cho_porcion":  "80-100 g (índice glucémico medio-alto)",
            "grasa_max":    "< 15 g (no retardar absorción)",
        },
        "variables": [
            _var("Arroz_Blanco",    0.35, None),
            _var("Platano",         0.30, None),
            _var("Batata",          0.25, None),
            _var("Proteina_Whey",   0.12, None),
            _var("Claras_Huevo",    0.30, None),
            _var("Leche_Descremada",0.40, None),
            _var("Yogur_Griego",    0.30, None),
            _var("Pechuga_Pollo",   0.25, None),
            _var("Manzana",         0.20, None),
            _var("Brocoli",         0.15, None),
        ],
        "constraints": [
            {"name": "Peso_Total",    "sense": "==", "rhs": 1.0,
             "coeffs": {n: 1.0 for n in ["Arroz_Blanco","Platano","Batata","Proteina_Whey",
                        "Claras_Huevo","Leche_Descremada","Yogur_Griego","Pechuga_Pollo",
                        "Manzana","Brocoli"]}},
            # Energía: 700 kcal ÷ 700 g = 1.00 Mcal/kg
            {"name": "Energia_Min",   "sense": ">=", "rhs": 0.80,
             "coeffs": _coeffs("kcal", ["Arroz_Blanco","Platano","Batata","Proteina_Whey",
                        "Claras_Huevo","Leche_Descremada","Yogur_Griego","Pechuga_Pollo",
                        "Manzana","Brocoli"])},
            {"name": "Energia_Max",   "sense": "<=", "rhs": 1.30,
             "coeffs": _coeffs("kcal", ["Arroz_Blanco","Platano","Batata","Proteina_Whey",
                        "Claras_Huevo","Leche_Descremada","Yogur_Griego","Pechuga_Pollo",
                        "Manzana","Brocoli"])},
            # Proteína de absorción rápida: 38 g ÷ 700 g = 0.054
            {"name": "Proteina_Min",  "sense": ">=", "rhs": 0.050,
             "coeffs": _coeffs("prot", ["Arroz_Blanco","Platano","Batata","Proteina_Whey",
                        "Claras_Huevo","Leche_Descremada","Yogur_Griego","Pechuga_Pollo",
                        "Manzana","Brocoli"])},
            # CHO alto para reposición de glucógeno: 90 g ÷ 700 g = 0.129
            {"name": "CHO_Min",       "sense": ">=", "rhs": 0.120,
             "coeffs": _coeffs("cho", ["Arroz_Blanco","Platano","Batata","Proteina_Whey",
                        "Claras_Huevo","Leche_Descremada","Yogur_Griego","Pechuga_Pollo",
                        "Manzana","Brocoli"])},
            # Ratio CHO:Prot ≥ 2.5:1 → CHO - 2.5*Prot ≥ 0
            {"name": "Ratio_CHO_Prot","sense": ">=", "rhs": 0.0,
             "coeffs": {n: (ALIMENTOS_DB[n]["cho"] - 2.5*ALIMENTOS_DB[n]["prot"])/1000
                        for n in ["Arroz_Blanco","Platano","Batata","Proteina_Whey",
                        "Claras_Huevo","Leche_Descremada","Yogur_Griego","Pechuga_Pollo",
                        "Manzana","Brocoli"]}},
            # Grasa baja para NO retardar absorción: máx 15 g ÷ 700 g = 0.021
            {"name": "Grasa_Max",     "sense": "<=", "rhs": 0.025,
             "coeffs": _coeffs("grasa", ["Arroz_Blanco","Platano","Batata","Proteina_Whey",
                        "Claras_Huevo","Leche_Descremada","Yogur_Griego","Pechuga_Pollo",
                        "Manzana","Brocoli"])},
            # Al menos 1 fuente proteica de rápida absorción (whey o claras)
            {"name": "Min_Prot_Rapida","sense": ">=", "rhs": 0.05,
             "coeffs": {"Proteina_Whey": 1.0, "Claras_Huevo": 1.0, "Leche_Descremada": 1.0}},
            # Al menos 1 fuente de CHO de índice alto-medio (arroz, plátano)
            {"name": "Min_CHO_Rapido","sense": ">=", "rhs": 0.15,
             "coeffs": {"Arroz_Blanco": 1.0, "Platano": 1.0}},
            # Max whey (no abusar de suplemento)
            {"name": "Max_Whey",      "sense": "<=", "rhs": 0.12,
             "coeffs": {"Proteina_Whey": 1.0}},
        ],
    },
}

# =============================================================================
# 🔹 ESTADO DE SESIÓN  (key= en widgets → sin asignación directa)
# =============================================================================
def _cons_df(k):
    df = pd.DataFrame(TEMPLATES[k]["constraints"])
    df["coeffs"] = df["coeffs"].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
    return df

_ss_defaults = {
    "vars_df":           pd.DataFrame(TEMPLATES["fuerza_volumen"]["variables"]),
    "cons_df":           _cons_df("fuerza_volumen"),
    "result":            None,
    "base_result":       None,
    "scenario_result":   None,
    "validation":        None,
    "validation_result": None,
    "sb_sense":          "min",
    "sb_time_limit":     60,
    "sb_model_name":     TEMPLATES["fuerza_volumen"]["name"],
    "sb_obj_desc":       "Minimizar costo diario de la dieta",
    "perfil_activo":     "fuerza_volumen",
}
for k, v in _ss_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =============================================================================
# 🔹 FUNCIONES AUXILIARES
# =============================================================================
def load_template(k):
    t = TEMPLATES[k]
    st.session_state.vars_df    = pd.DataFrame(t["variables"])
    st.session_state.cons_df    = _cons_df(k)
    st.session_state.sb_sense   = t["sense"]
    st.session_state.sb_model_name = t["name"]
    st.session_state.sb_obj_desc   = "Minimizar costo diario de la dieta"
    st.session_state.perfil_activo = k
    for key in ["result","base_result","scenario_result","validation","validation_result"]:
        st.session_state[key] = None
    st.success(f"✅ Perfil '{t['name']}' cargado.")


def build_payload():
    variables, objective_coefs = [], {}
    for _, r in st.session_state.vars_df.iterrows():
        vname = str(r["name"])
        variables.append({
            "name":     vname,
            "type":     str(r["type"]),
            "lb":       float(r["lb"]) if pd.notna(r.get("lb")) else 0.0,
            "ub":       float(r["ub"]) if pd.notna(r.get("ub")) else None,
            "obj_coef": float(r.get("obj_coef", 0.0)),
        })
        objective_coefs[vname] = float(r.get("obj_coef", 0.0))

    constraints = []
    for _, r in st.session_state.cons_df.iterrows():
        raw = r.get("coeffs", "{}")
        try:
            coeffs = json.loads(raw) if isinstance(raw, str) else (raw if isinstance(raw, dict) else {})
        except Exception:
            coeffs = {}
        constraints.append({
            "name":   str(r.get("name", "")),
            "sense":  str(r.get("sense", "<=")),
            "rhs":    float(r.get("rhs", 0)),
            "coeffs": {str(k): float(v) for k, v in coeffs.items()},
        })

    return {
        "sense":          st.session_state.sb_sense,
        "objective":      objective_coefs,
        "variables":      variables,
        "constraints":    constraints,
        "time_limit_sec": int(st.session_state.sb_time_limit),
        "metadata": {
            "name":        st.session_state.sb_model_name,
            "description": st.session_state.sb_obj_desc,
            "date":        datetime.now().isoformat(),
        },
    }


def solve_model(is_scenario=False):
    payload = build_payload()
    val = validate_model(payload)
    st.session_state.validation = val
    if val.get("issues"):
        st.error("❌ Modelo inválido. Corrige los errores antes de resolver.")
        for issue in val["issues"]:
            st.warning(f"• {issue}")
        return
    try:
        with st.spinner("⚙️ Calculando dieta óptima..."):
            res = requests.post(API_URL, json=payload,
                                timeout=int(st.session_state.sb_time_limit) + 10)
            res.raise_for_status()
            resultado = res.json()
        if is_scenario:
            st.session_state.scenario_result = resultado
            st.success("✅ Escenario calculado.")
        else:
            st.session_state.result      = resultado
            st.session_state.base_result = resultado.copy()
            obj = resultado.get("objective_value", 0)
            st.success(f"✅ Dieta óptima calculada. Costo: ${obj:.2f} USD/kg de dieta")
    except requests.exceptions.ConnectionError:
        st.error("❌ API no disponible en http://127.0.0.1:8000. ¿Está corriendo INICIAR.bat?")
    except requests.exceptions.HTTPError:
        try:
            st.error(f"❌ Error HTTP {res.status_code}: {res.json()}")
        except Exception:
            st.error(f"❌ Error HTTP {res.status_code}: {res.text}")
    except Exception as e:
        st.error(f"💥 Error inesperado: {e}")

# =============================================================================
# 🔹 SIDEBAR — todos los widgets con key= único y estable
# =============================================================================
with st.sidebar:
    st.header("🏅 Perfiles de Atletas")

    sel = st.selectbox(
        "Seleccionar perfil deportivo",
        list(TEMPLATES.keys()),
        format_func=lambda k: TEMPLATES[k]["name"],
        index=0,
        key="sb_template_sel",
    )

    # Tarjeta de perfil
    t_info = TEMPLATES[sel]
    with st.expander("📋 Ver descripción del perfil", expanded=False):
        st.caption(t_info["description"])
        if "perfil" in t_info:
            for campo, valor in t_info["perfil"].items():
                st.markdown(f"**{campo.replace('_',' ').title()}:** {valor}")

    if st.button("📥 Cargar Perfil", use_container_width=True, key="sb_btn_load"):
        load_template(sel)

    st.markdown("---")
    st.header("⚙️ Configuración")

    st.selectbox(
        "Sentido de optimización",
        ["min", "max"],
        index=0 if st.session_state.sb_sense == "min" else 1,
        key="sb_sense",
    )
    st.number_input(
        "Tiempo límite (segundos)",
        min_value=10, max_value=300,
        key="sb_time_limit",
    )
    st.text_input("Nombre del modelo",   key="sb_model_name")
    st.text_area("Descripción objetivo", key="sb_obj_desc", height=60)

    st.markdown("---")
    if st.button("🔍 Calcular Dieta Óptima", type="primary",
                 use_container_width=True, key="sb_btn_solve"):
        solve_model(is_scenario=False)

    # Referencia científica
    st.markdown("---")
    st.caption(
        "📚 Base científica: ISSN 2017 · ACSM 2016 · Thomas et al. 2016 · "
        "Helms et al. 2014 · Ivy & Portman 2004"
    )

# =============================================================================
# 🔹 TABS PRINCIPALES
# =============================================================================
tabs = st.tabs([
    "🥗 Alimentos y Restricciones",
    "📤 Importar Excel",
    "✅ Validación",
    "📊 Dieta Óptima",
    "📈 Análisis What-If",
    "📖 Exportar Informe",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 0 — Editor de Modelo
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    c1, c2 = st.columns([2, 3])

    with c1:
        st.subheader("🥦 Alimentos Disponibles")
        st.caption("Costo en USD/kg · Límite superior en fracción del kg total diario")
        edited_vars = st.data_editor(
            st.session_state.vars_df,
            use_container_width=True,
            num_rows="dynamic",
            key="de_vars",
            column_config={
                "name":     st.column_config.TextColumn("Alimento", required=True),
                "type":     st.column_config.SelectboxColumn("Tipo", options=["continuous","integer","binary"], required=True),
                "lb":       st.column_config.NumberColumn("Mín (kg)", step=0.01, format="%.3f"),
                "ub":       st.column_config.NumberColumn("Máx (kg)", step=0.01, format="%.3f",
                              help="Fracción máxima del total diario. Ej: 0.40 = máx 40%"),
                "obj_coef": st.column_config.NumberColumn("Costo (USD/kg)", step=0.1, format="%.2f", required=True),
            },
            hide_index=True,
        )
        st.session_state.vars_df = edited_vars

        # Tabla de referencia nutricional
        st.markdown("---")
        st.subheader("📊 Referencia Nutricional")
        alim_sel = st.multiselect(
            "Consultar composición de alimentos",
            list(ALIMENTOS_DB.keys()),
            default=["Pechuga_Pollo", "Avena", "Salmon"],
            key="ms_alim_ref",
        )
        if alim_sel:
            ref_rows = []
            for n in alim_sel:
                a = ALIMENTOS_DB[n]
                ref_rows.append({
                    "Alimento":   f"{a['emoji']} {n}",
                    "Kcal/kg":    a["kcal"],
                    "Prot (g/kg)":a["prot"],
                    "CHO (g/kg)": a["cho"],
                    "Grasa(g/kg)":a["grasa"],
                    "Fibra(g/kg)":a["fibra"],
                    "Ω3 (g/kg)":  a["omega3"],
                    "USD/kg":     a["costo"],
                })
            st.dataframe(pd.DataFrame(ref_rows), use_container_width=True, hide_index=True)

    with c2:
        st.subheader("📐 Restricciones Nutricionales")
        st.caption(
            "Coeficientes = fracción del nutriente por kg de alimento · "
            "RHS = objetivo por kg de dieta total · "
            'Formato `coeffs`: `{"Avena": 0.131, "Pechuga_Pollo": 0.310}` (JSON)'
        )
        edited_cons = st.data_editor(
            st.session_state.cons_df,
            use_container_width=True,
            num_rows="dynamic",
            key="de_cons",
            column_config={
                "name":   st.column_config.TextColumn("Restricción", required=True),
                "sense":  st.column_config.SelectboxColumn("Operador", options=["<=",">=","=="], required=True),
                "rhs":    st.column_config.NumberColumn("Valor RHS", format="%.5f", required=True,
                            help="Por kg de dieta. Ej: proteína 0.064 = 64g/kg de comida"),
                "coeffs": st.column_config.TextColumn("Coeficientes (JSON)", required=True),
            },
            hide_index=True,
        )
        st.session_state.cons_df = edited_cons

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Importar Excel
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("📥 Cargar Modelo desde Excel")
    uploaded = st.file_uploader(
        "Archivo .xlsx con hojas `Variables` y `Restricciones`",
        type=["xlsx"],
        key="fu_excel",
    )
    if uploaded:
        try:
            xls = pd.ExcelFile(uploaded)
            if "Variables" in xls.sheet_names:
                st.session_state.vars_df = pd.read_excel(xls, "Variables")
                st.success("✅ Alimentos cargados.")
            if "Restricciones" in xls.sheet_names:
                c_df = pd.read_excel(xls, "Restricciones")
                if "coeffs" in c_df.columns:
                    c_df["coeffs"] = c_df["coeffs"].apply(
                        lambda x: json.dumps(x) if isinstance(x, dict) else str(x)
                    )
                st.session_state.cons_df = c_df
                st.success("✅ Restricciones cargadas.")
            st.info("Revisa los datos en `🥗 Alimentos` antes de calcular.")
        except Exception as e:
            st.error(f"❌ Error leyendo Excel: {e}")

    if st.button("📥 Descargar Plantilla Excel", key="btn_dl_template"):
        buf = io.BytesIO()
        tv = st.session_state.vars_df.copy()
        tc = st.session_state.cons_df.copy()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            tv.to_excel(w, "Variables", index=False)
            tc.to_excel(w, "Restricciones", index=False)
        st.download_button(
            "💾 Descargar plantilla_atleta.xlsx",
            buf.getvalue(),
            f"plantilla_atleta_{st.session_state.perfil_activo}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_dl_xlsx",
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Validación
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    v = st.session_state.validation
    if not v:
        st.info("👈 Presiona `🔍 Calcular Dieta Óptima` para ejecutar el validador.")
    else:
        color_map = {"✅ VÁLIDO": "green", "⚠️ ADVERTENCIAS": "orange", "❌ INVÁLIDO": "red"}
        status = v.get("status", "Desconocido")
        st.markdown(
            f"### Estado: <span style='color:{color_map.get(status,'black')}'>{status}</span>",
            unsafe_allow_html=True,
        )
        for w in v.get("warnings", []):
            st.warning(f"⚠️ {w}")
        for issue in v.get("issues", []):
            st.error(f"❌ {issue}")
        m = v.get("metrics", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🥦 Alimentos",       m.get("n_variables", 0))
        c2.metric("📐 Restricciones",   m.get("n_constraints", 0))
        c3.metric("🔢 Ratio Coef.",     f"{m.get('coef_ratio', 0):.1e}")
        c4.metric("⚖️ Densidad",        f"{m.get('density', 0):.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Resultados / Dieta Óptima
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    r = st.session_state.result
    if not r:
        st.info("👈 Presiona `🔍 Calcular Dieta Óptima` para ver los resultados.")
    else:
        st.success(f"✅ Estado: `{r.get('status')}` | Solver: `{r.get('solver_used')}`")

        c1, c2, c3 = st.columns(3)
        obj = r.get("objective_value", 0)
        c1.metric("💰 Costo Dieta",    f"${obj:.2f} USD/kg")
        c2.metric("💰 Costo Diario",   f"${obj * 2.5:.2f} USD/día",
                  help="Estimado para 2.5 kg de alimento diario total")
        c3.metric("✅ Factible",        "Sí" if r.get("diagnostics", {}).get("feasible") else "No")

        sol = r.get("solution", {})

        # ── Tabla de receta ──────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("🥗 Receta Óptima del Día")

        rows = []
        for alim, frac in sol.items():
            if frac < 0.001:
                continue
            a = ALIMENTOS_DB.get(alim, {})
            gramos  = frac * 1000
            rows.append({
                "Alimento":    f"{a.get('emoji','🍽️')} {alim.replace('_',' ')}",
                "Grupo":       a.get("grupo", "—"),
                "Cantidad (g)":round(gramos, 1),
                "Kcal":        round(gramos * a.get("kcal", 0) / 1000, 0),
                "Proteína (g)":round(gramos * a.get("prot", 0) / 1000, 1),
                "CHO (g)":     round(gramos * a.get("cho",  0) / 1000, 1),
                "Grasa (g)":   round(gramos * a.get("grasa",0) / 1000, 1),
                "Costo USD":   round(frac   * a.get("costo",0), 3),
            })

        if rows:
            df_sol = pd.DataFrame(rows).sort_values("Cantidad (g)", ascending=False)
            st.dataframe(df_sol, use_container_width=True, hide_index=True)

            # ── Totales nutricionales ────────────────────────────────────────
            st.markdown("---")
            st.subheader("🔢 Totales Nutricionales por kg de Dieta")
            tot_kcal  = sum(r["Kcal"]          for r in rows)
            tot_prot  = sum(r["Proteína (g)"]   for r in rows)
            tot_cho   = sum(r["CHO (g)"]        for r in rows)
            tot_grasa = sum(r["Grasa (g)"]      for r in rows)
            tot_costo = sum(r["Costo USD"]      for r in rows)

            tc1, tc2, tc3, tc4, tc5 = st.columns(5)
            tc1.metric("🔥 Kcal/kg",      f"{tot_kcal:.0f}")
            tc2.metric("💪 Proteína",      f"{tot_prot:.1f} g/kg")
            tc3.metric("⚡ CHO",           f"{tot_cho:.1f} g/kg")
            tc4.metric("🫒 Grasa",         f"{tot_grasa:.1f} g/kg")
            tc5.metric("💰 Costo",         f"${tot_costo:.2f}/kg")

            # Ratio CHO:Proteína
            ratio = tot_cho / (tot_prot + 0.001)
            st.info(f"📊 Ratio CHO:Proteína = **{ratio:.1f}:1**  |  "
                    f"Estimado para 2.5 kg/día → "
                    f"**{tot_kcal*2.5:.0f} kcal · {tot_prot*2.5:.0f}g prot · "
                    f"{tot_cho*2.5:.0f}g CHO · ${tot_costo*2.5:.2f} USD**")

            # ── Gráficos ─────────────────────────────────────────────────────
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(
                    df_sol, values="Cantidad (g)", names="Alimento",
                    title="Composición de la Dieta por Peso",
                    hole=0.35, color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_pie, use_container_width=True, key="chart_pie")

            with c2:
                # Distribución de macros (% kcal)
                kcal_prot  = tot_prot  * 4
                kcal_cho   = tot_cho   * 4
                kcal_grasa = tot_grasa * 9
                fig_macro = go.Figure(go.Pie(
                    labels=["Proteína", "Carbohidratos", "Grasas"],
                    values=[kcal_prot, kcal_cho, kcal_grasa],
                    hole=0.35,
                    marker_colors=["#2196F3", "#FF9800", "#4CAF50"],
                ))
                fig_macro.update_layout(title="Distribución de Macronutrientes (% kcal)")
                st.plotly_chart(fig_macro, use_container_width=True, key="chart_macro")

            # ── Gráfico de barras por grupo de alimento ──────────────────────
            df_sol["Grupo_emoji"] = df_sol["Alimento"].apply(
                lambda x: ALIMENTOS_DB.get(x.split(" ", 1)[-1].replace(" ", "_"), {}).get("grupo", "—")
            )
            fig_bar = px.bar(
                df_sol.sort_values("Cantidad (g)", ascending=True),
                x="Cantidad (g)", y="Alimento", orientation="h",
                color="Grupo", title="Cantidad por Alimento (g/kg de dieta)",
                color_discrete_map={"CHO":"#FF9800","PROT":"#2196F3",
                                    "GRASA":"#4CAF50","LACT":"#9C27B0","VEG":"#8BC34A"},
            )
            fig_bar.update_layout(height=max(300, len(rows) * 35))
            st.plotly_chart(fig_bar, use_container_width=True, key="chart_bar")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Análisis What-If
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    if not st.session_state.base_result:
        st.info("👈 Calcula una dieta base primero.")
    else:
        st.subheader("📈 Análisis de Escenarios — ¿Qué pasa si...?")
        mode = st.radio(
            "Tipo de variación:",
            ["Precio de alimento (obj_coef)", "Requerimiento nutricional (RHS)"],
            horizontal=True, key="wi_mode",
        )
        payload = build_payload()

        if mode == "Precio de alimento (obj_coef)":
            alim_list = st.session_state.vars_df["name"].tolist()
            sel_var   = st.selectbox("Alimento a ajustar", alim_list, key="wi_sel_var")
            curr      = float(st.session_state.vars_df.loc[
                st.session_state.vars_df["name"] == sel_var, "obj_coef"].iloc[0])
            pct = st.slider(f"Variación de precio de {sel_var} (%)",
                            -60.0, 150.0, 0.0, 5.0, key=f"wi_slider_v_{sel_var}")
            new_val = curr * (1 + pct / 100)
            payload["objective"][sel_var] = new_val
            for var in payload["variables"]:
                if var["name"] == sel_var:
                    var["obj_coef"] = new_val
                    break
            st.metric(f"Precio de {sel_var}",
                      f"${curr:.2f}/kg", f"${new_val-curr:+.2f} ({pct:+.1f}%)")
        else:
            cons_list = st.session_state.cons_df["name"].tolist()
            sel_con   = st.selectbox("Restricción nutricional a ajustar",
                                     cons_list, key="wi_sel_con")
            curr      = float(st.session_state.cons_df.loc[
                st.session_state.cons_df["name"] == sel_con, "rhs"].iloc[0])
            pct = st.slider(f"Variación de {sel_con} (%)",
                            -40.0, 80.0, 0.0, 2.0, key=f"wi_slider_c_{sel_con}")
            new_val = curr * (1 + pct / 100)
            for con in payload["constraints"]:
                if con.get("name") == sel_con:
                    con["rhs"] = new_val
                    break
            st.metric(f"RHS de {sel_con}",
                      f"{curr:.5f}", f"{new_val-curr:+.5f} ({pct:+.1f}%)")

        if st.button("🔄 Recalcular Escenario", type="secondary", key="wi_btn_calc"):
            try:
                with st.spinner("Calculando escenario..."):
                    res = requests.post(API_URL, json=payload, timeout=30)
                    res.raise_for_status()
                    st.session_state.scenario_result = res.json()
                st.success("✅ Escenario calculado.")
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.scenario_result = None

        if st.session_state.scenario_result:
            base = st.session_state.base_result
            scen = st.session_state.scenario_result
            delta     = scen["objective_value"] - base["objective_value"]
            pct_delta = (delta / abs(base["objective_value"]) * 100) if base["objective_value"] else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Costo Base",      f"${base['objective_value']:.2f}/kg")
            c2.metric("🔄 Costo Escenario", f"${scen['objective_value']:.2f}/kg")
            c3.metric("📈 Impacto",          f"${delta:+.2f}/kg",
                      f"{pct_delta:+.2f}%",
                      delta_color="normal" if delta >= 0 else "inverse")

            # Tabla comparativa
            comp = []
            for alim in set(base["solution"]) | set(scen["solution"]):
                b_v = base["solution"].get(alim, 0)
                s_v = scen["solution"].get(alim, 0)
                if b_v > 0.001 or s_v > 0.001:
                    comp.append({
                        "Alimento":         alim.replace("_"," "),
                        "Base (g/kg)":      round(b_v * 1000, 1),
                        "Escenario (g/kg)": round(s_v * 1000, 1),
                        "Δ (g/kg)":         round((s_v - b_v) * 1000, 1),
                    })
            if comp:
                st.dataframe(pd.DataFrame(comp).sort_values("Δ (g/kg)", key=abs, ascending=False),
                             use_container_width=True, hide_index=True)

            fig = px.bar(
                x=["Base", "Escenario"],
                y=[base["objective_value"], scen["objective_value"]],
                title="Impacto en Costo por kg de Dieta",
                color=["Base", "Escenario"],
                color_discrete_map={"Base": "#4285F4", "Escenario": "#EA4335"},
            )
            st.plotly_chart(fig, use_container_width=True, key="wi_chart")
        else:
            st.info("Ajusta los parámetros y presiona `🔄 Recalcular Escenario`.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Exportar Informe
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    r = st.session_state.result
    if not r:
        st.warning("⚠️ Calcula una dieta primero para exportar el informe.")
    else:
        st.subheader("📄 Exportar Informe de Dieta")
        if st.button("📥 Generar Excel", key="btn_export"):
            sol   = r.get("solution", {})
            buf   = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                # Hoja Resumen
                pd.DataFrame([
                    {"Parámetro": "Perfil deportivo",   "Valor": st.session_state.sb_model_name},
                    {"Parámetro": "Estado solver",       "Valor": r.get("status")},
                    {"Parámetro": "Costo USD/kg dieta", "Valor": f"${r['objective_value']:.2f}"},
                    {"Parámetro": "Costo USD/día (2.5kg)","Valor": f"${r['objective_value']*2.5:.2f}"},
                    {"Parámetro": "Solver utilizado",   "Valor": r.get("solver_used")},
                    {"Parámetro": "Fecha cálculo",       "Valor": datetime.now().strftime("%Y-%m-%d %H:%M")},
                ]).to_excel(w, "Resumen", index=False)

                # Hoja Receta
                rows_xl = []
                for alim, frac in sol.items():
                    if frac < 0.001: continue
                    a = ALIMENTOS_DB.get(alim, {})
                    g = frac * 1000
                    rows_xl.append({
                        "Alimento":    alim.replace("_"," "),
                        "Grupo":       a.get("grupo","—"),
                        "Gramos/kg_dieta": round(g, 1),
                        "Gramos/dia(2.5kg)": round(g*2.5, 1),
                        "Kcal":        round(g * a.get("kcal",0)/1000, 0),
                        "Proteina_g":  round(g * a.get("prot",0)/1000, 1),
                        "CHO_g":       round(g * a.get("cho",0)/1000,  1),
                        "Grasa_g":     round(g * a.get("grasa",0)/1000, 1),
                        "Costo_USD":   round(frac * a.get("costo",0), 3),
                    })
                pd.DataFrame(rows_xl).to_excel(w, "Receta_Optima", index=False)

                # Hoja Referencia nutricional completa
                ref_rows = []
                for n, a in ALIMENTOS_DB.items():
                    ref_rows.append({
                        "Alimento": n, "Grupo": a["grupo"],
                        "Kcal/kg": a["kcal"], "Prot_g/kg": a["prot"],
                        "CHO_g/kg": a["cho"], "Grasa_g/kg": a["grasa"],
                        "Fibra_g/kg": a["fibra"], "Omega3_g/kg": a["omega3"],
                        "Costo_USD/kg": a["costo"],
                    })
                pd.DataFrame(ref_rows).to_excel(w, "Base_Nutricional", index=False)

            fname = (f"dieta_atleta_{st.session_state.perfil_activo}_"
                     f"{datetime.now().strftime('%Y%m%d')}.xlsx")
            st.download_button(
                "💾 Descargar Informe Excel",
                buf.getvalue(), fname,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_dl_informe",
            )
        st.info("📌 El informe incluye: Resumen ejecutivo · Receta óptima · "
                "Base de datos nutricional completa de los 20 alimentos.")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.caption(
    f"OptiCore Atletas v1.0  ·  {datetime.now().strftime('%Y-%m-%d')}  ·  "
    f"Base científica: ISSN 2017, ACSM 2016, USDA FoodData Central  ·  API: {API_URL}"
)
