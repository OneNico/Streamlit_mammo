# src/ui/visual.py

import streamlit as st
from PIL import Image
import os
import logging
from src.modulos.gestion_dicom import gestionar_dicom
from src.modulos.procesamiento_m import procesamiento_masivo

# Configuración del logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def main():
    # Configurar el título de la página en el navegador
    st.set_page_config(page_title="MamoViewer AI", layout="wide")

    # Inyectar CSS personalizado para estilos profesionales y el nuevo diseño del título
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');

    /* Estilos Generales */
    .stImage > img {
        border: 2px solid #00BFFF; /* Celeste */
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
    }
    .stExpander > div {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Roboto', sans-serif;
    }
    .main .block-container{
        padding-top: 2rem;
        padding-right: 3rem;
        padding-left: 3rem;
        padding-bottom: 2rem;
    }

    /* From Uiverse.io by Spacious74 */ 
    .outer {
      width: 800px; /* Aumentado de 800px a 850px para mayor anchura */
      height: 200px;
      border-radius: 10px;
      padding: 1px;
      background: radial-gradient(circle 230px at 0% 0%, #ffffff, #0c0d0d);
      position: relative;
      margin: 0 auto 50px auto; /* Centrado horizontalmente con margen inferior */
      overflow: hidden; /* Evitar que elementos animados salgan del contenedor */
    }

    .dot {
      width: 5px;
      aspect-ratio: 1;
      position: absolute;
      background-color: #fff;
      box-shadow: 0 0 10px #ffffff;
      border-radius: 100px;
      z-index: 2;
      right: 10%;
      top: 10%;
      animation: moveDot 6s linear infinite;
    }

    @keyframes moveDot {
      0%,
      100% {
        top: 10%;
        right: 10%;
      }
      25% {
        top: 10%;
        right: calc(100% - 35px);
      }
      50% {
        top: calc(100% - 25px);
        right: calc(100% - 35px);
      }
      75% {
        top: calc(100% - 25px);
        right: 10%;
      }
    }

    .card {
      z-index: 1;
      width: 100%;
      height: 100%;
      border-radius: 9px;
      border: solid 1px #202222;
      background-size: 20px 20px;
      background: radial-gradient(circle 280px at 0% 0%, #444444, #0c0d0d);
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      flex-direction: column;
      color: #fff;
      overflow-wrap: break-word; /* Añadido para evitar desbordamiento del texto */
    }
    .ray {
      width: 150px;
      height: 30px;
      border-radius: 100px;
      position: absolute;
      background-color: #c7c7c7;
      opacity: 0.4;
      box-shadow: 0 0 50px #fff;
      filter: blur(10px);
      transform-origin: 10%;
      top: 0%;
      left: 0;
      transform: rotate(40deg);
      animation: moveRay 6s linear infinite;
    }

    @keyframes moveRay {
        0% { transform: rotate(40deg); }
        50% { transform: rotate(-40deg); }
        100% { transform: rotate(40deg); }
    }

    .card .text {
      font-weight: bolder;
      font-size: 2.4rem; /* Reducido de 2.5rem a 2.4rem */
      background: linear-gradient(45deg, #000000 4%, #fff, #000);
      background-clip: text;
      color: transparent;
      margin-bottom: 5px;
      text-align: center;
      line-height: 1.2;
      padding: 0 20px; /* Aumentado para agregar más margen interno */
    }

    /* Estilo para resaltar las primeras letras */
    .card .text .highlight {
      color: #FFD700; /* Dorado para destacar */
      background: none;
      -webkit-background-clip: unset;
    }

    .line {
      width: 100%;
      height: 1px;
      position: absolute;
      background-color: #2c2c2c;
    }
    .topl {
      top: 10%;
      background: linear-gradient(90deg, #888888 30%, #1d1f1f 70%);
    }
    .bottoml {
      bottom: 10%;
      background: linear-gradient(90deg, #888888 30%, #1d1f1f 70%);
    }
    .leftl {
      left: 10%;
      width: 1px;
      height: 100%;
      background: linear-gradient(180deg, #747474 30%, #222424 70%);
    }
    .rightl {
      right: 10%;
      width: 1px;
      height: 100%;
      background: linear-gradient(180deg, #747474 30%, #222424 70%);
    }

    /* Estilos para Toggle Switches */
    .toggle-container {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }

    .toggle-container input[type="checkbox"] {
        display: none;
    }

    .toggle-container label {
        position: relative;
        display: inline-block;
        width: 50px;
        height: 24px;
        background-color: #ccc;
        border-radius: 24px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .toggle-container label::after {
        content: "";
        position: absolute;
        width: 20px;
        height: 20px;
        left: 2px;
        top: 2px;
        background-color: white;
        border-radius: 50%;
        transition: transform 0.2s;
    }

    .toggle-container input[type="checkbox"]:checked + label {
        background-color: #00BFFF;
    }

    .toggle-container input[type="checkbox"]:checked + label::after {
        transform: translateX(26px);
    }

    .toggle-label {
        margin-left: 10px;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #333;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # HTML para el título "MamoViewer AI" centrado
    title_html = """
    <div class="outer">
        <div class="dot"></div>
        <div class="card">
            <div class="ray"></div>
            <div class="text">
                <div>MamoViewer AI</div>
            </div>
            <div class="line topl"></div>
            <div class="line leftl"></div>
            <div class="line bottoml"></div>
            <div class="line rightl"></div>
        </div>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    # Barra lateral
    st.sidebar.header("Opciones de Procesamiento")
    tipo_carga = st.sidebar.radio(
        "Selecciona el tipo de carga",
        ["Visor DICOM", "Procesamiento Masivo"]
    )

    opciones = {'tipo_carga': tipo_carga}

    if tipo_carga == "Visor DICOM":
        # Establecer directamente la subsección a "Visor DICOM"
        opciones['subseccion'] = "Visor DICOM"  # Establecer directamente sin opciones adicionales

        gestionar_dicom(opciones)

    elif tipo_carga == "Procesamiento Masivo":
        st.sidebar.write("### Opciones para Procesamiento Masivo de Imágenes")

        # Subir múltiples imágenes (DICOM, PNG, JPG)
        uploaded_images = st.sidebar.file_uploader(
            "Cargar imágenes (DICOM, PNG, JPG)",
            type=["dcm", "dicom", "png", "jpg", "jpeg"],
            accept_multiple_files=True
        )
        opciones['uploaded_images'] = uploaded_images

        if uploaded_images:
            procesamiento_masivo(opciones)
        else:
            st.sidebar.info(
                "Por favor, carga una o más imágenes DICOM, PNG o JPG para realizar el procesamiento masivo.")

