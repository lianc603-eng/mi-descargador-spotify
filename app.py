import os
import shutil
import subprocess
import streamlit as st

st.set_page_config(
    page_title="Spotify Playlist Downloader", page_icon="🎵", layout="centered"
)

st.title("🎵 Descargador de Playlists de Spotify")
st.write(
    "Pega el enlace de una playlist o canción de Spotify para descargarla."
)

# Entrada de texto para el enlace
playlist_url = st.text_input(
    "Enlace de Spotify:", placeholder="https://open.spotify.com/playlist/..."
)

if st.button("Iniciar Descarga", type="primary"):
  if not playlist_url:
    st.warning("Por favor, introduce un enlace válido de Spotify.")
  else:
    # Directorio temporal para las descargas
    output_dir = "downloaded_music"
    if os.path.exists(output_dir):
      shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    with st.spinner(
        "Procesando y descargando canciones... Esto puede tardar unos"
        " minutos."
    ):
      try:
        # Ejecutar spotdl optimizado (formato m4a y 4 descargas simultáneas)
        command = [
            "spotdl", 
            playlist_url, 
            "--output", output_dir, 
            "--format", "m4a", 
            "--threads", "4"
        ]
        
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )

        # Comprobar si se descargaron archivos
        files = os.listdir(output_dir)
        if not files:
          st.error(
              "No se pudieron descargar canciones. Revisa que el enlace sea"
              " público y correcto."
          )
        else:
          st.success(
              f"¡Descarga completada! Se descargaron {len(files)} archivos."
          )

          # Comprimir la carpeta en un archivo .zip
          zip_filename = "spotify_playlist"
          shutil.make_archive(zip_filename, "zip", output_dir)
          zip_path = f"{zip_filename}.zip"

          # Botón para descargar el ZIP
          with open(zip_path, "rb") as f:
            st.download_button(
                label="📥 Descargar Playlist en ZIP",
                data=f,
                file_name="playlist_spotify.zip",
                mime="application/zip",
            )

      except subprocess.CalledProcessError as e:
        st.error(f"Error al ejecutar el descargador: {e.stderr}")
      except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")
