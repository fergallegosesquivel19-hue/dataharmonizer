import pandas as pd

class ConectorArchivos:
    @staticmethod
    def leer_excel(ruta: str) -> pd.DataFrame:
        return pd.read_excel(ruta)

    @staticmethod
    def leer_csv(ruta: str) -> pd.DataFrame:
        return pd.read_csv(ruta)
