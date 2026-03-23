# 🎵 Gestor de Música Retro (Downloader & Organizer)

Este es un gestor de descargas automatizado escrito en Python. Permite bajar álbumes completos o canciones individuales desde YouTube con portadas incrustadas, metadatos corregidos y organización automática de carpetas (`Artista / Álbum / Canción`).

Es el compañero de software para mi proyecto de hardware de reproductor de música DIY.

## 🚀 Características
* 📥 Descarga en formato **MP3 (128k a 320k)** o **FLAC (Lossless)**.
* 🖼️ Incrusta automáticamente la **portada del álbum** y etiquetas ID3.
* 📂 Organización automática de carpetas por artista y álbum.
* ✍️ Opción de corregir metadatos manualmente si YouTube no los tiene.
* 📊 Barra de progreso en tiempo real.

---

## 🛠️ Requisitos Previos (IMPORTANTE)

Para que el programa pueda convertir el audio y pegar las portadas, **DEBES** tener instalado **FFmpeg** en tu sistema:

* **Linux (Arch):** `sudo pacman -S ffmpeg nodejs`
* **Linux (Ubuntu/Debian):** `sudo apt install ffmpeg nodejs`
* **Windows:** Descarga el binario desde [ffmpeg.org](https://ffmpeg.org/download.html) y agrégalo al PATH de tu sistema.

---

## 💻 Instalación y Uso

Sigue estos pasos para ejecutarlo en cualquier ordenador (Windows, Linux o Mac):

## 🛠️ Requisitos Externos
Es necesario tener **FFmpeg** y **Node.js** instalados en el sistema:
* **Arch Linux:** `sudo pacman -S ffmpeg nodejs deno`
* **Ubuntu/Debian:** `sudo apt install ffmpeg nodejs`
* **Windows:** Descargar FFmpeg y Node.js y añadirlos al PATH.

## 🚀 Instalación Rápida
### Linux (Terminal)
1. `git clone https://github.com/DAMN-Day/https://github.com/DAMN-Day/GestorMusica.git`
2. `cd tu-repo`
3. `python -m venv venv-py && source venv-py/bin/activate`
4. `pip install yt-dlp`
5. `python reproductor-descargador.py`

### Windows (PowerShell)
1. `git clone ...`
2. `python -m venv venv-py`
3. `.\venv-py\Scripts\activate`
4. `pip install yt-dlp`
5. `python .\reproductor-descargador.py`
