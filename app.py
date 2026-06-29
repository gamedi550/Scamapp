import io
import cv2
import numpy as np
import pytesseract
import streamlit as st
from reportlab.pdfgen import canvas

# =====================================================================
# CONFIGURACIÓN PARA WINDOWS:
# Si usas Windows, descomenta la línea de abajo y ajusta tu ruta si cambia.
# =====================================================================
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuración de la página web en Streamlit
st.set_page_config(
    page_title="Escáner Inteligente a PDF", page_icon="📸", layout="centered"
)


def procesar_a_pdf(imagen_bytes, idioma):
    """Procesa la imagen en memoria y genera un PDF clonando estilo, tamaño y color."""
    # Convertir los bytes de la imagen subida a un formato que OpenCV entienda
    nparr = np.frombuffer(imagen_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    alto_img, ancho_img, _ = img.shape

    # Crear un buffer en memoria para el PDF (evita escribir archivos basura en el servidor)
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(ancho_img, alto_img))

    # Ejecutar el OCR para obtener las coordenadas de las palabras
    datos = pytesseract.image_to_data(
        img, lang=idioma, output_type=pytesseract.Output.DICT
    )
    n_elementos = len(datos["text"])

    for i in range(n_elementos):
        if int(datos["conf"][i]) > 40 and datos["text"][i].strip() != "":
            texto = datos["text"][i]
            x = datos["left"][i]
            y = datos["top"][i]
            w = datos["width"][i]
            h = datos["height"][i]

            # Muestreo de color de la tinta
            recorte = img[y : y + h, x : x + w]
            if recorte.size == 0:
                continue
            gris_recorte = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
            _, _, min_loc, _ = cv2.minMaxLoc(gris_recorte)

            color_bgr = recorte[min_loc[1], min_loc[0]]
            r, g, b = (
                int(color_bgr[2]),
                int(color_bgr[1]),
                int(color_bgr[0]),
            )

            # Normalizar color para ReportLab (escala 0.0 a 1.0)
            r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
            tamano_fuente = int(h * 0.85)
            y_reportlab = alto_img - (y + h) + (h * 0.12)

            # Escribir palabra con sus propiedades detectadas
            c.setFont("Helvetica", tamano_fuente)
            c.setFillColorRGB(r_norm, g_norm, b_norm)
            c.drawString(x, y_reportlab, texto)

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer


# =====================================================================
# INTERFAZ DE USUARIO (STREAMLIT)
# =====================================================================
st.title("📸 Escáner de Documentos Inteligente")
st.write(
    "Sube una foto de tu documento. La IA extraerá el texto manteniendo su **tamaño, posición y color original** en un PDF totalmente editable."
)

st.sidebar.header("Configuración")
idioma_seleccionado = st.sidebar.selectbox(
    "Idioma del documento:",
    options=["spa", "eng"],
    format_func=lambda x: "Español" if x == "spa" else "Inglés",
)

# Componente para arrastrar y soltar la imagen
archivo_subido = st.file_uploader(
    "Selecciona una imagen (JPG, JPEG, PNG)...", type=["jpg", "jpeg", "png"]
)

if archivo_subido is not None:
    # Mostrar vista previa de la imagen cargada
    st.image(
        archivo_subido,
        caption="Documento Cargado",
        use_container_width=True,
    )

    st.write("---")
    st.info("💡 Haz clic en el botón de abajo para iniciar la digitalización.")

    # Botón para activar el procesamiento
    if st.button("🚀 Convertir a PDF Editable", type="primary"):
        with st.spinner("Analizando tipografías y colores... Por favor espera."):
            try:
                # Leer bytes del archivo subido
                bytes_imagen = archivo_subido.read()

                # Ejecutar la función de conversión
                pdf_resultado = procesar_a_pdf(
                    bytes_imagen, idioma_seleccionado
                )

                st.success("✨ ¡Documento procesado con éxito!")

                # Botón nativo de descarga para el usuario
                st.download_button(
                    label="📥 Descargar PDF Guardando Estilos",
                    data=pdf_resultado,
                    file_name="documento_digitalizado.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Ocurrió un error durante el procesamiento: {e}")
                st.warning(
                    "Asegúrate de que Tesseract OCR esté instalado correctamente en el sistema."
                )
