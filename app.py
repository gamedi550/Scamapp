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
st.set_page_config(page_title="Generador de Oficios GN", page_icon="📄", layout="centered")

# FUNCIÓN PARA DIBUJAR EL PDF DESDE CERO CON DISEÑO OFICIAL
def generar_pdf_oficial(datos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Margen izquierdo estándar: 54pt (0.75 pulgada)
    
    # 1. ENCABEZADO ESTILO INSTITUCIONAL (Texto limpio)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#1C1C1C"))
    c.drawString(54, height - 60, "DEFENSA")
    c.setFont("Helvetica", 7)
    c.drawString(54, height - 70, "SECRETARÍA DE LA DEFENSA NACIONAL")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(115, height - 60, "|  GN")
    c.setFont("Helvetica", 7)
    c.drawString(115, height - 70, "   GUARDIA NACIONAL")
    
    # Slogan del año
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(54, height - 105, f'"{datos["lema"]}"')
    
    # 2. CUADRO DE DATOS SUPERIOR DERECHO (Formato Oficial)
    c.setLineWidth(0.8)
    c.setStrokeColor(colors.HexColor("#333333"))
    c.rect(width - 274, height - 130, 220, 85, fill=0)
    
    c.setFont("Helvetica-Bold", 8)
    y_box = height - 60
    c.drawString(width - 264, y_box, "Guardia Nacional")
    c.setFont("Helvetica", 8)
    c.drawString(width - 264, y_box - 12, f"Coordinación Estatal: {datos['coordinacion']}")
    c.drawString(width - 264, y_box - 24, f"Unidad: {datos['unidad']}")
    c.drawString(width - 264, y_box - 36, f"Sección: {datos['seccion']}")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(width - 264, y_box - 52, f"Oficio Número: {datos['num_oficio']}")
    
    # 3. ASUNTO, LUGAR Y FECHA
    c.setFont("Helvetica-Bold", 9)
    c.drawString(270, height - 160, "Asunto:")
    c.setFont("Helvetica", 9)
    c.drawString(310, height - 160, datos['asunto'])
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(270, height - 180, "Lugar y Fecha:")
    c.setFont("Helvetica", 9)
    c.drawString(340, height - 180, datos['fecha_lugar'])
    
    # 4. DESTINATARIO
    c.setFont("Helvetica-Bold", 10)
    c.drawString(54, height - 220, f"C. {datos['destinatario_grado'] couplings = datos.get('destinatario_grado', '')}")
    c.drawString(54, height - 234, datos['destinatario_nombre'].upper())
    c.setFont("Helvetica-Bold", 10)
    c.drawString(54, height - 248, "Presente.")
    
    # 5. ANTECEDENTES
    c.setFont("Helvetica-Bold", 9)
    c.drawString(270, height - 280, "Antecedentes:")
    c.setFont("Helvetica", 8)
    lineas_ant = textwrap.wrap(datos['antecedentes'], width=45)
    y_ant = height - 280
    for l_ant in lineas_ant:
        c.drawString(345, y_ant, l_ant)
        y_ant -= 11
        
    # 6. CUERPO DEL TEXTO
    c.setFont("Helvetica", 9.5)
    textobject = c.beginText(54, height - 340)
    textobject.setLeading(14)
    lineas_cuerpo = textwrap.wrap(datos['cuerpo'], width=100)
    for line in lineas_cuerpo:
        textobject.textLine(line)
    c.drawText(textobject)
    
    # 7. DATOS GENERALES (Mesa de control inferior)
    y_datos = height - 510
    c.setFont("Helvetica-Bold", 9)
    c.drawString(180, y_datos, f"No. de Guardia Nacional: {datos['no_gn']}")
    c.drawString(180, y_datos - 15, f"R.F.C.: {datos['rfc']}")
    c.drawString(180, y_datos - 30, f"C.U.R.P.: {datos['curp']}")
    c.drawString(180, y_datos - 45, f"C.U.I.P.: {datos['cuip']}")
    c.drawString(180, y_datos - 60, f"Gpo. Sanguíneo y Factor R.H.: {datos['grupo_sangre']}")
    
    # 8. SECCIÓN DE FIRMAS
    c.setFont("Helvetica", 9.5)
    c.drawCentredString(width / 2.0, y_datos - 110, "Atentamente.")
    c.drawCentredString(width / 2.0, y_datos - 122, "Sufraquio Efectivo. No Reelección.")
    c.drawCentredString(width / 2.0, y_datos - 134, datos['firmante_cargo'])
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2.0, y_datos - 180, datos['firmante_nombre'])
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# LÓGICA DE LA APLICACIÓN EN STREAMLIT
st.title("🖨️ Escáner y Editor de Oficios Oficiales")
st.write("Sube una foto para auto-completar los datos o llena el formato manualmente para descargar un PDF editable impecable.")

