import streamlit as st
import pytesseract
from PIL import Image
import io

# 1. Configuración de la aplicación
st.set_page_config(page_title="Digitalizador OCR", page_icon="📄", layout="centered")

st.title("📄 Digitalizador de Documentos")
st.write("Sube una imagen para convertirla en un PDF con texto seleccionable manteniendo el 100% del formato original.")

# 2. Selector de archivos
uploaded_file = st.file_uploader("Cargar Imagen del Documento", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # Abrir y mostrar la imagen cargada
        imagen = Image.open(uploaded_file)
        st.image(imagen, caption="Documento Cargado", use_container_width=True)
        
        st.info("💡 Haz clic en el botón de abajo para iniciar la digitalización.")
        
        # 3. Botón de procesamiento
        if st.button("🚀 Convertir a PDF Editable", type="primary"):
            with st.spinner("Procesando OCR y generando capa de texto invisible..."):
                
                # Generar el PDF nativo (Sándwich) con el idioma español configurado
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(imagen, extension='pdf', lang='spa')
            
            st.success("¡Digitalización completada con éxito!")
            
            # 4. Botón para descargar el resultado
            st.download_button(
                label="📥 Descargar PDF Editable",
                data=pdf_bytes,
                file_name="documento_digitalizado.pdf",
                mime="application/pdf"
            )
            
    except Exception as e:
        st.error(f"Ocurrió un error durante el procesamiento: {e}")
        st.warning("Nota: Si el error menciona que 'tesseract is not installed', asegúrate de que tu archivo 'packages.txt' esté guardado en minúsculas en GitHub y reinicia la app desde el panel de control.")
