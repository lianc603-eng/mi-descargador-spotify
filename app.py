import os
import json
import shutil
import subprocess
import streamlit as st

st.set_page_config(page_title="Spotify Downloader", page_icon="🎵", layout="centered")

st.title("🎵 Descargador Selectivo de Spotify")
st.write("Busca las canciones de una playlist y elige cuáles descargar.")

# 1. Memoria de la aplicación: Guardamos la lista de canciones para no perderla al interactuar
if "songs_list" not in st.session_state:
    st.session_state.songs_list = []

playlist_url = st.text_input("Enlace de Spotify:", placeholder="https://open.spotify.com/playlist/...")

# --- PASO 1: BUSCAR CANCIONES ---
if st.button("🔍 Buscar Canciones", type="primary"):
    if not playlist_url:
        st.warning("Por favor, introduce un enlace válido.")
    else:
        with st.spinner("Obteniendo la lista de canciones... (Esto es rápido)"):
            save_file = "playlist.spotdl"
            if os.path.exists(save_file):
                os.remove(save_file)
            
            # El comando 'save' de spotdl extrae los metadatos y crea un archivo JSON sin descargar audio
            command = ["spotdl", "save", playlist_url, "--save-file", save_file]
            try:
                subprocess.run(command, capture_output=True, text=True, check=True)
                
                if os.path.exists(save_file):
                    # Leemos el archivo generado para sacar los nombres y artistas
                    with open(save_file, "r", encoding="utf-8") as f:
                        st.session_state.songs_list = json.load(f)
                    st.success(f"Se encontraron {len(st.session_state.songs_list)} canciones. ¡Selecciona las que quieras abajo!")
                else:
                    st.error("No se pudo obtener la lista. Verifica que la playlist sea pública.")
            except subprocess.CalledProcessError as e:
                st.error(f"Error al buscar la playlist: {e.stderr}")


# --- PASO 2: SELECCIONAR Y DESCARGAR ---
# Solo se muestra esta sección si ya hay canciones guardadas en la memoria
if st.session_state.songs_list:
    st.write("---")
    st.write("### Selecciona las canciones a descargar:")
    
    # Usamos un formulario para poder marcar varias casillas antes de enviar la orden de descarga
    with st.form("formulario_canciones"):
        seleccionadas = []
        
        # Generamos una casilla por cada canción
        for idx, song in enumerate(st.session_state.songs_list):
            titulo = song.get("name", "Desconocido")
            artista = song.get("artist", "Desconocido")
            url = song.get("url", "")
            
            # Si el usuario marca la casilla, guardamos la URL de esa canción
            if st.checkbox(f"{titulo} - {artista}", key=f"chk_{idx}"):
                seleccionadas.append(url)
                
        boton_descargar = st.form_submit_button("📥 Descargar Seleccionadas")
        
    # Lógica cuando se presiona el botón de descargar del formulario
    if boton_descargar:
        if not seleccionadas:
            st.warning("No seleccionaste ninguna canción.")
        else:
            output_dir = "downloaded_music"
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            with st.spinner(f"Descargando {len(seleccionadas)} canciones..."):
                try:
                    # Guardamos las URLs seleccionadas en un archivo de texto para dárselo a spotdl
                    urls_file = "urls_seleccionadas.txt"
                    with open(urls_file, "w", encoding="utf-8") as f:
                        for u in seleccionadas:
                            f.write(f"{u}\n")
                    
                    # Ejecutamos spotdl leyendo solo las URLs del archivo de texto
                    command = [
                        "spotdl", 
                        urls_file, 
                        "--output", output_dir, 
                        "--output-format", "m4a", 
                        "--download-threads", "4"
                    ]
                    
                    subprocess.run(command, capture_output=True, text=True, check=True)
                    
                    files = os.listdir(output_dir)
                    if not files:
                        st.error("Ocurrió un error y no se descargaron los archivos.")
                    else:
                        st.success(f"¡Listo! Se descargaron {len(files)} canciones.")
                        
                        # Comprimimos la carpeta en un ZIP
                        zip_filename = "mis_canciones"
                        shutil.make_archive(zip_filename, "zip", output_dir)
                        
                        # Mostramos el botón para descargar el ZIP
                        with open(f"{zip_filename}.zip", "rb") as f:
                            st.download_button(
                                label="📦 Descargar ZIP con tu música",
                                data=f,
                                file_name="mis_canciones.zip",
                                mime="application/zip",
                            )
                except subprocess.CalledProcessError as e:
                    st.error(f"Error en la descarga: {e.stderr}")
