# src/ui/visual.py

import streamlit as st
from PIL import Image
import os
import logging
from src.modulos.gestion_dicom import gestionar_dicom
from src.modulos.procesamiento_i import procesamiento_individual
from src.modulos.procesamiento_m import procesamiento_masivo

# Configuración del logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def main():
    # Aplicar estilos desde styles.css
    with open('src/ui/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Título principal y subtítulo
    st.markdown("""
    <div class="title-container">
        <h1>Procesamiento, Análisis y Clasificación</h1>
        <h2>de Mamografías</h2>
    </div>
    """, unsafe_allow_html=True)

    # Barra lateral
    st.sidebar.header("Opciones de Procesamiento")
    tipo_carga = st.sidebar.radio(
        "Selecciona el tipo de carga",
        ["Diagnóstico Asistido por AI", "Gestión de Imágenes DICOM"]
    )

    opciones = {'tipo_carga': tipo_carga}

    if tipo_carga == "Gestión de Imágenes DICOM":
        st.sidebar.subheader("Opciones para Procesamiento de DICOM")
        subseccion = st.sidebar.radio(
            "Selecciona la subsección",
            ["Exploración de Imágenes DICOM", "Exportar Imágenes a PNG/JPG"]
        )
        opciones['subseccion'] = subseccion

        if subseccion == "Exploración de Imágenes DICOM":
            # Instrucciones
            st.markdown('<p class="instruction-text">Cargue uno o más archivos DICOM para explorar las imágenes.</p>', unsafe_allow_html=True)

            # Opciones para Exploración de Imágenes DICOM
            uploaded_files = st.sidebar.file_uploader(
                "Cargar archivos DICOM",
                type=["dcm", "dicom"],
                accept_multiple_files=True
            )
            opciones['uploaded_files'] = uploaded_files

            # Opciones adicionales
            opciones['mostrar_metadatos'] = st.sidebar.checkbox("Mostrar Metadatos", value=False)
            opciones['aplicar_voilut'] = st.sidebar.checkbox("Aplicar VOI LUT", value=False)
            opciones['invertir_interpretacion'] = st.sidebar.checkbox("Invertir Interpretación Fotométrica", value=False)
            opciones['aplicar_transformaciones'] = st.sidebar.checkbox("Ajustes de Imagen y Filtrado", value=False)

            # Si se selecciona aplicar transformaciones, mostrar las opciones
            if opciones['aplicar_transformaciones']:
                st.sidebar.subheader("Ajustes de Imagen y Filtrado")
                # Crear una lista de transformaciones
                transformaciones = [
                    ('voltear_horizontal', "Volteo Horizontal"),
                    ('voltear_vertical', "Volteo Vertical"),
                    ('brillo_contraste', "Ajuste de Brillo y Contraste"),
                    ('ruido_gaussiano', "Añadir Ruido Gaussiano"),
                    ('recorte_redimension', "Recorte Aleatorio y Redimensionado"),
                    ('desenfoque', "Aplicar Desenfoque")
                ]

                # Diccionario para almacenar las selecciones
                opciones['transformaciones_seleccionadas'] = {}

                for key, label in transformaciones:
                    opciones['transformaciones_seleccionadas'][key] = st.sidebar.checkbox(label=label, value=False, key=key)

            gestionar_dicom(opciones)

        elif subseccion == "Exportar Imágenes a PNG/JPG":
            st.markdown('<p class="instruction-text">Cargue archivos DICOM para convertirlos a formato PNG o JPG.</p>', unsafe_allow_html=True)
            gestionar_dicom(opciones)

    elif tipo_carga == "Diagnóstico Asistido por AI":
        st.sidebar.subheader("Opciones para Clasificación mediante Deep Learning")

        # Nueva Sección: Selección de Sub-sección
        subseccion_ai = st.sidebar.radio(
            "Selecciona el tipo de procesamiento",
            ["Procesamiento Individual", "Procesamiento Masivo"]
        )
        opciones['subseccion_ai'] = subseccion_ai

        if subseccion_ai == "Procesamiento Individual":
            st.sidebar.subheader("Procesamiento Individual")

            # Instrucciones
            st.markdown('<p class="instruction-text">Cargue una imagen en formato DICOM, PNG o JPG para realizar la clasificación.</p>', unsafe_allow_html=True)

            # Subir una imagen (DICOM, PNG, JPG)
            uploaded_image = st.sidebar.file_uploader(
                "Cargar imagen",
                type=["dcm", "dicom", "png", "jpg", "jpeg"],
                accept_multiple_files=False
            )
            opciones['uploaded_image'] = uploaded_image

            procesamiento_individual(opciones)

        elif subseccion_ai == "Procesamiento Masivo":
            st.sidebar.subheader("Procesamiento Masivo")

            # Instrucciones
            st.markdown('<p class="instruction-text">Cargue múltiples imágenes en formato DICOM, PNG o JPG para realizar la clasificación masiva.</p>', unsafe_allow_html=True)

            # Subir múltiples imágenes (DICOM, PNG, JPG)
            uploaded_images = st.sidebar.file_uploader(
                "Cargar imágenes",
                type=["dcm", "dicom", "png", "jpg", "jpeg"],
                accept_multiple_files=True
            )
            opciones['uploaded_images'] = uploaded_images

            procesamiento_masivo(opciones)
