import streamlit as st
from PIL import Image, ImageEnhance
import pydicom
import numpy as np
from io import BytesIO
import os
import logging
from streamlit_drawable_canvas import st_canvas
from pydicom.pixels import apply_voi_lut  # Actualización de importación

logger = logging.getLogger(__name__)

def visualizar_dicom(opciones):
    st.write("---")
    st.header("Visor Avanzado de Imágenes DICOM")

    # Subir múltiples archivos DICOM
    uploaded_files = st.file_uploader(
        "Cargar archivos DICOM",
        type=["dcm", "dicom"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Por favor, carga uno o más archivos DICOM para visualizar.")
        return

    num_imagenes = len(uploaded_files)
    logger.info(f"Cantidad de imágenes cargadas para visualización: {num_imagenes}")

    # Seleccionar la imagen a visualizar
    selected_file = st.selectbox("Selecciona una imagen DICOM para visualizar", uploaded_files, format_func=lambda x: x.name)

    # Botón para abrir el visor
    if st.button("Abrir Visor DICOM"):
        mostrar_visor(selected_file)

def mostrar_visor(selected_file):
    with st.container():
        imagen, ds = procesar_imagen_dicom(selected_file)

        if imagen is not None:
            # Control de brillo y contraste
            col1, col2 = st.columns(2)
            with col1:
                brillo = st.slider("Brillo", -100, 100, 0)
            with col2:
                contraste = st.slider("Contraste", -100, 100, 0)

            # Aplicar ajustes de brillo y contraste
            imagen_editada = ajustar_brillo_contraste(imagen, brillo, contraste)

            # Mostrar imagen
            st.image(imagen_editada, caption=selected_file.name, use_column_width=True)

            # Anotaciones
            st.subheader("Anotar Imagen DICOM")
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=2,
                stroke_color="#000000",
                background_image=imagen_editada,
                update_streamlit=True,
                height=imagen_editada.height,
                width=imagen_editada.width,
                drawing_mode="rectangle",
                key="canvas",
            )

            if canvas_result.json_data is not None:
                st.write("### Anotaciones:")
                st.json(canvas_result.json_data)

            # Opciones de movimiento (simples controles de navegación)
            st.subheader("Mover Imagen")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Mover Arriba"):
                    st.write("Funcionalidad de mover arriba no implementada.")
            with col2:
                if st.button("Mover Centro"):
                    st.write("Funcionalidad de mover al centro no implementada.")
            with col3:
                if st.button("Mover Abajo"):
                    st.write("Funcionalidad de mover abajo no implementada.")

            # Descargar DICOM modificado
            st.subheader("Descargar Imagen DICOM Modificada")
            if st.button("Descargar DICOM"):
                try:
                    # Aplicar los cambios al dataset DICOM
                    # Convertir la imagen editada a escala de grises
                    imagen_gris = imagen_editada.convert("L")
                    # Obtener los datos de píxeles como bytes
                    pixel_data = np.array(imagen_gris)
                    ds.PixelData = pixel_data.tobytes()
                    ds.Rows, ds.Columns = pixel_data.shape

                    dicom_buffer = BytesIO()
                    ds.save_as(dicom_buffer)
                    dicom_buffer.seek(0)
                    st.download_button(
                        label="Descargar DICOM",
                        data=dicom_buffer,
                        file_name=f"modificado_{selected_file.name}",
                        mime="application/dicom"
                    )
                except Exception as e:
                    st.error(f"Error al descargar el archivo DICOM: {e}")
        else:
            st.error(f"No se pudo procesar la imagen {selected_file.name}")

def procesar_imagen_dicom(dicom_file):
    """
    Procesa un archivo DICOM y devuelve la imagen para mostrar y el dataset.
    """
    try:
        dicom = pydicom.dcmread(BytesIO(dicom_file.getvalue()))
        original_image = dicom.pixel_array

        # Aplicar VOI LUT si está disponible
        img_windowed = apply_voi_lut(original_image, dicom)

        # Manejar Photometric Interpretation
        photometric_interpretation = dicom.get('PhotometricInterpretation', 'UNKNOWN')
        if photometric_interpretation == 'MONOCHROME1':
            img_windowed = np.max(img_windowed) - img_windowed

        # Normalizar la imagen para mostrar
        img_normalized_display = (img_windowed - np.min(img_windowed)) / (np.max(img_windowed) - np.min(img_windowed))
        img_normalized_display = (img_normalized_display * 255).astype(np.uint8)

        # Crear imagen para mostrar
        image_display = Image.fromarray(img_normalized_display).convert('L')

        return image_display, dicom

    except Exception as e:
        logger.error(f"Error al procesar el archivo DICOM: {e}")
        st.error(f"Error al procesar el archivo DICOM: {e}")
        return None, None

def ajustar_brillo_contraste(imagen, brillo, contraste):
    """
    Ajusta el brillo y contraste de una imagen PIL.
    """
    try:
        enhancer = ImageEnhance.Brightness(imagen)
        imagen = enhancer.enhance(1 + brillo / 100)

        enhancer = ImageEnhance.Contrast(imagen)
        imagen = enhancer.enhance(1 + contraste / 100)

        return imagen
    except Exception as e:
        logger.error(f"Error al ajustar brillo y contraste: {e}")
        st.error(f"Error al ajustar brillo y contraste: {e}")
        return imagen
