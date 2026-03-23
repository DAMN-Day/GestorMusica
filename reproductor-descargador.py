import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os
import requests
from PIL import Image, ImageTk
from io import BytesIO

class GestorMusicaRetro:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Música Retro V2.6")
        self.root.geometry("850x650")
        self.root.config(padx=20, pady=20)
        
        self.info_actual = None
        self.portada_tk = None

        self.setup_ui()

    def setup_ui(self):
        self.paneles = tk.Frame(self.root)
        self.paneles.pack(fill="both", expand=True)

        # PANEL IZQUIERDO
        self.p_izq = tk.Frame(self.paneles, width=450)
        self.p_izq.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(self.p_izq, text="Enlace de YouTube:", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.entrada_url = tk.Entry(self.p_izq, width=50)
        self.entrada_url.pack(pady=5, fill="x")

        self.btn_info = tk.Button(self.p_izq, text="🔍 Obtener Información", command=self.obtener_info_thread, bg="#3498db", fg="white")
        self.btn_info.pack(pady=5, fill="x")

        self.var_modo_playlist = tk.BooleanVar(value=False)
        tk.Checkbutton(self.p_izq, text="Descargar como Playlist (Carpeta única + M3U)", 
                       variable=self.var_modo_playlist, font=('Arial', 9, 'bold'), fg="#e67e22").pack(anchor="w", pady=5)

        self.marco_meta = tk.LabelFrame(self.p_izq, text=" Metadatos Manuales ", padx=10, pady=10)
        self.marco_meta.pack(fill="x", pady=10)
        
        tk.Label(self.marco_meta, text="Artista:").grid(row=0, column=0, sticky="w")
        self.ent_artista = tk.Entry(self.marco_meta, width=35); self.ent_artista.grid(row=0, column=1, pady=2)
        
        tk.Label(self.marco_meta, text="Álbum:").grid(row=1, column=0, sticky="w")
        self.ent_album = tk.Entry(self.marco_meta, width=35); self.ent_album.grid(row=1, column=1, pady=2)

        tk.Label(self.p_izq, text="Guardar en:", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.f_ruta = tk.Frame(self.p_izq)
        self.f_ruta.pack(fill="x", pady=5)
        self.var_ruta = tk.StringVar(value=os.getcwd())
        tk.Entry(self.f_ruta, textvariable=self.var_ruta, width=35).pack(side="left", fill="x", expand=True)
        tk.Button(self.f_ruta, text="...", command=self.seleccionar_carpeta).pack(side="left", padx=2)

        self.marco_fmt = tk.LabelFrame(self.p_izq, text=" Formato y Calidad ", padx=10, pady=10)
        self.marco_fmt.pack(fill="x", pady=10)
        self.var_fmt = tk.StringVar(value="mp3")
        tk.Radiobutton(self.marco_fmt, text="MP3", variable=self.var_fmt, value="mp3").pack(side="left")
        tk.Radiobutton(self.marco_fmt, text="FLAC", variable=self.var_fmt, value="flac").pack(side="left", padx=20)
        self.cb_calidad = ttk.Combobox(self.marco_fmt, values=["128kbps", "192kbps", "256kbps", "320kbps"], width=10, state="readonly")
        self.cb_calidad.set("320kbps")
        self.cb_calidad.pack(side="left")

        # PANEL DERECHO (PREVIEW)
        self.p_der = tk.LabelFrame(self.paneles, text=" Vista Previa ", padx=10, pady=10, width=320)
        self.p_der.pack(side="right", fill="both")
        self.p_der.pack_propagate(False)

        self.lbl_img = tk.Label(self.p_der, text="Sin miniatura", bg="gray90", width=30, height=10)
        self.lbl_img.pack(pady=10)

        self.lbl_preview_info = tk.Label(self.p_der, text="Esperando enlace...", wraplength=280, justify="left", font=('Arial', 9))
        self.lbl_preview_info.pack(fill="x")

        # SECCIÓN INFERIOR
        self.lbl_estado = tk.Label(self.root, text="Listo", fg="#7f8c8d")
        self.lbl_estado.pack(pady=(10,0))
        self.progreso = ttk.Progressbar(self.root, orient="horizontal", length=800, mode="determinate")
        self.progreso.pack(pady=5)

        self.btn_descargar = tk.Button(self.root, text="INICIAR DESCARGA", command=self.descargar_thread, 
                                       bg="#27ae60", fg="white", font=('Arial', 12, 'bold'), height=2)
        self.btn_descargar.pack(fill="x", pady=10)

    # --- FUNCIONES ---
    def seleccionar_carpeta(self):
        c = filedialog.askdirectory()
        if c: self.var_ruta.set(c)

    def obtener_info_thread(self):
        url = self.entrada_url.get().strip()
        if not url: return
        self.lbl_estado.config(text="Buscando información rápidamente...")
        self.btn_info.config(state="disabled")
        threading.Thread(target=self.obtener_info, args=(url,), daemon=True).start()

    def obtener_info(self, url):
        opciones = {'quiet': True, 'skip_download': True, 'extract_flat': 'in_playlist', 'no_warnings': True}
        try:
            with yt_dlp.YoutubeDL(opciones) as ydl:
                self.info_actual = ydl.extract_info(url, download=False)
                
                # Obtener thumbnail
                thumb_url = self.info_actual.get('thumbnail')
                if not thumb_url and 'entries' in self.info_actual:
                    thumb_url = self.info_actual['entries'][0].get('thumbnail')
                
                if thumb_url:
                    res = requests.get(thumb_url, timeout=5)
                    img = Image.open(BytesIO(res.content))
                    img.thumbnail((280, 280))
                    self.portada_tk = ImageTk.PhotoImage(img)
                
                self.root.after(0, self.actualizar_preview)
        except Exception as e:
            err_str = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Info fallida: {err_str}"))
        finally:
            self.root.after(0, lambda: self.btn_info.config(state="normal"))

    def actualizar_preview(self):
        if self.portada_tk:
            self.lbl_img.config(image=self.portada_tk, text="")
        titulo = self.info_actual.get('title', 'N/A')
        canal = self.info_actual.get('uploader', 'N/A')
        tipo = "Playlist/Álbum" if 'entries' in self.info_actual else "Track"
        self.lbl_preview_info.config(text=f" {tipo}\n\nTITULO:\n{titulo}\n\nCANAL:\n{canal}")
        self.lbl_estado.config(text="Info cargada.")

    def progreso_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                p = (d['downloaded_bytes'] / total) * 100
                self.root.after(0, lambda: self.progreso.config(value=p))

    def descargar_thread(self):
        if not self.entrada_url.get(): return
        self.btn_descargar.config(state="disabled")
        threading.Thread(target=self.descargar, daemon=True).start()

    def crear_archivo_m3u(self, ruta_carpeta, nombre_carpeta):
        full_path = os.path.join(ruta_carpeta, nombre_carpeta)
        if not os.path.exists(full_path): return
        
        archivos = [f for f in os.listdir(full_path) if f.endswith(('.mp3', '.flac'))]
        archivos.sort() # Mantener el orden numérico que pusimos
        
        with open(os.path.join(full_path, f"{nombre_carpeta}.m3u"), "w", encoding="utf-8") as m3u:
            m3u.write("#EXTM3U\n")
            for f in archivos:
                m3u.write(f"{f}\n")

    def descargar(self):
        # DECLARACIÓN DE VARIABLES DESDE LA UI
        url = self.entrada_url.get().strip()
        ruta_base = self.var_ruta.get()
        fmt = self.var_fmt.get()
        cal = self.cb_calidad.get().replace("kbps", "")
        user_art = self.ent_artista.get().strip()
        user_alb = self.ent_album.get().strip()
        es_playlist = self.var_modo_playlist.get()

        # Configuración de Plantilla y Carpetas
        if es_playlist:
            # %(playlist_autonumber)s o %(playlist_index)s aseguran el orden 01, 02...
            folder_name = user_alb if user_alb else "%(playlist_title,uploader)s"
            plantilla = os.path.join(ruta_base, folder_name, "%(playlist_index)02d - %(title)s.%(ext)s")
        else:
            art = user_art if user_art else "%(artist,uploader,Unknown Artist)s"
            alb = user_alb if user_alb else "%(album,Unknown Album)s"
            plantilla = os.path.join(ruta_base, art, alb, "%(playlist_index)02d - %(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': plantilla,
            'writethumbnail': True,
            'no_warnings': True,
            'progress_hooks': [self.progreso_hook],
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': fmt, 'preferredquality': cal},
                {'key': 'FFmpegMetadata', 'add_metadata': True},
                {'key': 'EmbedThumbnail'}
            ],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extraer info para aplicar metadatos manuales si existen
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    for i, entry in enumerate(info['entries']):
                        if entry:
                            if user_art: entry['artist'] = user_art
                            if user_alb: entry['album'] = user_alb
                            entry['track_number'] = i + 1
                            ydl.process_info(entry)
                else:
                    if user_art: info['artist'] = user_art
                    if user_alb: info['album'] = user_alb
                    ydl.process_info(info)
                
                # Crear el archivo de playlist si es necesario
                if es_playlist:
                    # Obtenemos el nombre final de la carpeta procesada
                    nombre_final_folder = ydl.prepare_filename(info if 'entries' not in info else info['entries'][0])
                    folder_path = os.path.basename(os.path.dirname(nombre_final_folder))
                    self.crear_archivo_m3u(ruta_base, folder_path)

            self.root.after(0, lambda: messagebox.showinfo("Éxito", "¡Todo listo y ordenado!"))
        except Exception as e:
            err_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", err_msg))
        finally:
            self.root.after(0, lambda: self.btn_descargar.config(state="normal"))
            self.root.after(0, lambda: self.lbl_estado.config(text="Listo"))

if __name__ == "__main__":
    root = tk.Tk()
    app = GestorMusicaRetro(root)
    root.mainloop()