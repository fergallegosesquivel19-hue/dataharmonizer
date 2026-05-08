from sqlalchemy import create_engine
import pandas as pd

class ConectorSQL:
    def __init__(self, dsn: str):
        self.engine = create_engine(dsn)

    def leer_datos(self, query: str) -> pd.DataFrame:
        return pd.read_sql(query, self.engine)

    def escribir_datos(self, df: pd.DataFrame, nombre_tabla: str, if_exists: str = "append"):
        df.to_sql(nombre_tabla, self.engine, if_exists=if_exists, index=False)
