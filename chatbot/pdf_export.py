import io

def escape_pdf_text(text):
    """Escapa caracteres especiales para el formato PDF en texto de 8 bits."""
    # Sanitizar a latin-1 para compatibilidad con fuentes Type1 WinAnsi
    text = text.encode('latin-1', 'replace').decode('latin-1')
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def wrap_text(text, max_len=72):
    """Divide el texto en líneas respetando palabras y saltos de línea."""
    result = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            result.append('')
            continue
        words = raw_line.split(' ')
        curr = ''
        for w in words:
            if not curr:
                curr = w
            elif len(curr) + 1 + len(w) <= max_len:
                curr += ' ' + w
            else:
                result.append(curr)
                curr = w
        if curr:
            result.append(curr)
    return result if result else ['']

def generate_chat_pdf(house, messages):
    """
    Genera un archivo PDF válido estándar en memoria con el historial de conversación
    asociado a la propiedad, sin requerir librerías externas.
    """
    lines = []
    lines.append("=" * 72)
    lines.append(f"HISTORIAL DE CONVERSACION - {house.name}")
    lines.append("=" * 72)
    lines.append(f"Ubicacion : {house.location}")
    lines.append(f"Precio    : {house.precio_formateado()}")
    lines.append("-" * 72)
    lines.append("")

    if not messages:
        lines.append("No hay mensajes registrados en el historial para esta propiedad.")
    else:
        for idx, msg in enumerate(messages, start=1):
            created_str = msg.created_at.strftime('%d/%m/%Y %H:%M:%S')
            lines.append(f"[{idx}] FECHA: {created_str}")
            lines.append("USUARIO:")
            for q_line in wrap_text(msg.question, 70):
                lines.append(f"  {q_line}")
            lines.append("ASISTENTE IA:")
            for r_line in wrap_text(msg.response, 70):
                lines.append(f"  {r_line}")
            lines.append("-" * 72)
            lines.append("")

    lines_per_page = 42
    pages_lines = [lines[i:i + lines_per_page] for i in range(0, max(len(lines), 1), lines_per_page)]
    num_pages = len(pages_lines)

    body = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = []

    def add_obj(b_data):
        offsets.append(sum(len(x) for x in body))
        body.append(b_data)

    font_obj_id = 3 + 2 * num_pages

    # 1. Objeto Catalog
    add_obj(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # 2. Objeto Pages
    kids = " ".join([f"{3 + 2 * i} 0 R" for i in range(num_pages)])
    pages_obj = f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {num_pages} >>\nendobj\n".encode("ascii")
    add_obj(pages_obj)

    # 3. Páginas y Content Streams
    for i, p_lines in enumerate(pages_lines):
        page_obj_id = 3 + 2 * i
        content_obj_id = 4 + 2 * i

        p_obj = (
            f"{page_obj_id} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {content_obj_id} 0 R /Resources << /Font << /F1 {font_obj_id} 0 R >> >> >>\n"
            f"endobj\n"
        ).encode("ascii")
        add_obj(p_obj)

        stream = "BT\n/F1 9 Tf\n45 745 Td\n15 TL\n"
        for l in p_lines:
            escaped = escape_pdf_text(l)
            stream += f"({escaped}) '\n"
        stream += f"(--- Pagina {i+1} de {num_pages} ---) '\n"
        stream += "ET\n"
        stream_bytes = stream.encode("latin-1", "replace")

        c_obj = (
            f"{content_obj_id} 0 obj\n"
            f"<< /Length {len(stream_bytes)} >>\n"
            f"stream\n"
        ).encode("ascii") + stream_bytes + b"\nendstream\nendobj\n"
        add_obj(c_obj)

    # 4. Fuente Courier con WinAnsiEncoding para caracteres en español
    font_obj = f"{font_obj_id} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>\nendobj\n".encode("ascii")
    add_obj(font_obj)

    # 5. Xref y Trailer
    xref_offset = sum(len(x) for x in body)
    body.append(f"xref\n0 {len(offsets) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for off in offsets:
        body.append(f"{off:010d} 00000 n \n".encode("ascii"))
    body.append(f"trailer\n<< /Size {len(offsets) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))

    return b"".join(body)
