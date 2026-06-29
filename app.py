import streamlit as st
import pytesseract
from PIL import Image
import io

# 1. Configuración de la aplicación
st.set_page_config(page_title="Digitalizador y Editor OCR", page_icon="📄", layout="centered")

st.title("📄 Digitalizador y Editor de Documentos")
st.write("Sube una imagen para extraer su texto, editarlo directamente o guardarlo como PDF.")

# 2. Selector de archivos
uploaded_file = st.file_uploader("Cargar Imagen del Documento", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # Abrir y mostrar la imagen cargada
        imagen = Image.open(uploaded_file)
        st.image(imagen, caption="Documento Cargado", use_container_width=True)
        
        st.info("💡 Haz clic en el botón de abajo para procesar el documento.")
        
        # 3. Botón de procesamiento
        if st.button("🚀 Iniciar Procesamiento OCR", type="primary"):
            with st.spinner("Analizando documento y extrayendo texto..."):
                
                # Generar las dos opciones: PDF Sándwich y Texto Puro
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(imagen, extension='pdf', lang='spa')
                texto_extraido = pytesseract.image_to_string(imagen, lang='spa')
                
                # Guardar en el estado de Streamlit para que no se borre al interactuar
                st.session_state['pdf_bytes'] = pdf_bytes
                st.session_state['texto_extraido'] = texto_extraido

        # 4. Mostrar resultados si ya fueron procesados
        if 'texto_extraido' in st.session_state:
            st.success("¡Procesamiento completada con éxito!")
            
            # --- SECCIÓN 1: DESCARGA DE PDF (Para mantener formato, sellos y firmas) ---
            st.subheader("Opción 1: Descargar como PDF Buscable")
            st.write("Mantiene el diseño exacto de la foto, permitiendo seleccionar y copiar el texto desde un lector de PDF.")
            st.download_button(
                label="📥 Descargar PDF Seleccionable",
                data=st.session_state['pdf_bytes'],
                file_name="documento_formato.pdf",
                mime="application/pdf"
            )
            
            st.write("---")
            
            # --- SECCIÓN 2: EDITOR DE TEXTO EN PANTALLA (Para modificar libremente) ---
            st.subheader("Opción 2: Editor de Texto Libre")
            st.write("Modifica, borra o escribe lo que quieras directamente aquí abajo:")
            
            # Cuadro de texto totalmente editable por el usuario
            texto_modificado = st.text_area(
                label="Texto detectado (Puedes editarlo aquí):",
                value=st.session_state['texto_extraido'],
                height=400
            )
            
            # Botón para descargar el texto que el usuario editó
            st.download_button(
                label="💾 Descargar Texto Editado (.txt)",
                data=texto_modificado,
                file_name="texto_modificado.txt",
                mime="text/plain"
            )
            
    except Exception as e:
        st.error(f"Ocurrió un error durante el procesamiento: {e}")
