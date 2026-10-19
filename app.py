import os
import json
import shutil
import subprocess
import streamlit as st

st.set_page_config(page_title="Spotify Downloader", page_icon="🎵", layout="centered")

st.title("🎵 Descargador Selectivo de Spotify")
st.write("Busca las canciones de una playlist y elige cuáles descargar.")

# Memoria para guardar la lista de canciones
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
            
            # Comando de spotdl v4 para extraer metadatos
            command = ["spotdl", "save", playlist_url, "--save-file", save_file]
            try:
                subprocess.run(command, capture_output=True, text=True, check=True)
                
                if os.path.exists(save_file):
                    with open(save_file, "r", encoding="utf-8") as f:
                        st.session_state.songs_list = json.load(f)
                    st.success(f"Se encontraron {len(st.session_state.songs_list)} canciones. ¡Selecciona las que quieras abajo!")
                else:
                    st.error("No se pudo obtener la lista. Verifica que la playlist sea pública.")
            except subprocess.CalledProcessError as e:
                st.error(f"Error al buscar la playlist: {e.stderr}")


# --- PASO 2: SELECCIONAR Y DESCARGAR ---
if st.session_state.songs_list:
    st.write("---")
    st.write("### Selecciona las canciones a descargar:")
    
    with st.form("formulario_canciones"):
        seleccionadas = []
        
        for idx, song in enumerate(st.session_state.songs_list):
            titulo = song.get("name", "Desconocido")
            artista = song.get("artist", "Desconocido")
            
            # Formatear el artista si viene como lista
            if isinstance(artista, list):
                artista = ", ".join(artista)
                
            url = song.get("url", "")
            
            if st.checkbox(f"{titulo} - {artista}", key=f"chk_{idx}"):
                seleccionadas.append(url)
                
        boton_descargar = st.form_submit_button("📥 Descargar Seleccionadas")
        
    if boton_descargar:
        if not seleccionadas:
            st.warning("No seleccionaste ninguna canción.")
        else:
            output_dir = "downloaded_music"
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            with st.spinner(f"Descargando {len(seleccionadas)} canciones... Esto tomará un momento."):
                try:
                    urls_file = "urls_seleccionadas.txt"
                    with open(urls_file, "w", encoding="utf-8") as f:
                        for u in seleccionadas:
                            f.write(f"{u}\n")
                    
                    # Comandos actualizados para spotdl v4 (--format y --threads)
                    command = [
                        "spotdl", 
                        urls_file, 
                        "--output", output_dir, 
                        "--format", "m4a", 
                        "--threads", "4"
                    ]
                    
                    subprocess.run(command, capture_output=True, text=True, check=True)
                    
                    files = os.listdir(output_dir)
                    if not files:
                        st.error("Ocurrió un error y no se descargaron los archivos.")
                    else:
                        st.success(f"¡Listo! Se descargaron {len(files)} canciones.")
                        
                        zip_filename = "mis_canciones"
                        shutil.make_archive(zip_filename, "zip", output_dir)
                        
                        with open(f"{zip_filename}.zip", "rb") as f:
                            st.download_button(
                                label="📦 Descargar ZIP con tu música",
                                data=f,
                                file_name="mis_canciones.zip",
                                mime="application/zip",
                            )
                except subprocess.CalledProcessError as e:
                    st.error(f"Error en la descarga: {e.stderr}")
