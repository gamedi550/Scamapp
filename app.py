import streamlit as st
import pytesseract
from PIL import Image
import io
import re
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Editor de Oficios GN", page_icon="📄", layout="centered")

# Función auxiliar para escribir párrafos sin que se encimen los textos
def escribir_parrafo(c, texto, x, y, ancho_caracteres, espacio_linea, font_name="Helvetica", font_size=9.5, centro=False):
    c.setFont(font_name, font_size)
    lineas = textwrap.wrap(texto, width=ancho_caracteres)
    for linea in lineas:
        if centro:
            c.drawCentredString(x, y, linea)
        else:
            c.drawString(x, y, linea)
        y -= espacio_linea
    return y

# FUNCIÓN PARA GENERAR EL PDF CON EL DISEÑO EXACTO DE TU CAPTURA
def generar_pdf_oficial(datos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # 1. ENCABEZADO INSTITUCIONAL
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#1C1C1C"))
    c.drawString(54, height - 50, "Defensa")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(110, height - 50, "GN")
    
    c.setFont("Helvetica", 7)
    c.drawString(54, height - 60, "SECRETARÍA DE LA DEFENSA NACIONAL")
    c.drawString(110, height - 60, "GUARDIA NACIONAL")
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(54, height - 90, f'"{datos["lema"]}"')
    
    # 2. CUADRO DE DATOS SUPERIOR DERECHO
    c.setLineWidth(0.8)
    c.setStrokeColor(colors.HexColor("#333333"))
    c.rect(width - 254, height - 120, 200, 80, fill=0)
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(width - 244, height - 55, "Guardia Nacional.")
    c.setFont("Helvetica", 8)
    c.drawString(width - 244, height - 67, f"Coordinación Estatal: {datos['coordinacion']}")
    c.drawString(width - 244, height - 79, f"Unidad: {datos['unidad']}")
    c.drawString(width - 244, height - 91, f"Sección: {datos['seccion']}")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(width - 244, height - 108, f"Oficio Número: {datos['num_oficio']}")
    
    # 3. ASUNTO Y FECHA (Derecha)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(width - 270, height - 150, "Asunto:")
    c.setFont("Helvetica", 9)
    c.drawString(width - 265, height - 150, datos['asunto'])
    
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(width - 270, height - 175, "Lugar y Fecha:")
    c.setFont("Helvetica", 9)
    # Ajustar lugar y fecha si es largo
    escribir_parrafo(c, datos['fecha_lugar'], width - 265, height - 175, 45, 12, "Helvetica", 9)
    
    # 4. DESTINATARIO (Izquierda)
    y_doc = height - 210
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(54, y_doc, datos['destinatario_grado'])
    c.drawString(54, y_doc - 14, datos['destinatario_nombre'].upper())
    c.drawString(54, y_doc - 28, "Presente.")
    
    # 5. ANTECEDENTES (Derecha, alineado con destinatario)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawRightString(width - 270, height - 210, "Antecedentes:")
    escribir_parrafo(c, datos['antecedentes'], width - 265, height - 210, 45, 11, "Helvetica", 8)
    
    # 6. CUERPO DEL TEXTO
    y_cuerpo = height - 290
    y_cuerpo = escribir_parrafo(c, datos['cuerpo'], 54, y_cuerpo, 88, 14, "Helvetica", 9.5)
    
    # 7. MATRIZ DE DATOS GENERALES (Centro Inferior)
    y_datos = y_cuerpo - 30
    c.setFont("Helvetica-Bold", 9)
    c.drawString(160, y_datos, f"No. de Guardia Nacional: {datos['no_gn']}")
    c.drawString(160, y_datos - 15, f"R.F.C.: {datos['rfc']}")
    c.drawString(160, y_datos - 30, f"C.U.R.P.: {datos['curp']}")
    c.drawString(160, y_datos - 45, f"C.U.I.P.: {datos['cuip']}")
    c.drawString(160, y_datos - 60, f"Gpo. Sanguíneo y Factor R.H.: {datos['grupo_sangre']}")
    
    # Recuadros simulados para Foto y Huella
    c.rect(54, y_datos - 60, 65, 80, fill=0) # Foto
    c.setFont("Helvetica", 7)
    c.drawCentredString(86, y_datos - 50, "[ FOTO ]")
    
    c.rect(width - 120, y_datos - 60, 65, 80, fill=0) # Huella
    c.drawCentredString(width - 87, y_datos - 50, "[ HUELLA ]")
    
    # 8. TEXTO DE VALIDEZ LEGAL
    y_legal = y_datos - 95
    c.setFont("Helvetica-Bold", 9)
    c.drawString(54, y_legal, "Firma: _______________________")
    
    y_legal_txt = y_legal - 20
    texto_legal = "Este oficio tendrá validez oficial y merecerá fe respecto a la identidad del interesado ante las autoridades ministeriales, judiciales administrativas, oficinas federales y sociedades nacionales de crédito público, por lo que se solicita a todas las autoridades civiles y militares, presenten oportuno y eficaz auxilio al portador de este documento, en el ejercicio de sus atribuciones en materia de Seguridad Pública."
    y_final_legal = escribir_parrafo(c, texto_legal, 54, y_legal_txt, 110, 12, "Helvetica", 8)
    
    # 9. SECCIÓN DE FIRMAS Y CIERRE
    y_firma = y_final_legal - 30
    c.drawCentredString(width / 2.0, y_firma, "Atentamente.")
    c.drawCentredString(width / 2.0, y_firma - 12, "Sufragio Efectivo. No Reelección.")
    c.drawCentredString(width / 2.0, y_firma - 24, datos['firmante_cargo'])
    
    c.setFont("Helvetica-Bold", 9.5)
    c.drawCentredString(width / 2.0, y_firma - 55, datos['firmante_nombre'])
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# INTERFAZ EN STREAMLIT
st.title("📄 Escáner y Editor de Oficios GN")
st.write("Sube la captura de tu oficio. El sistema extraerá los textos y te dejará editarlos en los cuadros de abajo antes de generar el PDF final.")

# Valores por defecto idénticos a tu captura real
if 'form_datos' not in st.session_state:
    st.session_state['form_datos'] = {
        "coordinacion": '"Chihuahua"',
        "unidad": "4/o. Btn. Apoyo para la Admón. y Opn. Aduanas.",
        "seccion": "Administrativa.",
        "num_oficio": "S.P.A.A./G.N./0226",
        "lema": "2026, Año de Margarita Maza Parada",
        "asunto": "Oficio de Identidad de Guardia Nacional Temporal.",
        "fecha_lugar": 'Campo Militar No. 5-B, "Abraham González", Cd. Chihuahua, Chih., a 1/o. de enero de 2026.',
        "destinatario_grado": "C. Soldado Guardia Nacional.",
        "destinatario_nombre": "Gabriel Medina Diaz",
        "antecedentes": "Msje. SWEAR. No. S.P.A. y L./Cred./255/045648 de 24 Dic. 2025, Gdo. por la Cmcia. Gdia. Nal.",
        "cuerpo": "Por disposición del Comandante de la Guardia Nacional y con fundamento en los artículos 21, párrafo Décimo segundo, 123 apartado 'B' fracción XIII de la Constitución Política de los Estados Unidos Mexicanos; 42 de la Ley General del Sistema Nacional de Seguridad Pública; 3 de la Ley Federal del Procedimiento Administrativo; 9, 11 fracción I, 12 fracción IV, 18, 21 fracción IV, 18, 21 fracción III de la Ley de la Guardia Nacional; 2 fracción IX, 6, 14, 18 fracción IX, del Reglamento de la Ley de la Guardia Nacional.\n\nEsta Coordinación de Batallón a mi cargo, expide el presente Oficio de Identificación Temporal, el cual tendrá una vigencia del 1/o. de Enero al 31 de diciembre del 2026, del C. Soldado Guardia Nacional Gabriel Medina Diaz, asignado al 4/o. Btn. Apoyo para la Admón. y Opn. Aduanas, con sede en Chihuahua, Chih., cuya fotografía aparece en el margen izquierdo, asentado firmado, huella dactilar índice derecho y datos generales siguientes:",
        "no_gn": "202425",
        "rfc": "MEDG950505PUA",
        "curp": "MEDG950505HNTDZB08",
        "cuip": "1T22F40L00422/0325633/MEDG950505PUA/40",
        "grupo_sangre": "O+",
        "firmante_cargo": "El Coronel G.N. Comandante del Batallón",
        "firmante_nombre": "CORONEL G.N. DEM. JOSÉ FRANCISCO RODRÍGUEZ ESTRADA"
    }

# LÓGICA DE CARGA DESDE LA CAPTURA
with st.expander("📸 PASO 1: Subir Captura / Foto del Oficio", expanded=True):
    archivo_foto = st.file_uploader("Selecciona la imagen del oficio:", type=["jpg", "jpeg", "png"])
    if archivo_foto is not None:
        if st.button("🔍 Analizar foto y extraer textos", type="secondary"):
            with st.spinner("Procesando imagen con Tesseract OCR..."):
                try:
                    img = Image.open(archivo_foto)
                    txt_ocr = pytesseract.image_to_string(img, lang='spa')
                    
                    # Buscar patrones de datos clave en la captura
                    rfc_match = re.search(r'[A-Z]{4}\d{6}[A-Z0-9]{3}', txt_ocr)
                    curp_match = re.search(r'[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d', txt_ocr)
                    gn_match = re.search(r'(Nacional:|Guardia:)\s*(\d+)', txt_ocr, re.IGNORECASE)
                    
                    if rfc_match: st.session_state['form_datos']['rfc'] = rfc_match.group(0)
                    if curp_match: st.session_state['form_datos']['curp'] = curp_match.group(0)
                    if gn_match: st.session_state['form_datos']['no_gn'] = gn_match.group(2)
                    
                    st.success("¡Lectura completada! Revisa y modifica los campos extraídos abajo.")
                except Exception as e:
                    st.error(f"Error al procesar la imagen: Asegúrate de completar el Paso 1 de las instrucciones en GitHub. Detalle: {e}")

# FORMULARIO CON CAMPOS TOTALMENTE MODIFICABLES
st.subheader("📝 PASO 2: Modificar Datos Extraídos")
st.write("Cualquier texto que cambies aquí se reflejará perfectamente ordenado en el PDF:")

col1, col2 = st.columns(2)
with col1:
    coordinacion = st.text_input("Coordinación Estatal", st.session_state['form_datos']['coordinacion'])
    unidad = st.text_input("Unidad / Batallón", st.session_state['form_datos']['unidad'])
    num_oficio = st.text_input("Número de Oficio", st.session_state['form_datos']['num_oficio'])
    destinatario_nombre = st.text_input("Nombre del Elemento", st.session_state['form_datos']['destinatario_nombre'])
    rfc = st.text_input("R.F.C.", st.session_state['form_datos']['rfc'])
    curp = st.text_input("C.U.R.P.", st.session_state['form_datos']['curp'])

with col2:
    asunto = st.text_input("Asunto del Oficio", st.session_state['form_datos']['asunto'])
    fecha_lugar = st.text_input("Lugar y Fecha", st.session_state['form_datos']['fecha_lugar'])
    destinatario_grado = st.text_input("Grado del Destinatario", st.session_state['form_datos']['destinatario_grado'])
    no_gn = st.text_input("No. de Guardia Nacional", st.session_state['form_datos']['no_gn'])
    cuip = st.text_input("C.U.I.P.", st.session_state['form_datos']['cuip'])
    grupo_sangre = st.text_input("Grupo Sanguíneo", st.session_state['form_datos']['grupo_sangre'])

antecedentes = st.text_area("Antecedentes", st.session_state['form_datos']['antecedentes'])
cuerpo = st.text_area("Cuerpo del Oficio", st.session_state['form_datos']['cuerpo'], height=180)

st.write("---")
st.subheader("✒️ Autoridad que Firma")
firmante_cargo = st.text_input("Cargo del Firmante", st.session_state['form_datos']['firmante_cargo'])
firmante_nombre = st.text_input("Nombre Completo del Firmante", st.session_state['form_datos']['firmante_nombre'])

# Recopilar los datos actualizados del formulario
datos_finales = {
    "coordinacion": coordinacion, "unidad": unidad, "seccion": st.session_state['form_datos']['seccion'],
    "num_oficio": num_oficio, "lema": st.session_state['form_datos']['lema'], "asunto": asunto,
    "fecha_lugar": fecha_lugar, "destinatario_grado": destinatario_grado, "destinatario_nombre": destinatario_nombre,
    "antecedentes": antecedentes, "cuerpo": cuerpo, "no_gn": no_gn, "rfc": rfc, "curp": curp,
    "cuip": cuip, "grupo_sangre": grupo_sangre, "firmante_cargo": firmante_cargo, "firmante_nombre": firmante_nombre
}

# PASO 3: DESCARGA
st.write("---")
if st.button("🖨️ Generar PDF Editable", type="primary"):
    pdf_data = generar_pdf_oficial(datos_finales)
    st.success("¡Documento PDF formateado con éxito!")
    st.download_button(
        label="📥 Descargar PDF Impresion Impecable",
        data=pdf_data,
        file_name=f"Oficio_Procesado_{no_gn}.pdf",
        mime="application/pdf"
    )
