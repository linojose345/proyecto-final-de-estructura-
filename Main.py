import heapq
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import calendar
import locale  # Importar el módulo locale

# Configurar el locale a español (específico para Windows)
try:
    locale.setlocale(locale.LC_TIME, "es_ES")  # Configura el locale a español para Windows
except locale.Error:
    print("No se pudo configurar el locale a español. Los meses se mostrarán en inglés.")

# -----------------------
# Cola de Prioridad
# -----------------------
cola_prioridad = []
contador_tareas = 0  # Contador para mantener el orden de creación

# -----------------------
# Árbol de Categorías
# -----------------------
class NodoArbol:
    def __init__(self, categoria):
        self.categoria = categoria
        self.tareas = []  # Lista de tareas para esta categoría
        self.izquierda = None
        self.derecha = None

# Árbol global para almacenar tareas por categoría
arbol_categorias = None

# -----------------------
# Funciones para Tkinter
# -----------------------

def actualizar_lista_tareas():
    """Actualiza la lista de tareas en la interfaz."""
    for row in treeview_tareas.get_children():
        treeview_tareas.delete(row)
    tareas = sorted(cola_prioridad, key=lambda x: (x[0], x[1]))  # Ordenar por prioridad y orden de creación
    for _, _, tarea in tareas:
        treeview_tareas.insert("", tk.END, values=(tarea["prioridad"], tarea["descripcion"], tarea["categoria"], tarea["fecha"]))
    actualizar_estado()

def actualizar_estado():
    """Actualiza el panel de estado con el número de tareas pendientes."""
    estado_label.config(text=f"Tareas pendientes: {len(cola_prioridad)}")

def insertar_en_arbol(nodo, categoria, tarea):
    """
    Inserta una tarea en el árbol según su categoría (usando recursividad).
    """
    if nodo is None:
        nodo = NodoArbol(categoria)
    if categoria == nodo.categoria:
        nodo.tareas.append(tarea)
    elif categoria < nodo.categoria:
        nodo.izquierda = insertar_en_arbol(nodo.izquierda, categoria, tarea)
    else:
        nodo.derecha = insertar_en_arbol(nodo.derecha, categoria, tarea)
    return nodo

def buscar_tareas_por_categoria(nodo, categoria):
    """
    Busca todas las tareas de una categoría específica (usando recursividad).
    """
    if nodo is None:
        return []
    if categoria == nodo.categoria:
        return nodo.tareas
    elif categoria < nodo.categoria:
        return buscar_tareas_por_categoria(nodo.izquierda, categoria)
    else:
        return buscar_tareas_por_categoria(nodo.derecha, categoria)

def agregar_tarea():
    """Agrega una tarea desde la interfaz."""
    global contador_tareas, arbol_categorias

    descripcion = entry_descripcion.get()
    categoria = entry_categoria.get()
    prioridad = entry_prioridad.get()

    if not descripcion or not categoria or not prioridad.isdigit():
        messagebox.showwarning("Entrada inválida", "Por favor, completa todos los campos correctamente.")
        return

    prioridad = int(prioridad)

    if prioridad < 1 or prioridad > 5:
        messagebox.showwarning("Prioridad inválida", "La prioridad debe estar entre 1 (más urgente) y 5 (menos urgente).")
        return

    fecha = entry_fecha.get()
    if not fecha:
        messagebox.showwarning("Fecha inválida", "Debes seleccionar una fecha válida.")
        return

    tarea = {"prioridad": prioridad, "descripcion": descripcion, "categoria": categoria, "fecha": fecha}
    heapq.heappush(cola_prioridad, (prioridad, contador_tareas, tarea))
    contador_tareas += 1

    # Insertar la tarea en el árbol de categorías
    arbol_categorias = insertar_en_arbol(arbol_categorias, categoria, tarea)

    entry_descripcion.delete(0, tk.END)
    entry_categoria.delete(0, tk.END)
    entry_prioridad.delete(0, tk.END)
    entry_fecha.delete(0, tk.END)
    actualizar_lista_tareas()
    mostrar_tareas_en_calendario()

def buscar_por_categoria():
    """Busca tareas por categoría usando el árbol."""
    categoria = entry_categoria.get()
    if not categoria:
        messagebox.showwarning("Categoría vacía", "Por favor, ingresa una categoría.")
        return

    tareas = buscar_tareas_por_categoria(arbol_categorias, categoria)
    if not tareas:
        messagebox.showinfo("Sin resultados", f"No hay tareas para la categoría '{categoria}'.")
    else:
        messagebox.showinfo(f"Tareas de '{categoria}'", "\n".join([t["descripcion"] for t in tareas]))

