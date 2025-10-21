# GUÍA DE CONTRIBUCIÓN
## Normas básicas de uso del repositorio

Para mantener un flujo de trabajo limpio y facilitar la colaboración, se deben seguir las siguientes normas básicas:

- Cada cambio debe ir en una rama con nombre descriptivo.
- Los commits deben ser pequeños y atómicos.
- Antes de hacer un Push Request, asegúrate de que el código pasa las pruebas y sigue el estilo del proyecto.
- No realizar commits ni push directamente en la rama `main`. Todo cambio debe hacerse desde una rama independiente.
- Utilizar nombres de rama descriptivos, por ejemplo: `feature/nueva-funcionalidad` o `fix/error-login`.
- Antes de hacer un commit, asegurarse de que el código compila y pasa todas las pruebas existentes.
- No subir archivos generados automáticamente (como binarios, `node_modules`, `__pycache__`, etc.).
- Mantener el estilo y la estructura del proyecto. No reorganizar carpetas ni modificar nombres de archivos sin motivo justificado.
- Añadir comentarios claros y concisos cuando sea necesario, pero evitar la redundancia.
- Si se abre un *issue*, describir con detalle el problema, los pasos para reproducirlo y, si es posible, una propuesta de solución.
- Revisa siempre los *Pull Requests* antes de aprobarlos y comenta cualquier aspecto que pueda mejorarse.

## Estilo de los mensajes de commit
Los mensajes de commit deben seguir un formato coherente y descriptivo. De este modo, se facilita la comprensión del historial del proyecto y la revisión los cambios realizados.

### Formato estándar
Usamos el formato **Conventional Commits**, que sigue esta estructura:

- **tipo** indica la naturaleza del cambio.
- **scope** (opcional) indica el área o módulo afectado.
- **descripción** resume brevemente la modificación, escrita en **imperativo** (por ejemplo, “añadir validación”, no “añadido” ni “añadiendo”).
 **ej** `docs(readme): actualizar instrucciones de instalación`

### Tipos permitidos
- `feat`: nueva funcionalidad
- `fix`: corrección de errores
- `docs`: cambios en la documentación
- `style`: cambios de formato (espacios, comas, indentación, etc.) sin alterar la lógica
- `refactor`: reestructuración del código sin cambiar su comportamiento
- `test`: adición o modificación de pruebas
- `chore`: tareas de mantenimiento (dependencias, configuración, scripts…)


### Reglas básicas
- Usar frases breves (máximo 100 caracteres en la descripción).
- No combinar cambios de distintos tipos en un mismo commit.
- Evitar mensajes vagos o sin contexto.

## Procedimiento para modificar el README o la documentación

Cualquier cambio en el README o en la documentación debe realizarse con cuidado, ya que afecta la comprensión general del proyecto.  
Se debe seguir los pasos indicados a continuación para mantener la coherencia y evitar conflictos entre versiones.

### Pasos a seguir
1. **Crear una nueva rama** específica para el cambio.  
   Usa un nombre descriptivo, por ejemplo:  
   `docs/update-readme` o `docs/fix-typos`.
2. **Realiza los cambios necesarios** en el archivo correspondiente (`README.md`, `CONTRIBUTING.md`, u otros documentos).  
   Mantén el mismo estilo, formato y tono que el resto del texto.
3. **Verifica la validez de los enlaces, ejemplos y comandos** antes de hacer commit.
4. **Haz un commit** siguiendo el formato establecido, por ejemplo:  
   `docs(readme): actualizar instrucciones de instalación`.
5. **Abre un Pull Request (PR)** describiendo brevemente qué se modificó y por qué.  
   Si el cambio es menor (una corrección ortográfica o de formato), indícalo en el título.
6. **Solicita una revisión** antes de fusionar los cambios a `main`.  
   Al menos un colaborador debe aprobar el PR.

## Flujo de trabajo colaborativo con ramas y revisiones

Para garantizar un desarrollo ordenado y evitar conflictos, todo el trabajo colaborativo debe seguir el siguiente flujo:

### 1. Rama principal
La rama `main` (o `master`) siempre debe contener el código estable y funcional.  
No se realizan commits directos en ella.

### 2. Creación de ramas de trabajo
Cada nueva funcionalidad, corrección o cambio de documentación debe desarrollarse en una rama independiente creada desde `main`.  
Usa nombres descriptivos:
- `feature/nueva-funcionalidad`
- `fix/error-en-login`
- `docs/actualizar-readme`

### Commits y pushes
Realizar commits pequeños y claros, siguiendo el formato establecido.
Antes de subir una rama, asegurarse de que el código pasa las pruebas y no rompe nada.

### Pull Requests
Al terminar la tarea, abrir un Pull Request hacia main.
En la descripción del PR se debe:
    -explicar brevemente qué se ha hecho y por qué
    -incluir capturas o ejemplos si el cambio afecta la interfaz o el comportamiento
    -mencionar el issue relacionado (si lo hay)

### Revisión de código
Al menos un colaborador debe revisar el PR antes de aprobarlo.
Durante la revisión:
    -comenta posibles mejoras o errores detectados
    -evita mezclar cambios no relacionados
    -sé respetuoso y constructivo en las observaciones

### Fusión (merge)
Solo se realiza el merge cuando:
    -el PR ha sido aprobado
    -los conflictos se han resuelto
    -el código pasa las pruebas y mantiene la estabilidad
Tras la fusión, elimina la rama en remoto y local para mantener el repositorio limpio.