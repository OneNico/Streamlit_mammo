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
    # Inyectar CSS personalizado para estilos profesionales y el nuevo diseño del título
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

    /* Estilos Generales */
    body {
        background-color: #f7f9fc; /* Fondo gris suave */
        color: #333333; /* Texto en color oscuro */
        font-family: 'Roboto', sans-serif;
    }

    /* Estilos de Contenedores y Secciones */
    .main .block-container{
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }

    /* Estilos de Títulos y Subtítulos */
    h1, h2, h3, h4, h5, h6 {
        color: #2E4053; /* Azul oscuro */
        font-weight: 700;
    }

    /* Estilos de Instrucciones */
    .instruction-text {
        color: #555555; /* Gris oscuro para instrucciones */
        font-size: 16px;
        margin-bottom: 20px;
    }

    /* Estilos de la Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6; /* Fondo claro */
        color: #333333;
    }

    /* Estilos de Widgets en la Barra Lateral */
    [data-testid="stSidebar"] .st-radio label, 
    [data-testid="stSidebar"] .st-checkbox label {
        color: #333333;
    }

    /* Estilos de Botones */
    .stButton>button {
        background-color: #2E86C1; /* Azul médico */
        color: white;
        border-radius: 5px;
        height: 50px;
        font-size: 16px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #21618C; /* Azul más oscuro al pasar el cursor */
        color: white;
    }

    /* Estilos de Inputs y Selectboxes */
    .stSelectbox, .stFileUploader, .stCheckbox, .stRadio {
        margin-bottom: 20px;
    }

    /* Estilos de la Barra de Progreso */
    .stProgress > div > div {
        background-color: #2E86C1; /* Azul médico */
    }

    /* Estilos de Mensajes Informativos */
    .stAlert {
        background-color: #D6EAF8; /* Azul claro */
        color: #154360; /* Azul oscuro para texto */
        border-left: 4px solid #2E86C1;
    }

    /* Estilos de Imágenes */
    .stImage > img {
        border: 2px solid #2E86C1; /* Borde azul médico */
        border-radius: 10px;
    }

    /* Estilos de Expander */
    .st-expander {
        background-color: #f0f2f6; /* Fondo claro */
    }

    /* Estilos de Checkbox y Radio Buttons */
    .stCheckbox label, .stRadio label {
        color: #333333;
    }

    /* Estilos de Texto */
    p, label {
        font-size: 16px;
    }

    /* Estilos de Enlaces */
    a {
        color: #2E86C1;
    }

    /* Ajustes de Espaciado */
    .css-1kyxreq {
        margin-bottom: 20px;
    }

    /* Estilos para el Título Principal */
    .title-container {
        text-align: center;
        margin-bottom: 40px;
    }

    .title-text {
        font-size: 36px;
        font-weight: bold;
        color: #2E4053;
        line-height: 1.2;
    }

    .subtitle-text {
        font-size: 24px;
        color: #2E4053;
        margin-top: 10px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # HTML para el título principal y subtítulo
    title_html = """
    <div class="title-container">
        <div class="title-text">Procesamiento, Análisis y Clasificación</div>
        <div class="subtitle-text">de Mamografías</div>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)

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
