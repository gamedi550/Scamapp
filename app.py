import streamlit as st
import pytesseract
import pandas as pd
from PIL import Image
import io
import base64
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# CONFIGURACIÓN DE PÁGINA ANCHA PARA EL EDITOR VISUAL
st.set_page_config(page_title="Editor Visual sobre Oficio", page_icon="🖼️", layout="wide")

# Función para convertir la imagen cargada a Base64 y pasarla al contenedor HTML
def img_a_base64(img_pil):
    buffered = io.BytesIO()
    img_pil.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# FUNCIÓN PARA GENERAR EL PDF DIGITAL LIMPIO RECONSTRUYENDO LAS COORDENADAS
def generar_pdf_limpio_coordenadas(lineas_datos, orig_w, orig_h):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    pdf_w, pdf_h = letter
    
    # Márgenes de cortesía de 0.5 pulgadas (36 puntos)
    margen = 36
    max_pdf_w = pdf_w - (margen * 2)
    max_pdf_h = pdf_h - (margen * 2)
    
    # Escala uniforme para encajar la imagen original en el tamaño Carta
    escala = min(max_pdf_w / orig_w, max_pdf_h / orig_h)
    
    # Centrar el contenido en la página PDF
    offset_x = margen + (max_pdf_w - (orig_w * escala)) / 2
    offset_y = margen + (max_pdf_h - (orig_h * escala)) / 2
    
    for linea in lineas_datos:
        texto_editado = linea['text']
        if not texto_editado.strip():
            continue  # Si el usuario borró todo el texto, no lo dibuja
            
        x = linea['x']
        y = linea['y']
        h = linea['h']
        
        # Conversión del sistema de coordenadas: Top-Left (Imagen) a Bottom-Left (ReportLab PDF)
        pdf_x = offset_x + (x * escala)
        pdf_y = pdf_h - (offset_y + ((y + h) * escala))
        
        # Tamaño dinámico de fuente proporcional a la altura de la caja detectada
        font_size = max(h * escala * 0.9, 7)
        
        # Detectar palabras institucionales comunes para aplicar negritas automáticamente
        txt_upper = texto_editado.upper()
        if any(w in txt_upper for w in ["DEFENSA", "GUARDIA NACIONAL", "SECRETARÍA", "ASUNTO:", "ATENTAMENTE"]):
            c.setFont("Helvetica-Bold", font_size)
        else:
            c.setFont("Helvetica", font_size)
            
        c.drawString(pdf_x, pdf_y, texto_editado)
        
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# INTERFAZ PRINCIPAL
st.title("🖼️ Editor de Texto sobre la Imagen (Lienzo OCR)")
st.write("Sube la captura de tu oficio. Los cuadros de texto editables se posicionarán exactamente encima del texto detectado.")

archivo_foto = st.file_uploader("Sube la imagen del oficio (.jpg, .jpeg, .png):", type=["jpg", "jpeg", "png"])