def mostrar_tareas_recursivo(tareas, indice=0):
    """
    Muestra las tareas en orden usando recursividad.
    """
    if indice >= len(tareas):
        return
    tarea = tareas[indice][2]  # Extraer la tarea de la tupla (prioridad, contador, tarea)
    print(f"Prioridad: {tarea['prioridad']}, Descripción: {tarea['descripcion']}, Fecha: {tarea['fecha']}")
    mostrar_tareas_recursivo(tareas, indice + 1)

def mostrar_tareas_ordenadas():
    """Muestra las tareas en orden de prioridad usando recursividad."""
    tareas_ordenadas = sorted(cola_prioridad, key=lambda x: x[0])  # Ordenar por prioridad
    mostrar_tareas_recursivo(tareas_ordenadas)

def completar_tarea_seleccionada():
    """Completa la tarea seleccionada de la lista."""
    seleccion = treeview_tareas.selection()
    
    if not seleccion:
        messagebox.showwarning("Ninguna tarea seleccionada", "Selecciona una tarea de la lista.")
        return

    item = treeview_tareas.item(seleccion[0])
    prioridad = int(item["values"][0])
    descripcion = item["values"][1]
    categoria = item["values"][2]
    fecha = item["values"][3]

    # Buscar la tarea en la cola y eliminarla
    for i, (_, _, tarea) in enumerate(cola_prioridad):
        if (tarea["prioridad"] == prioridad and
            tarea["descripcion"] == descripcion and
            tarea["categoria"] == categoria and
            tarea["fecha"] == fecha):
            cola_prioridad.pop(i)
            heapq.heapify(cola_prioridad)
            break

    messagebox.showinfo("Tarea Completada", f"✅ Completaste: {descripcion} - {categoria} (Prioridad {prioridad})")
    actualizar_lista_tareas()
    mostrar_tareas_en_calendario()

def completar_tarea_mas_urgente():
    """Completa automáticamente la tarea con mayor prioridad (menor número)."""
    if not cola_prioridad:
        messagebox.showwarning("Sin tareas", "No hay tareas para completar.")
        return

    # Obtener la tarea más urgente (prioridad más baja)
    prioridad, _, tarea = heapq.heappop(cola_prioridad)
    messagebox.showinfo("Tarea Completada", f"✅ Completaste: {tarea['descripcion']} - {tarea['categoria']} (Prioridad {tarea['prioridad']})")
    actualizar_lista_tareas()
    mostrar_tareas_en_calendario()

def completar_tarea_menos_urgente():
    """Completa automáticamente la tarea con menor prioridad (mayor número)."""
    if not cola_prioridad:
        messagebox.showwarning("Sin tareas", "No hay tareas para completar.")
        return

    # Buscar la tarea con la prioridad más alta (menos urgente)
    tarea_menos_urgente = max(cola_prioridad, key=lambda x: x[0])
    cola_prioridad.remove(tarea_menos_urgente)
    heapq.heapify(cola_prioridad)

    messagebox.showinfo("Tarea Completada", f"✅ Completaste: {tarea_menos_urgente[2]['descripcion']} - {tarea_menos_urgente[2]['categoria']} (Prioridad {tarea_menos_urgente[2]['prioridad']})")
    actualizar_lista_tareas()
    mostrar_tareas_en_calendario()

def limpiar_campos():
    """Limpia los campos de entrada."""
    entry_descripcion.delete(0, tk.END)
    entry_categoria.delete(0, tk.END)
    entry_prioridad.delete(0, tk.END)
    entry_fecha.delete(0, tk.END)

def mostrar_calendario():
    """Muestra un calendario para seleccionar fechas."""
    def seleccionar_fecha():
        fecha_seleccionada = f"{anio.get()}-{mes.get():02d}-{dia.get():02d}"
        entry_fecha.delete(0, tk.END)
        entry_fecha.insert(0, fecha_seleccionada)
        ventana_calendario.destroy()

    ventana_calendario = tk.Toplevel(root)
    ventana_calendario.title("Seleccionar Fecha")
    ventana_calendario.configure(bg="#f0f0f0")  # Fondo neutro para la ventana del calendario

    hoy = datetime.now()
    anio = tk.IntVar(value=hoy.year)
    mes = tk.IntVar(value=hoy.month)
    dia = tk.IntVar(value=hoy.day)

    ttk.Label(ventana_calendario, text="Año:").grid(row=0, column=0, padx=5, pady=5)
    ttk.Entry(ventana_calendario, textvariable=anio, width=10).grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(ventana_calendario, text="Mes:").grid(row=1, column=0, padx=5, pady=5)
    ttk.Entry(ventana_calendario, textvariable=mes, width=10).grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(ventana_calendario, text="Día:").grid(row=2, column=0, padx=5, pady=5)
    ttk.Entry(ventana_calendario, textvariable=dia, width=10).grid(row=2, column=1, padx=5, pady=5)

    ttk.Button(ventana_calendario, text="Seleccionar", command=seleccionar_fecha).grid(row=3, column=0, columnspan=2, pady=10)

