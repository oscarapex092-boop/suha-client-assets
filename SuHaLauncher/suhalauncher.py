import customtkinter as ctk
import requests, zipfile, io, os, shutil

# Configuración global de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# URLs directos de Google Drive
URL_USUARIOS = "https://drive.google.com/uc?export=download&id=166fla4gdQbfP52qqTr3A3KP8ltGl1ZWW"
URL_EVENTOS = "https://drive.google.com/uc?export=download&id=1SBMoLiMB9Sy1yfl6CfQFmkpLV6YrgfZG"

usuario_actual = None
evento_seleccionado = None
evento_link = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ------------------ Configuración de RAM ------------------
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
RAM_FILE = os.path.join(CONFIG_DIR, "ram.txt")
os.makedirs(CONFIG_DIR, exist_ok=True)

def guardar_ram(ram):
    try:
        with open(RAM_FILE, "w", encoding="utf-8") as f:
            f.write(str(ram))
    except Exception as e:
        print("Error guardando RAM:", e)

def cargar_ram():
    if os.path.exists(RAM_FILE):
        return open(RAM_FILE, "r", encoding="utf-8").read().strip()
    return "2048"  # valor por defecto

def abrir_configuracion():
    config_win = ctk.CTkToplevel()
    config_win.title("Configuración")
    config_win.geometry("400x200")
    config_win.configure(fg_color="#000000")

    # Mantener ventana al frente (como login)
    config_win.grab_set()
    config_win.focus_force()
    config_win.transient(ventana)

    ram_actual = cargar_ram()

    ctk.CTkLabel(config_win, text="RAM (MB)", font=("Helvetica Neue", 14), text_color="white").pack(pady=10)

    entry_ram = ctk.CTkEntry(config_win, width=200, fg_color="#2e2e2e", text_color="white")
    entry_ram.insert(0, ram_actual)
    entry_ram.pack(pady=10)

    def guardar():
        guardar_ram(entry_ram.get())
        config_win.destroy()

    btn_guardar = ctk.CTkButton(config_win, text="Guardar", command=guardar,
                                corner_radius=30, width=200, height=40,
                                fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white")
    btn_guardar.pack(pady=20)

# ------------------ Cargar usuarios ------------------
def cargar_usuarios():
    usuarios = {}
    try:
        resp = requests.get(URL_USUARIOS)
        if resp.status_code == 200:
            for linea in resp.text.splitlines():
                if ":" in linea:
                    usuario, clave = linea.split(":", 1)
                    usuarios[usuario.strip()] = clave.strip()
    except Exception as e:
        print("Error al descargar archivo de usuarios:", e)
    return usuarios

# ------------------ Cargar eventos ------------------
def cargar_eventos():
    eventos = []
    try:
        resp = requests.get(URL_EVENTOS)
        if resp.status_code == 200:
            for linea in resp.text.splitlines():
                if ":" in linea:
                    _, datos = linea.split(":", 1)
                    partes = datos.split(",")
                    if len(partes) == 3:
                        nombre = partes[0].strip().strip('"')
                        link = partes[1].strip().strip('"')
                        imagen = partes[2].strip().strip('"')
                        eventos.append((nombre, link, imagen))
    except Exception as e:
        print("Error al descargar eventos:", e)

    while len(eventos) < 6:
        eventos.append(("", "", ""))  # espacios vacíos
    return eventos[:6]

# ------------------ Reemplazar carpetas ------------------
def limpiar_carpetas():
    for carpeta in ["mods", "config", "resourcepacks", "saves"]:
        ruta = os.path.join(BASE_DIR, carpeta)
        if os.path.exists(ruta):
            shutil.rmtree(ruta)   # borra todo
        os.makedirs(ruta)         # crea carpeta vacía

def instalar_evento(nombre, link):
    print(f"Instalando evento {nombre}...")
    limpiar_carpetas()
    try:
        resp = requests.get(link)
        if resp.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                z.extractall(BASE_DIR)  # descomprime en raíz
            print(f"Evento {nombre} instalado correctamente.")
        else:
            print("Error al descargar el zip del evento.")
    except Exception as e:
        print("Error instalando evento:", e)

# ------------------ Login ------------------
def abrir_login():
    login = ctk.CTkToplevel()
    login.title("Login")
    login.geometry("450x500")
    login.configure(fg_color="#000000")

    login.grab_set()
    login.focus_force()
    login.transient(ventana)

    ventana.update_idletasks()
    x_principal = ventana.winfo_x()
    y_principal = ventana.winfo_y()
    ancho_principal = ventana.winfo_width()
    alto_principal = ventana.winfo_height()

    ancho_login = 450
    alto_login = 500

    x_centro = x_principal + (ancho_principal // 2) - (ancho_login // 2)
    y_centro = y_principal + (alto_principal // 2) - (alto_login // 2)

    login.geometry(f"{ancho_login}x{alto_login}+{x_centro}+{y_centro}")

    ctk.CTkLabel(
        login,
        text="Inicia sesión con tu usuario y contraseña\nproporcionados por el owner",
        font=("Helvetica Neue", 22, "bold"),
        text_color="white"
    ).pack(pady=20)

    ctk.CTkLabel(login, text="Nombre de usuario", font=("Helvetica Neue", 20), text_color="white").pack(pady=5)
    entry_user = ctk.CTkEntry(login, width=300, height=40, corner_radius=20,
                              font=("Helvetica Neue", 14), fg_color="#2e2e2e", text_color="white")
    entry_user.pack(pady=5)

    ctk.CTkLabel(login, text="Contraseña", font=("Helvetica Neue", 20), text_color="white").pack(pady=5)
    entry_pass = ctk.CTkEntry(login, width=300, height=40, corner_radius=20,
                              font=("Helvetica Neue", 14), fg_color="#2e2e2e", text_color="white", show="*")
    entry_pass.pack(pady=5)

    def toggle_password():
        if entry_pass.cget("show") == "":
            entry_pass.configure(show="*")
            btn_toggle.configure(text="Mostrar contraseña")
        else:
            entry_pass.configure(show="")
            btn_toggle.configure(text="Ocultar contraseña")

    btn_toggle = ctk.CTkButton(login, text="Mostrar contraseña", corner_radius=25,
                               width=220, height=40, font=("Helvetica Neue", 13, "bold"),
                               fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white",
                               command=toggle_password)
    btn_toggle.pack(pady=10)

    mensaje = ctk.CTkLabel(login, text="", font=("Helvetica Neue", 14), text_color="white")
    mensaje.pack(pady=15)

    def validar():
        global usuario_actual
        usuarios = cargar_usuarios()
        usuario = entry_user.get()
        clave = entry_pass.get()
        if usuario in usuarios and usuarios[usuario] == clave:
            usuario_actual = usuario
            mensaje.configure(text=f"Bienvenido a SuHa client {usuario}", text_color="lime")
            login.after(2000, lambda: cerrar_login(login))
        else:
            mensaje.configure(text="Usuario o contraseña incorrectos.\n Recuerda el uso de mayúsculas y/o signos \nen usuario y contraseña.", text_color="red")

    btn_login = ctk.CTkButton(login, text="Entrar", corner_radius=30, width=220, height=50,
                              font=("Helvetica Neue", 15, "bold"),
                              fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white",
                              command=validar)
    btn_login.pack(pady=20)

def cerrar_login(login):
    login.destroy()
    mostrar_menu_principal()

# ------------------ Menú principal ------------------
def mostrar_menu_principal():
    for widget in frame.winfo_children():
        widget.destroy()

    centro = ctk.CTkFrame(frame, fg_color="#000000")
    centro.pack(expand=True)

    titulo = ctk.CTkLabel(centro, text="Su-Ha Client",
                          font=("Helvetica Neue", 56, "bold"),
                          text_color="white")
    titulo.pack(pady=30)

    # Barra de progreso (creada una sola vez, oculta al inicio)
    barra_progreso = ctk.CTkProgressBar(centro, width=300,
                                        fg_color="gray",       # color vacío
                                        progress_color="white" # color lleno
                                        )
    barra_progreso.set(0)
    barra_progreso.pack(pady=10)
    barra_progreso.pack_forget()  # oculta al inicio

    estado_label = ctk.CTkLabel(centro, text="", font=("Helvetica Neue", 14), text_color="white")
    estado_label.pack(pady=5)

    def iniciar_evento():
        if evento_seleccionado and evento_link:
            barra_progreso.set(0)
            barra_progreso.pack(pady=10)
            estado_label.configure(text="Descargando mods...", text_color="yellow")
            ventana.update_idletasks()
            try:
                resp = requests.get(evento_link, stream=True)
                total = int(resp.headers.get('content-length', 0))
                descargado = 0
                contenido = io.BytesIO()
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        contenido.write(chunk)
                        descargado += len(chunk)
                        progreso = descargado / total if total > 0 else 0
                        barra_progreso.set(progreso)
                        ventana.update_idletasks()
                estado_label.configure(text="Instalando evento...", text_color="yellow")
                limpiar_carpetas()
                with zipfile.ZipFile(contenido) as z:
                    z.extractall(BASE_DIR)
                estado_label.configure(text=f"Evento '{evento_seleccionado}' instalado correctamente.", text_color="lime")
                ventana.after(3000, lambda: barra_progreso.pack_forget())
            except Exception as e:
                estado_label.configure(text=f"Error: {e}", text_color="red")
                ventana.after(3000, lambda: barra_progreso.pack_forget())
        else:
            estado_label.configure(text="No hay evento seleccionado.", text_color="red")

    if evento_seleccionado:
        texto_iniciar = f"Iniciar evento: {evento_seleccionado}"
        btn_juego = ctk.CTkButton(centro, text=texto_iniciar,
                                  corner_radius=30, width=300, height=60,
                                  font=("Helvetica Neue", 16, "bold"),
                                  fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white",
                                  command=iniciar_evento)
    else:
        btn_juego = ctk.CTkButton(centro, text="No hay eventos seleccionados",
                                  corner_radius=30, width=300, height=60,
                                  font=("Helvetica Neue", 16, "bold"),
                                  fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white")
    btn_juego.pack(pady=20)

    btn_eventos = ctk.CTkButton(centro, text="Eventos", corner_radius=30, width=220, height=60,
                                font=("Helvetica Neue", 16, "bold"),
                                fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white",
                                command=mostrar_eventos)
    btn_eventos.pack(pady=20)

    # Botón Settings para RAM
    btn_config = ctk.CTkButton(centro, text="Settings", corner_radius=30, width=220, height=60,
                               font=("Helvetica Neue", 16, "bold"),
                               fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white",
                               command=abrir_configuracion)
    btn_config.pack(pady=20)

    usuario_label = ctk.CTkLabel(frame, text=f"Usuario: {usuario_actual if usuario_actual else '(ninguno)'}",
                                 font=("Helvetica Neue", 14), text_color="white")
    usuario_label.place(relx=0.01, rely=0.95, anchor="sw")

    evento_label = ctk.CTkLabel(frame, text=f"Evento seleccionado: {evento_seleccionado if evento_seleccionado else '(ninguno)'}",
                                font=("Helvetica Neue", 14), text_color="white")
    evento_label.place(relx=0.99, rely=0.95, anchor="se")

# ------------------ Mostrar eventos ------------------
def mostrar_eventos():
    for widget in frame.winfo_children():
        widget.destroy()

    eventos = cargar_eventos()

    contenedor = ctk.CTkFrame(frame, fg_color="#000000")
    contenedor.pack(expand=True)

    max_cols = 3
    for i, (nombre, link, imagen) in enumerate(eventos):  # ahora 3 valores
        fila = i // max_cols
        col = i % max_cols
        card = crear_card(contenedor, nombre, link, imagen)  # pasar imagen también
        card.grid(row=fila, column=col, padx=20, pady=20, sticky="n")

    btn_volver = ctk.CTkButton(contenedor, text="Volver", corner_radius=30,
                               width=220, height=50, font=("Helvetica Neue", 15, "bold"),
                               fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white",
                               command=mostrar_menu_principal)
    filas_totales = (len(eventos) + max_cols - 1) // max_cols
    btn_volver.grid(row=filas_totales, column=0, columnspan=max_cols, pady=30)

# ------------------ Crear card de evento ------------------
def crear_card(parent, nombre_evento, link_evento, imagen_evento):
    card = ctk.CTkFrame(parent, corner_radius=20, fg_color="#1a1a1a")

    # Imagen del evento
    if imagen_evento:
        try:
            from PIL import Image
            import requests
            from io import BytesIO

            # Descargar la imagen desde el link
            resp = requests.get(imagen_evento)
            if resp.status_code == 200:
                try:
                    img_data = BytesIO(resp.content)
                    img = ctk.CTkImage(Image.open(img_data), size=(180, 100))
                    espacio_img = ctk.CTkLabel(card, image=img, text="")
                except Exception as e:
                    espacio_img = ctk.CTkLabel(card, text=f"[Error abriendo imagen: {e}]",
                                               width=180, height=100,
                                               font=("Helvetica Neue", 12), text_color="gray")
            else:
                espacio_img = ctk.CTkLabel(card, text=f"[HTTP {resp.status_code}]",
                                           width=180, height=100,
                                           font=("Helvetica Neue", 12), text_color="gray")
        except Exception as e:
            espacio_img = ctk.CTkLabel(card, text=f"[Error: {e}]",
                                       width=180, height=100,
                                       font=("Helvetica Neue", 12), text_color="gray")
    else:
        espacio_img = ctk.CTkLabel(card, text="[Imagen aquí]", width=180, height=100,
                                   font=("Helvetica Neue", 12), text_color="gray")
    espacio_img.pack(pady=10)

    # Título del evento
    titulo_evento = ctk.CTkLabel(card, text=nombre_evento if nombre_evento else "Evento finalizado\n o sin iniciar",
                                 font=("Helvetica Neue", 17, "bold"), text_color="white")
    titulo_evento.pack(pady=10)

    # Botón de selección
    if nombre_evento:
        def seleccionar_evento():
            global evento_seleccionado, evento_link, evento_imagen
            evento_seleccionado = nombre_evento
            evento_link = link_evento
            evento_imagen = imagen_evento
            mostrar_menu_principal()

        btn_select = ctk.CTkButton(card, text="Seleccionar evento", corner_radius=30,
                                   width=180, height=40, font=("Helvetica Neue", 14, "bold"),
                                   fg_color="#0084ff", hover_color="#33e0ff", text_color="white",
                                   command=seleccionar_evento)
        btn_select.pack(pady=10)
    else:
        btn_soon = ctk.CTkButton(card, text="Muy pronto", corner_radius=30,
                                 width=180, height=40, font=("Helvetica Neue", 14, "bold"),
                                 fg_color="#cc0000", hover_color="#ff3333", text_color="white",
                                 state="disabled")
        btn_soon.pack(pady=10)

    return card

# ------------------ Ventana principal ------------------
ventana = ctk.CTk()
ventana.title("Su-Ha Client")
ventana.geometry("1200x800")
ventana.configure(fg_color="#000000")

frame = ctk.CTkFrame(ventana, fg_color="#000000")
frame.pack(expand=True, fill="both")

centro = ctk.CTkFrame(frame, fg_color="#000000")
centro.pack(expand=True)

titulo_bienvenida = ctk.CTkLabel(
    centro,
    text="Bienvenido a Su-Ha Client.\nAquí podrás jugar eventos hechos por Su-Ha Spore Studios",
    font=("Helvetica Neue", 28, "bold"),
    text_color="white",
    justify="center"
)
titulo_bienvenida.pack(pady=40)

btn_iniciar = ctk.CTkButton(
    centro,
    text="Iniciar sesión",
    corner_radius=30,
    width=220,
    height=60,
    font=("Helvetica Neue", 18, "bold"),
    fg_color="#3a3a3a",
    hover_color="#5a5a5a",
    text_color="white",
    command=abrir_login
)
btn_iniciar.pack(pady=20)

ventana.mainloop()

