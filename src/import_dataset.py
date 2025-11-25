import pandas as pd
import sqlite3
import sys

def load_data(file_path):
    try:
        # Detectar el tipo de archivo por extensión
        if file_path.endswith(('.csv')):  # Si el archivo es CSV
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):  # Si el archivo es Excel
            df = pd.read_excel(file_path)
        elif file_path.endswith(('.sqlite', '.db')):  # Si el archivo es SQLite
            conn = sqlite3.connect(file_path)
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            cursor = conn.cursor()
            cursor.execute(query)
            tables = cursor.fetchall()
            
            if len(tables) == 0:
                print("No se encontraron tablas en la base de datos SQLite.")
                return None
            
            table_name = tables[0][0]  # Selecciona la primera tabla
            print(f"Cargando datos de la tabla: {table_name}")
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
        else:
            raise ValueError("Formato de archivo inválido")

        print("Primeras filas de los datos cargados:")
        print(df.head())
        return df

    except FileNotFoundError:
        print("Archivo no encontrado")
        return None
    except pd.errors.EmptyDataError:
        print("Archivo vacío")
        return None
    except sqlite3.OperationalError:
        print("La tabla no existe en la base de datos SQLite")
        return None
    except ValueError as e:
        print(e)
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <ruta_del_archivo>")
    else:
        file_path = sys.argv[1]
        data = load_data(file_path)
        if data is not None:
            print("Datos cargados correctamente")