if archivo_foto is not None:
    img_pil = Image.open(archivo_foto)
    orig_w, orig_h = img_pil.size
    
    # Controlar estados de sesión para no repetir el OCR innecesariamente
    if 'current_img' not in st.session_state or st.session_state['current_img'] != archivo_foto.name:
        with st.spinner("Analizando geometría espacial del documento..."):
            # Obtener el DataFrame detallado de posiciones con Tesseract
            datos_ocr = pytesseract.image_to_data(img_pil, output_type=pytesseract.Output.DICT)
            df = pd.DataFrame(datos_ocr)
            
            # Filtrar filas sin texto o vacías
            df = df[df['text'].str.strip().str.len() > 0]
            
            # Agrupar palabras por bloques y líneas de lectura para crear inputs de frases completas
            lineas_mapeadas = []
            if not df.empty:
                grouped = df.groupby(['block_num', 'line_num'])
                for (b_num, l_num), group in grouped:
                    group = group.sort_values(by='left') # Asegurar orden de lectura horizontal
                    texto_completo_linea = " ".join(group['text'].astype(str).tolist())
                    
                    # Calcular caja contenedora de la línea completa
                    x_min = int(group['left'].min())
                    y_min = int(group['top'].min())
                    w_max = int((group['left'] + group['width']).max() - x_min)
                    h_max = int((group['top'] + group['height']).max() - y_min)
                    
                    lineas_mapeadas.append({
                        "id": f"inp_{b_num}_{l_num}",
                        "text": texto_completo_linea,
                        "x": x_min, "y": y_min, "w": w_max, "h": h_max
                    })
            
            st.session_state['ocr_lineas'] = lineas_mapeadas
            st.session_state['current_img'] = archivo_foto.name
            st.session_state['pdf_listo'] = None

    # Ancho fijo del lienzo visual en la pantalla de Streamlit
    ancho_pantalla = 780
    ratio_escala = ancho_pantalla / orig_w
    alto_pantalla = int(orig_h * ratio_escala)
    
    # Preparar datos base64 y JSON para el iframe de edición
    img_b64 = img_a_base64(img_pil)
    diccionario_textos = {linea['id']: linea['text'] for linea in st.session_state['ocr_lineas']}
    json_textos = json.dumps(diccionario_textos)
    
    # Construcción dinámica de los campos de texto HTML colocados de forma absoluta sobre el fondo
    inputs_html = ""
    for linea in st.session_state['ocr_lineas']:
        lx = linea['x'] * ratio_escala
        ly = linea['y'] * ratio_escala
        lw = linea['w'] * ratio_escala
        lh = linea['h'] * ratio_escala
        
        # Dar un margen mínimo de comodidad para escribir de forma táctil/cursor
        pad_h = max(lh, 18)
        font_size_ui = max(lh * 0.85, 11)
        texto_escapado = linea['text'].replace('"', '&quot;')
        
        inputs_html += f"""
        <input type="text" id="{linea['id']}" value="{texto_escapado}" class="caja-flotante"
               style="left:{lx}px; top:{ly}px; width:{lw}px; height:{pad_h}px; font-size:{font_size_ui}px;"
               oninput="actualizarTexto('{linea['id']}', this.value)">
        """
    
    # CÓDIGO HTML/CSS/JS INTEGRADO PARA EL COMPONENTE VISUAL
    codigo_iframe = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 10px; background-color: #f8f9fa; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; }}
            .lienzo {{
                position: relative;
                width: {ancho_pantalla}px;
                height: {alto_pantalla}px;
                background-image: url(data:image/jpeg;base64,{img_b64});
                background-size: 100% 100%;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                box-shadow: 0px 8px 24px rgba(0,0,0,0.12);
            }}
            .caja-flotante {{
                position: absolute;
                background: rgba(255, 255, 180, 0.45); /* Color amarillo traslúcido sobre el texto original */
                border: 1px solid rgba(0, 120, 255, 0.4);
                color: #000;
                font-family: Arial, sans-serif;
                font-weight: bold;
                box-sizing: border-box;
                padding: 0 3px;
                border-radius: 2px;
                transition: all 0.2s;
            }}
            .caja-flotante:focus {{
                background: rgba(255, 255, 255, 0.98);
                border: 2px solid #007bff;
                box-shadow: 0 0 8px rgba(0, 123, 255, 0.5);
                outline: none;
                z-index: 9999;
            }}
            .contenedor-boton {{ margin-top: 20px; }}
            .btn-guardar {{
                background-color: #00cc66; color: white; border: none; padding: 12px 35px;
                font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: background 0.2s;
            }}
            .btn-guardar:hover {{ background-color: #00b359; }}
        </style>
    </head>
    <body>
        <div class="lienzo">
            {inputs_html}
        </div>
        <div class="contenedor-boton">
            <button class="btn-guardar" onclick="mandarAStreamlit()">💾 Confirmar Modificaciones Realizadas</button>
        </div>

        <script>
            // Mapeo local de cambios
            let datosDocumento = {json_textos};

            function actualizarTexto(id, valor) {{
                datosDocumento[id] = valor;
            }}

            function mandarAStreamlit() {{
                // Envía el diccionario modificado de vuelta a Python
                window.parent.postMessage({{
                    type: "streamlit:setComponentValue",
                    value: datosDocumento
                }}, "*");
            }}
        </script>
    </body>
    </html>
    """
    
    st.subheader("🛠️ Panel de Edición en Vivo")
    st.info("💡 Haz clic en cualquier recuadro amarillo directamente sobre el documento para sobreescribir su contenido.")
    
    # Renderizar el lienzo interactivo. Captura el retorno cuando el usuario da clic en guardar.
    datos_retorno_js = st.components.v1.html(codigo_iframe, height=alto_pantalla + 100, scrolling=False)
    
    # Si el usuario confirmó cambios desde el Canvas, actualizamos la sesión de Python
    if datos_retorno_js:
        for linea in st.session_state['ocr_lineas']:
            l_id = linea['id']
            if l_id in datos_retorno_js:
                linea['text'] = datos_retorno_js[l_id]
        
        # Generar el PDF final vectorizado limpio con los nuevos textos recopilados
        pdf_bytes = generar_pdf_limpio_coordenadas(st.session_state['ocr_lineas'], orig_w, orig_h)
        st.session_state['pdf_listo'] = pdf_bytes
        st.success("¡Estructura gráfica sincronizada con éxito! Tu descarga está lista abajo.")

    # Botón de descarga de Streamlit (se activa al confirmar cambios)
    if st.session_state.get('pdf_listo') is not None:
        st.write("---")
        st.subheader("📥 Paso Final: Obtener Documento Oficial")
        st.download_button(
            label="📥 Descargar PDF Digitalizado Impecable",
            data=st.session_state['pdf_listo'],
            file_name="Oficio_Reconstruido_Lienzo.pdf",
            mime="application/pdf"
        )
else:
    # Limpiar caché si se remueve la imagen
    if 'ocr_lineas' in st.session_state:
        del st.session_state['ocr_lineas']
        del st.session_state['current_img']
        del st.session_state['pdf_listo']
