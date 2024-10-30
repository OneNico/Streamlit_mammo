import streamlit as st
from PIL import Image
import pydicom
import numpy as np
from io import BytesIO
import os
import logging
from streamlit_drawable_canvas import st_canvas
#ok

logger = logging.getLogger(__name__)

def visualizar_dicom(opciones):
    st.write("---")
    st.header("Visor Avanzado de Imágenes DICOM")

    uploaded_files = opciones.get('uploaded_files', [])
    if not uploaded_files:
        st.info("No has cargado ningún archivo DICOM.")
        return

    num_imagenes = len(uploaded_files)
    logger.info(f"Cantidad de imágenes cargadas para visualización: {num_imagenes}")

    if num_imagenes == 0:
        st.info("No has cargado ningún archivo DICOM.")
        return

    # Seleccionar la imagen a visualizar
    selected_file = st.selectbox("Selecciona una imagen DICOM para visualizar", uploaded_files, format_func=lambda x: x.name)

    # Procesar la imagen seleccionada
    imagen, ds = procesar_imagen_dicom(selected_file)

    if imagen is not None:
        st.image(imagen, caption=selected_file.name, use_column_width=True)

        # Anotaciones
        st.subheader("Anotar Imagen DICOM")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_image=imagen,
            update_streamlit=True,
            height=imagen.height,
            width=imagen.width,
            drawing_mode="rectangle",
            key="canvas",
        )

        if canvas_result.json_data is not None:
            st.write("### Anotaciones:")
            st.json(canvas_result.json_data)

        # Descargar DICOM original
        st.subheader("Descargar Imagen DICOM")
        dicom_bytes = selected_file.getvalue()
        st.download_button(
            label="Descargar DICOM",
            data=dicom_bytes,
            file_name=selected_file.name,
            mime="application/dicom"
        )

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
        if hasattr(pydicom.pixel_data_handlers, 'apply_voi_lut'):
            img_windowed = pydicom.pixel_data_handlers.apply_voi_lut(original_image, dicom)
        else:
            img_windowed = original_image

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
