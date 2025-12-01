import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import sqlite3
import threading

def cargar_dataset(file_path):
    """Carga un dataset desde un archivo CSV, Excel o SQLite y lo devuelve como un DataFrame de pandas"""
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        elif file_path.endswith((".sqlite", ".db")):
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                raise ValueError("Non se atoparon tablas na base de datos SQLite.")
            table_name = tables[0][0]
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
        else:
            raise ValueError("Formato de arquivo non válido.")
        return df

    except FileNotFoundError:
        messagebox.showerror("Erro", "Arquivo non atopado.")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Erro", "O arquivo está baleiro.")
    except sqlite3.OperationalError:
        messagebox.showerror("Erro", "Non se puido ler a base de datos SQLite.")
    except ValueError as e:
        messagebox.showerror("Erro", str(e))
    except Exception as e:
        messagebox.showerror("Erro inesperado", f"Ocurriu un problema:\n{e}")
    return None


def abrir_archivo(entrada_texto, start_progress, stop_progress, mostrar_tabla, iniciar_flujo_paso_1, ventana, set_dataframes, reset_callback=None):
    """Abre un cuadro de diálogo para seleccionar un archivo de datos, lo carga y actualiza la interfaz"""
    ruta = filedialog.askopenfilename(
        title="Seleccionar arquivo de datos", 
        filetypes=[("Arquivos soportados", "*.csv *.xls *.xlsx *.sqlite *.db"), ("Todos os arquivos", "*.*")]
    )
    if not ruta:
        messagebox.showinfo("Carga cancelada", "A carga do arquivo foi cancelada.")
        return
    
    # Ejecutar reset solo después de confirmar que hay archivo seleccionado
    if reset_callback:
        reset_callback()
    
    entrada_texto.config(state="normal")
    entrada_texto.delete(0, tk.END)
    entrada_texto.insert(0, ruta)
    entrada_texto.config(state="readonly", disabledforeground="black")
    start_progress()
    
    def hilo_carga():
        """Hilo para cargar el dataset y actualizar la interfaz"""
        df = cargar_dataset(ruta)
        def fin():
            """Finaliza la carga del dataset y actualiza la interfaz"""
            stop_progress()
            if df is not None:
                df_original = df.copy()
                df_original_sin_filtrar = df.copy()
                # Actualizar las variables globales en interface.py
                set_dataframes(df_original, df_original_sin_filtrar)
                mostrar_tabla(df_original)
                messagebox.showinfo("Datos cargados", "Arquivo cargado exitosamente. Iniciando fluxo de preprocesamento.")
                iniciar_flujo_paso_1(df_original)
            else:
                messagebox.showerror("Erro na carga", "Non se puido cargar o arquivo.")
        ventana.after(0, fin)
    
    threading.Thread(target=hilo_carga, daemon=True).start()