def mostrar_tareas_en_calendario():
    """Muestra las tareas en el calendario."""
    # Limpiar el calendario anterior
    for widget in frame_calendario.winfo_children():
        widget.destroy()

    # Crear botones de navegación del calendario en la parte superior
    frame_navegacion = tk.Frame(frame_calendario, bg="#f0f0f0")
    frame_navegacion.grid(row=0, column=0, columnspan=7, pady=5)

    ttk.Button(frame_navegacion, text="<", command=lambda: cambiar_mes(-1)).grid(row=0, column=0, padx=5, pady=5)
    
    # Mostrar el nombre del mes y el año en español
    nombre_mes = calendar.month_name[mes_actual].capitalize()  # Obtener el nombre del mes en español
    label_mes_anio = ttk.Label(frame_navegacion, text=f"{nombre_mes} {año_actual}", font=("Arial", 12, "bold"), background="#f0f0f0")
    label_mes_anio.grid(row=0, column=1, columnspan=5, padx=10, pady=5)

    ttk.Button(frame_navegacion, text=">", command=lambda: cambiar_mes(1)).grid(row=0, column=6, padx=5, pady=5)

    # Crear etiquetas para los días de la semana
    dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    for i, dia in enumerate(dias_semana):
        tk.Label(frame_calendario, text=dia, font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=1, column=i, padx=5, pady=5)

    # Obtener el número de días en el mes
    num_dias = calendar.monthrange(año_actual, mes_actual)[1]

    # Obtener el primer día del mes (para alinear correctamente en la cuadrícula)
    primer_dia_semana = calendar.monthrange(año_actual, mes_actual)[0]  # 0 = Lunes, 6 = Domingo

    # Mostrar los días del mes con tareas resaltadas
    fila = 2  # Fila donde comienzan los días
    columna = primer_dia_semana  # Empezar en el día correcto de la semana

    for dia in range(1, num_dias + 1):
        fecha = f"{año_actual}-{mes_actual:02d}-{dia:02d}"
        tareas_dia = [tarea["descripcion"] for _, _, tarea in cola_prioridad if tarea["fecha"] == fecha]

        # Cambiar el color de fondo si hay tareas
        bg_color = "#c7d9e5" if tareas_dia else "#f0f0f0"
        tk.Label(frame_calendario, text=str(dia), font=("Arial", 10), bg=bg_color, width=5, height=2).grid(row=fila, column=columna, padx=5, pady=5)

        # Mostrar las tareas para este día
        if tareas_dia:
            tareas_texto = "\n".join(tareas_dia)
            tk.Label(frame_calendario, text=tareas_texto, font=("Arial", 8), fg="blue", bg=bg_color, justify="center", wraplength=80).grid(row=fila + 1, column=columna, sticky="n")

        columna += 1
        if columna > 6:  # Si llega al domingo, pasa a la siguiente fila
            columna = 0
            fila += 2  # Se mueve dos filas para dar espacio a las tareas

def cambiar_mes(delta):
    """Cambia el mes mostrado en el calendario."""
    global mes_actual, año_actual

    mes_actual += delta
    if mes_actual < 1:
        mes_actual = 12
        año_actual -= 1
    elif mes_actual > 12:
        mes_actual = 1
        año_actual += 1

    mostrar_tareas_en_calendario()

# -----------------------
# Interfaz Gráfica con Tkinter y Estilos
# -----------------------

root = tk.Tk()
root.title("Gestor de Tareas con Prioridad")
root.geometry("1000x700")  # Aumentamos el tamaño de la ventana
root.configure(bg="#f0f0f0")  # Fondo neutro para la ventana principal

# Variables globales para el calendario
mes_actual = datetime.now().month
año_actual = datetime.now().year

# Estilos
style = ttk.Style()
style.configure("TButton", font=("Arial", 10), padding=5, background="#c7d9e5", foreground="black")  # Color de fondo de los botones
style.map("TButton", background=[("active", "#a8c4d9")])  # Cambiar color al hacer clic