# Inicializar variables por defecto en el estado de la app
if 'form_datos' not_in st.session_state:
    st.session_state['form_datos'] = {
        "coordinacion": '"Chihuahua"',
        "unidad": "4/o. Btn. Apoyo para la Admón. y Opn. Aduanas.",
        "seccion": "Administrativa.",
        "num_oficio": "S.P.A.A./G.N./0226",
        "lema": "2026, Año de Margarita Maza Parada",
        "asunto": "Oficio de Identidad de Guardia Nacional Temporal.",
        "fecha_lugar": 'Campo Militar No. 5-B, "Abraham González", Cd. Chihuahua, Chih., a 1/o. de enero de 2026.',
        "destinatario_grado": "Soldado Guardia Nacional",
        "destinatario_nombre": "Gabriel Medina Diaz",
        "antecedentes": "Msje. SWEAR. No. S.P.A. y L./Cred./255/045648 de 24 Dic. 2025, Gdo. por la Cmcia. Gdia. Nal.",
        "cuerpo": "Por disposición del Comandante de la Guardia Nacional y con fundamento en los artículos 21... Esta Coordinación de Batallón a mi cargo, expide el presente Oficio de Identificación Temporal, el cual tendrá una vigencia del 1/o. de Enero al 31 de diciembre del 2026...",
        "no_gn": "202425",
        "rfc": "MEDG950505PUA",
        "curp": "MEDG950505HNTDZB08",
        "cuip": "1T22F40L00422/0325633/MEDG950505PUA/40",
        "grupo_sangre": "O+ Sanguíneo y Factor R.H.: O+",
        "firmante_cargo": "El Coronel G.N. Coordinador de Unidad",
        "firmante_nombre": "CORONEL G.N. JOSÉ FRANCISCO RODRÍGUEZ ESTRADA"
    }

# SECCIÓN 1: ESCANEAR POR FOTO (OPCIONAL)
with st.expander("📸 PASO OPTATIVO: Escanear desde una Foto/Imagen", expanded=True):
    archivo_foto = st.file_uploader("Carga la foto del oficio para extraer los textos automáticamente:", type=["jpg", "jpeg", "png"])
    if archivo_foto is not None:
        if st.button("🔍 Analizar y Autocompletar Formulario"):
            with st.spinner("Leyendo caracteres de la imagen..."):
                img = Image.open(archivo_foto)
                txt_ocr = pytesseract.image_to_string(img, lang='spa')
                
                # Intentar extraer identificadores usando expresiones regulares (Regex)
                rfc_match = re.search(r'[A-Z]{4}\d{6}[A-Z0-9]{3}', txt_ocr)
                curp_match = re.search(r'[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d', txt_ocr)
                gn_match = re.search(r'No\.\s*de\s*Guardia\s*Nacional:\s*(\d+)', txt_ocr, re.IGNORECASE)
                
                # Actualizar lo que se encuentre de forma inteligente
                if rfc_match: st.session_state['form_datos']['rfc'] = rfc_match.group(0)
                if curp_match: st.session_state['form_datos']['curp'] = curp_match.group(0)
                if gn_match: st.session_state['form_datos']['no_gn'] = gn_match.group(1)
                
                st.success("¡Análisis finalizado! Los datos detectados se han cargado en el formulario de abajo.")

# SECCIÓN 2: FORMULARIO TOTALMENTE EDITABLE
st.subheader("📝 Modificar Datos del Oficio")
st.write("Haz clic en cualquier campo para editar el texto libremente:")

col1, col2 = st.columns(2)

with col1:
    coordinacion = st.text_input("Coordinación Estatal", st.session_state['form_datos']['coordinacion'])
    unidad = st.text_input("Unidad / Batallón", st.session_state['form_datos']['unidad'])
    num_oficio = st.text_input("Número de Oficio", st.session_state['form_datos']['num_oficio'])
    destinatario_nombre = st.text_input("Nombre del Elemento", st.session_state['form_datos']['destinatario_nombre'])
    rfc = st.text_input("R.F.C.", st.session_state['form_datos']['rfc'])
    curp = st.text_input("C.U.R.P.", st.session_state['form_datos']['curp'])

with col2:
    asunto = st.text_input("Asunto", st.session_state['form_datos']['asunto'])
    fecha_lugar = st.text_input("Lugar y Fecha de Emisión", st.session_state['form_datos']['fecha_lugar'])
    destinatario_grado = st.text_input("Grado", st.session_state['form_datos']['destinatario_grado'])
    no_gn = st.text_input("No. de Guardia", st.session_state['form_datos']['no_gn'])
    cuip = st.text_input("C.U.I.P.", st.session_state['form_datos']['cuip'])
    grupo_sangre = st.text_input("Grupo Sanguíneo", st.session_state['form_datos']['grupo_sangre'])

antecedentes = st.text_area("Antecedentes del Oficio", st.session_state['form_datos']['antecedentes'])
cuerpo = st.text_area("Cuerpo Principal del Documento", st.session_state['form_datos']['cuerpo'], height=150)

st.write("---")
st.subheader("✒️ Datos del Firmante (Autoridad)")
firmante_cargo = st.text_input("Cargo de quien firma", st.session_state['form_datos']['firmante_cargo'])
firmante_nombre = st.text_input("Nombre de quien firma", st.session_state['form_datos']['firmante_nombre'])

# Guardar cambios en el estado
dic_datos_actualizados = {
    "coordinacion": coordinacion, "unidad": unidad, "seccion": st.session_state['form_datos']['seccion'],
    "num_oficio": num_oficio, "lema": st.session_state['form_datos']['lema'], "asunto": asunto,
    "fecha_lugar": fecha_lugar, "destinatario_grado": destinatario_grado, "destinatario_nombre": destinatario_nombre,
    "antecedentes": antecedentes, "cuerpo": cuerpo, "no_gn": no_gn, "rfc": rfc, "curp": curp,
    "cuip": cuip, "grupo_sangre": grupo_sangre, "firmante_cargo": firmante_cargo, "firmante_nombre": firmante_nombre
}

# SECCIÓN 3: GENERAR Y DESCARGAR PDF LIMPIO Y SELECCIONABLE
if st.button("🖨️ Generar PDF con Formato Oficial", type="primary"):
    pdf_final = generar_pdf_oficial(dic_datos_actualizados)
    
    st.success("¡PDF generado perfectamente con tipografía digital!")
    st.download_button(
        label="📥 Descargar PDF Listo para Imprimir",
        data=pdf_final,
        file_name=f"Oficio_Identidad_{no_gn}.pdf",
        mime="application/pdf"
    )
