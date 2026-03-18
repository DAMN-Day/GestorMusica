import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os

def actualizar_gui_progreso(porcentaje, texto):
    barra_progreso['value'] = porcentaje
    etiqueta_estado.config(text=texto)

def progreso_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        if total_bytes:
            descargado = d.get('downloaded_bytes', 0)
            porcentaje = (descargado / total_bytes) * 100
            ventana.after(0, actualizar_gui_progreso, porcentaje, f"Descargando... {porcentaje:.1f}%")
    elif d['status'] == 'finished':
        ventana.after(0, actualizar_gui_progreso, 100, "Finalizando archivo...")

def manejar_cambio_formato():
    if variable_formato.get() == "flac":
        selector_calidad.config(state="disabled")
    else:
        selector_calidad.config(state="readonly")

def seleccionar_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        variable_ruta.set(carpeta)

def descargar_musica():
    url = entrada_url.get()
    formato = variable_formato.get()
    calidad = combo_calidad.get().replace("kbps", "")
    ruta_base = variable_ruta.get()
    
    user_artist = entrada_artista.get().strip()
    user_album = entrada_album.get().strip()
    
    if not url or not ruta_base:
        messagebox.showwarning("Atención", "Falta el enlace o la carpeta de destino.")
        return

    boton_descargar.config(state="disabled", text="Trabajando...")
    barra_progreso['value'] = 0

    # Lógica de carpetas mejorada
    folder_art = user_artist if user_artist else "%(artist,uploader,Unknown Artist)s"
    folder_alb = user_album if user_album else "%(album,Unknown Album)s"
    plantilla_ruta = os.path.join(ruta_base, folder_art, folder_alb, "%(title)s.%(ext)s")

    opciones_ydl = {
        'format': 'bestaudio/best',
        'outtmpl': plantilla_ruta,
        'writethumbnail': True,
        'progress_hooks': [progreso_hook],
        '#js-runtimes': 'node', # Intentar forzar node si está instalado
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': formato,
                'preferredquality': calidad if formato == 'mp3' else '0', 
            },
            { 'key': 'FFmpegMetadata', 'add_metadata': True },
            { 'key': 'EmbedThumbnail' }
        ],
        # Esta opción ayuda a que no ignore videos que ya cree que bajó
        'ignoreerrors': True, 
    }

    def hilo_descarga():
        try:
            with yt_dlp.YoutubeDL(opciones_ydl) as ydl:
                # 1. Extraer información (sin descargar aún)
                info_dict = ydl.extract_info(url, download=False)
                
                # 2. Verificar si es una playlist (álbum) o un solo video
                if 'entries' in info_dict:
                    # Es una playlist/álbum
                    total_videos = len(info_dict['entries'])
                    ventana.after(0, lambda: etiqueta_estado.config(text=f"Detectado álbum con {total_videos} canciones..."))
                    
                    for i, entry in enumerate(info_dict['entries']):
                        if entry is None: continue # Saltar si hay videos privados/borrados
                        
                        # Inyectar metadatos manuales en cada canción del álbum
                        if user_artist: entry['artist'] = user_artist
                        if user_album: entry['album'] = user_album
                        
                        ventana.after(0, lambda n=i+1: etiqueta_estado.config(text=f"Procesando canción {n} de {total_videos}..."))
                        ydl.process_info(entry)
                else:
                    # Es un solo video
                    if user_artist: info_dict['artist'] = user_artist
                    if user_album: info_dict['album'] = user_album
                    ydl.process_info(info_dict)
                
            ventana.after(0, lambda: messagebox.showinfo("Éxito", "¡Álbum completo descargado y organizado!"))
        except Exception as err:
            error_msg = str(err)
            ventana.after(0, lambda: messagebox.showerror("Error", f"Error en el álbum: {error_msg}"))
        finally:
            ventana.after(0, lambda: boton_descargar.config(state="normal", text="INICIAR DESCARGA"))

    threading.Thread(target=hilo_descarga, daemon=True).start()

# --- Interfaz Gráfica ---
ventana = tk.Tk()
ventana.title("Gestor de Música Retro")
ventana.geometry("520x560")
ventana.config(padx=20, pady=20)

tk.Label(ventana, text="Enlace de YouTube:", font=('Arial', 10, 'bold')).pack(anchor="w")
entrada_url = tk.Entry(ventana, width=65)
entrada_url.pack(pady=5)

marco_meta = tk.LabelFrame(ventana, text=" Metadatos del Álbum (Opcional) ", padx=10, pady=10)
marco_meta.pack(fill="x", pady=10)

tk.Label(marco_meta, text="Artista:").grid(row=0, column=0, sticky="w")
entrada_artista = tk.Entry(marco_meta, width=45)
entrada_artista.grid(row=0, column=1, pady=5)

tk.Label(marco_meta, text="Álbum:").grid(row=1, column=0, sticky="w")
entrada_album = tk.Entry(marco_meta, width=45)
entrada_album.grid(row=1, column=1, pady=5)

tk.Label(ventana, text="Guardar en:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(10,0))
marco_ruta = tk.Frame(ventana)
marco_ruta.pack(fill="x", pady=5)
variable_ruta = tk.StringVar(value=os.getcwd())
tk.Entry(marco_ruta, textvariable=variable_ruta, width=50).pack(side="left", padx=(0,5))
tk.Button(marco_ruta, text="Carpeta", command=seleccionar_carpeta).pack(side="left")

marco_opciones = tk.LabelFrame(ventana, text=" Calidad y Formato ", padx=10, pady=10)
marco_opciones.pack(fill="x", pady=10)

variable_formato = tk.StringVar(value="mp3")
tk.Radiobutton(marco_opciones, text="MP3", variable=variable_formato, value="mp3", command=manejar_cambio_formato).grid(row=0, column=0)
tk.Radiobutton(marco_opciones, text="FLAC", variable=variable_formato, value="flac", command=manejar_cambio_formato).grid(row=0, column=1, padx=20)

combo_calidad = tk.StringVar(value="320kbps")
selector_calidad = ttk.Combobox(marco_opciones, textvariable=combo_calidad, width=10, state="readonly")
selector_calidad['values'] = ("128kbps", "192kbps", "256kbps", "320kbps")
selector_calidad.grid(row=0, column=2)

etiqueta_estado = tk.Label(ventana, text="Listo para iniciar", fg="#555")
etiqueta_estado.pack(pady=(10,0))
barra_progreso = ttk.Progressbar(ventana, orient="horizontal", length=450, mode="determinate")
barra_progreso.pack(pady=5)

boton_descargar = tk.Button(ventana, text="INICIAR DESCARGA", command=descargar_musica, bg="#2196F3", fg="white", font=('Arial', 11, 'bold'), height=2)
boton_descargar.pack(pady=20, fill="x")

ventana.mainloop()