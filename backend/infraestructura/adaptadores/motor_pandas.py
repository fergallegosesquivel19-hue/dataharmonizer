from backend.dominio.puertos.motor_procesamiento import MotorProcesamiento
from backend.dominio.entidades.flujo_limpieza import ReglaLimpieza
from typing import Any, List
import pandas as pd
import numpy as np
from rapidfuzz import fuzz
import re

class MotorPandas(MotorProcesamiento):
    def cargar_datos(self, conexion_config: dict) -> pd.DataFrame:
        if "ruta_archivo" in conexion_config:
            ruta = conexion_config["ruta_archivo"]
            if ruta.endswith(".csv"):
                return pd.read_csv(ruta)
            elif ruta.endswith((".xls", ".xlsx")):
                return pd.read_excel(ruta)
        raise ValueError("Configuración de conexión no soportada por el motor.")

    def aplicar_reglas(self, datos: pd.DataFrame, reglas: List[ReglaLimpieza]) -> pd.DataFrame:
        df = datos.copy()
        for regla in reglas:
            if regla.tipo == "eliminar_nulos":
                cols = regla.parametros.get("columnas")
                if cols:
                    df = df.dropna(subset=cols)
                else:
                    df = df.dropna()
            
            elif regla.tipo == "reemplazar_nulos":
                cols = regla.parametros.get("columnas")
                valor = regla.parametros.get("valor", "No aplica")
                if cols:
                    for c in cols:
                        df[c] = df[c].fillna(valor)
                else:
                    df = df.fillna(valor)

            elif regla.tipo == "remover_duplicados":
                cols = regla.parametros.get("columnas")
                df = df.drop_duplicates(subset=cols)

            elif regla.tipo == "mayusculas":
                cols = regla.parametros.get("columnas", [])
                for c in cols:
                    df[c] = df[c].astype(str).str.upper()

            elif regla.tipo == "minusculas":
                cols = regla.parametros.get("columnas", [])
                for c in cols:
                    df[c] = df[c].astype(str).str.lower()

            elif regla.tipo == "homologacion_difusa":
                df = self._homologacion_difusa(df, regla.parametros)
                
            elif regla.tipo == "cruce_bases":
                conexion_B_config = regla.parametros.get("conexion_B_config")
                col_A = regla.parametros.get("columna_A")
                col_B = regla.parametros.get("columna_B")
                umbral = regla.parametros.get("umbral", 80)
                
                if conexion_B_config and col_A and col_B:
                    df_B = self.cargar_datos(conexion_B_config)
                    df = self._cruzar_bases_difuso(df, df_B, col_A, col_B, umbral)
                
        return df

    def _numeros_coinciden_exactamente(self, t1: str, t2: str) -> bool:
        nums1 = set(re.findall(r'\d+', str(t1)))
        nums2 = set(re.findall(r'\d+', str(t2)))
        if not nums1 and not nums2:
            return True
        return nums1 == nums2

    def _homologacion_difusa(self, df: pd.DataFrame, params: dict) -> pd.DataFrame:
        columna = params.get("columna")
        lista_maestra = params.get("lista_maestra", [])
        umbral = params.get("umbral", 80)
        
        if not columna or not lista_maestra or columna not in df.columns:
            return df
        
        def buscar_mejor_coincidencia(valor):
            if pd.isna(valor):
                return valor
            
            mejor_match = None
            mejor_score = 0
            valor_str = str(valor)
            
            for master in lista_maestra:
                master_str = str(master)
                # REGLA CRÍTICA: Validar números primero
                if not self._numeros_coinciden_exactamente(valor_str, master_str):
                    continue
                    
                score = fuzz.token_sort_ratio(valor_str, master_str)
                if score > mejor_score:
                    mejor_score = score
                    mejor_match = master
            
            if mejor_score >= umbral:
                return mejor_match
            return valor

        df[columna] = df[columna].apply(buscar_mejor_coincidencia)
        return df

    def _cruzar_bases_difuso(self, df_A: pd.DataFrame, df_B: pd.DataFrame, col_A: str, col_B: str, umbral: int) -> pd.DataFrame:
        if col_A not in df_A.columns or col_B not in df_B.columns:
            return df_A
            
        lista_maestra = df_B[col_B].dropna().unique().tolist()
        
        def buscar_mejor_coincidencia(valor):
            if pd.isna(valor):
                return None
            
            mejor_match = None
            mejor_score = 0
            valor_str = str(valor)
            
            for master in lista_maestra:
                master_str = str(master)
                if not self._numeros_coinciden_exactamente(valor_str, master_str):
                    continue
                    
                score = fuzz.token_sort_ratio(valor_str, master_str)
                if score > mejor_score:
                    mejor_score = score
                    mejor_match = master
            
            if mejor_score >= umbral:
                return mejor_match
            return None

        col_match = f"{col_A}_matched_temp"
        df_A[col_match] = df_A[col_A].apply(buscar_mejor_coincidencia)
        
        df_resultado = pd.merge(df_A, df_B, left_on=col_match, right_on=col_B, how="left", suffixes=('_A', '_B'))
        df_resultado = df_resultado.drop(columns=[col_match])
        
        return df_resultado

    def guardar_resultados(self, datos: pd.DataFrame, destino_config: dict) -> None:
        if "ruta_archivo" in destino_config:
            ruta = destino_config["ruta_archivo"]
            if ruta.endswith(".csv"):
                datos.to_csv(ruta, index=False)
            elif ruta.endswith((".xls", ".xlsx")):
                datos.to_excel(ruta, index=False)
