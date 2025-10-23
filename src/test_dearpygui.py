import dearpygui.dearpygui as dpg


# Callback del botón
def mostrar_mensaje(sender, app_data, user_data):
    texto = dpg.get_value(user_data)
    dpg.configure_item("texto_salida", default_value=f"Has escrito: {texto}")


# Crear ventana principal
dpg.create_context()

with dpg.window(label="Interfaz Mínima", width=300, height=200):
    # Cuadro de texto
    input_id = dpg.add_input_text(label="Escribe algo")

    # Botón
    dpg.add_button(label="Mostrar mensaje", callback=mostrar_mensaje, user_data=input_id)

    # Texto de salida
    dpg.add_text("", tag="texto_salida")

dpg.create_viewport(title='Prueba Dear PyGui', width=300, height=200)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