style.configure("TLabel", font=("Arial", 11))
style.configure("Treeview", font=("Arial", 10), rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

# Título
titulo = ttk.Label(root, text="Gestor de Tareas Académicas", font=("Arial", 16, "bold"), background="#f0f0f0")
titulo.grid(row=0, column=0, columnspan=3, pady=10)

# Calendario (esquina superior izquierda)
frame_calendario = tk.Frame(root, bg="#f0f0f0")  # Fondo neutro para el calendario
frame_calendario.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

# Sección de ingreso de datos
frame_ingreso = tk.Frame(root, bg="#f0f0f0")  # Fondo neutro para el frame de ingreso
frame_ingreso.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

ttk.Label(frame_ingreso, text="Descripción:").grid(row=0, column=0, padx=5, pady=5)
entry_descripcion = ttk.Entry(frame_ingreso, width=40)
entry_descripcion.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_ingreso, text="Categoría:").grid(row=1, column=0, padx=5, pady=5)
entry_categoria = ttk.Entry(frame_ingreso, width=40)
entry_categoria.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_ingreso, text="Prioridad (1 = Más urgente, 5 = Menos urgente):").grid(row=2, column=0, padx=5, pady=5)
entry_prioridad = ttk.Entry(frame_ingreso, width=5)
entry_prioridad.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_ingreso, text="Fecha (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
entry_fecha = ttk.Entry(frame_ingreso, width=15)
entry_fecha.grid(row=3, column=1, padx=5, pady=5)
ttk.Button(frame_ingreso, text="📅 Seleccionar Fecha", command=mostrar_calendario, compound="left").grid(row=3, column=2, padx=5, pady=5)

btn_agregar = ttk.Button(frame_ingreso, text="➕ Agregar Tarea", command=agregar_tarea, compound="left")
btn_agregar.grid(row=4, column=0, pady=10)

btn_limpiar = ttk.Button(frame_ingreso, text="🗑️ Limpiar Campos", command=limpiar_campos, compound="left")
btn_limpiar.grid(row=4, column=1, pady=10)

# Botón para buscar por categoría
ttk.Button(frame_ingreso, text="🔍 Buscar por Categoría", command=buscar_por_categoria, compound="left").grid(row=5, column=0, pady=10)

# Lista de tareas
frame_lista = tk.Frame(root, bg="#f0f0f0")  # Fondo neutro para el frame de lista
frame_lista.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

columnas = ("prioridad", "descripcion", "categoria", "fecha")
treeview_tareas = ttk.Treeview(frame_lista, columns=columnas, show="headings", selectmode="browse")
treeview_tareas.heading("prioridad", text="Prioridad", anchor="center")
treeview_tareas.heading("descripcion", text="Descripción", anchor="center")
treeview_tareas.heading("categoria", text="Categoría", anchor="center")
treeview_tareas.heading("fecha", text="Fecha", anchor="center")
treeview_tareas.column("prioridad", width=80, anchor="center")
treeview_tareas.column("descripcion", width=300, anchor="center")
treeview_tareas.column("categoria", width=150, anchor="center")
treeview_tareas.column("fecha", width=100, anchor="center")
treeview_tareas.pack(fill=tk.BOTH, expand=True)

# Botones de acción
frame_botones = tk.Frame(root, bg="#f0f0f0")  # Fondo neutro para el frame de botones
frame_botones.grid(row=3, column=0, columnspan=3, pady=10)

ttk.Button(frame_botones, text="✅ Completar Tarea Seleccionada", command=completar_tarea_seleccionada, compound="left").grid(row=0, column=0, padx=5, pady=5)
ttk.Button(frame_botones, text="🔥 Completar Tarea Más Urgente", command=completar_tarea_mas_urgente, compound="left").grid(row=0, column=1, padx=5, pady=5)
ttk.Button(frame_botones, text="🐢 Completar Tarea Menos Urgente", command=completar_tarea_menos_urgente, compound="left").grid(row=0, column=2, padx=5, pady=5)
ttk.Button(frame_botones, text="📄 Mostrar Tareas Ordenadas", command=mostrar_tareas_ordenadas, compound="left").grid(row=1, column=0, padx=5, pady=5)
ttk.Button(frame_botones, text="🚪 Salir", command=root.quit, compound="left").grid(row=1, column=3, padx=5, pady=5)

# Panel de estado
frame_estado = tk.Frame(root, bg="#f0f0f0")  # Fondo neutro para el frame de estado
frame_estado.grid(row=4, column=0, columnspan=3, pady=10)

estado_label = ttk.Label(frame_estado, text="Tareas pendientes: 0", font=("Arial", 11), background="#f0f0f0")
estado_label.pack()

# Mostrar el calendario al iniciar
mostrar_tareas_en_calendario()

# Configurar el peso de las filas y columnas para que se expandan correctamente
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

root.mainloop()
