"""Generación del documento XML para la DIAN."""

from xml.etree.ElementTree import Element, SubElement, tostring


def generate_support_document(datos):
    """Construye un XML base con los datos recibidos.

    La estructura fiscal final debe ajustarse al anexo técnico vigente de la DIAN.
    """
    if not isinstance(datos, dict):
        raise TypeError("datos debe ser un diccionario")
    raiz = Element("DocumentoSoporte", {"version": str(datos.get("version", "1.0"))})
    for clave, valor in datos.items():
        if clave == "version":
            continue
        nodo = SubElement(raiz, str(clave))
        nodo.text = "" if valor is None else str(valor)
    return tostring(raiz, encoding="utf-8", xml_declaration=True)