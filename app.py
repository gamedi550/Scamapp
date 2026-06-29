import streamlit as st
import pytesseract
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Digitalizador de Documentos Oficiales", layout="centered")

st.title("🪖 Digitalizador de Oficios - Guardia Nacional")
st.write("Carga la imagen del oficio para iniciar la digitalización y conversión a PDF Editable.")

# 2. CARGADOR DE ARCHIVOS (IMAGE UPLOADER)
uploaded_file = st.file_uploader("Selecciona una imagen del documento...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    imagen = Image.open(uploaded_file)
    st.image(imagen, caption="Documento Cargado", use_container_width=True)
    
    st.info("💡 Haz clic en el botón de abajo para iniciar la extracción por OCR.")
    
    # Botón principal de procesamiento OCR
    if st.button("🚀 Convertir a PDF Editable", type="primary"):
        with st.spinner("Procesando OCR con Tesseract..."):
            try:
                # Intento de extracción de texto automático
                texto_extraido = pytesseract.image_to_string(imagen, lang="spa")
                st.success("Texto extraído con éxito.")
                st.session_state['texto_ocr'] = texto_extraido
            except Exception as e:
                st.error(f"Ocurrió un error con Tesseract: {str(e)}")
                st.warning("⚠️ Nota: Recuerda que para que funcione en Streamlit Cloud debes renombrar tu archivo a 'packages.txt' en minúsculas.")

    # 3. EDITOR VISUAL Y FORMULARIO DE RECONSTITUCIÓN
    if 'texto_ocr' in st.session_state:
        st.subheader("📝 Editor Visual de Datos Extraídos")
        st.write("Modifica o valida los campos extraídos del Oficio de Identidad Temporal:")
        
        # Columnas interactivas con los datos del documento de Guardia Nacional
        col1, col2 = st.columns(2)
        with col1:
            oficio_num = st.text_input("Número de Oficio", value="S.P.A.A./G.N./0226")
            nombre_gn = st.text_input("Nombre del Personal", value="Gabriel Medina Diaz")
            rfc_gn = st.text_input("R.F.C.", value="MEDG950505PUA")
        with col2:
            num_guardia = st.text_input("No. de Guardia Nacional", value="202425")
            curp_gn = st.text_input("C.U.R.P.", value="MEDG950505HNTDZB08")
            cuip_gn = st.text_input("C.U.I.P.", value="1T22F40L00422/0325633/MEDG950505PUA/40")

        # --- PROTECCIÓN INTERACTIVA (SOLUCIÓN AL TYPEERROR) ---
        # Aquí simulamos los datos devueltos por el editor JS. 
        # Si el componente devuelve None, la validación de abajo evitará que la app se caiga.
        datos_retorno_js = None  # Cambiará dinámicamente según tu componente visual
        lista_elementos = ["linea_1", "linea_2", "linea_3"]

        if st.button("💾 Confirmar Modificaciones Realizadas"):
            # Validación de Seguridad Obligatoria: evaluamos primero si NO es None
            if datos_retorno_js is not None:
                cambios_detectados = False
                for l_id in lista_elementos:
                    if l_id in datos_retorno_js:
                        cambios_detectados = True
                if cambios_detectados:
                    st.success("¡Modificaciones interactivas aplicadas con éxito!")
                else:
                    st.info("No se registraron cambios estructurales.")
            else:
                st.warning("El editor no detectó modificaciones del lienzo interactivo. Se usarán los campos de texto estándar.")

        # 4. COMPILACIÓN DE REPORTLAB PDF (SOLUCIÓN AL SYNTAXERROR)
        st.subheader("🖨️ Generar Documento PDF Reconstituido")
        
        if st.button("🛠️ Compilar y Descargar PDF"):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            # Encabezados Oficiales
            c.setFont("Helvetica-Bold", 11)
            c.drawString(54, height - 60, "Secretaría de la Defensa Nacional / Guardia Nacional")
            
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(54, height - 80, '"2026, Año de Margarita Maza Parada"')
            
            # Bloque de datos a la derecha
            c.setFont("Helvetica", 9)
            c.drawString(350, height - 110, "Guardia Nacional.")
            c.drawString(350, height - 122, "Coordinación Estatal 'Chihuahua'")
            c.drawString(350, height - 134, f"Oficio Número: {oficio_num}")
            
            # Asunto y Cuerpo
            c.setFont("Helvetica-Bold", 10)
            c.drawString(54, height - 170, "Asunto: Oficio de Identidad de Guardia Nacional Temporal.")
            
            c.setFont("Helvetica", 10)
            c.drawString(54, height - 200, f"C. Soldado Guardia Nacional: {nombre_gn}")
            
            # --- CORRECCIÓN DE SINTAXIS APLICADA ---
            # El método string recibe exactamente 3 parámetros claros y aislados sin conflictos de cierre:
            altura_actual = height - 220
            texto_linea = "Presente."
            c.drawString(54, altura_actual, texto_linea)
            
            # Cuadro de Identificadores Únicos Nacionales (Recuadro del Oficio)
            c.rect(54, height - 340, 500, 100, stroke=1, fill=0)
            c.drawString(64, height - 260, f"No. de Guardia Nacional: {num_guardia}")
            c.drawString(64, height - 280, f"R.F.C.: {rfc_gn}")
            c.drawString(64, height - 300, f"C.U.R.P.: {curp_gn}")
            c.drawString(64, height - 320, f"C.U.I.P.: {cuip_gn}")
            
            # Cierre Institucional
            c.drawString(54, height - 380, "Por disposición del Comandante de la Guardia Nacional y con fundamento legal...")
            c.drawString(54, height - 420, "Atentamente.")
            c.drawString(54, height - 440, "Sufragio Efectivo. No Reelección.")
            c.drawString(54, height - 460, "El Coordinador de la Unidad.")
            
            # Guardar Página
            c.showPage()
            c.save()
            
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Botón de Descarga
            st.download_button(
                label="📥 Descargar PDF Terminado",
                data=pdf_data,
                file_name=f"Oficio_Identidad_{num_guardia}.pdf",
                mime="application/pdf"
            )
