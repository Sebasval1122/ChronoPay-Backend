"""Firma local de documentos DIAN."""

import hashlib
import hmac


def firmar_documento(documento, certificado):
    """Adjunta una huella HMAC para integridad en entornos de desarrollo.

    Para producción se debe reemplazar por XMLDSig usando el certificado digital autorizado.
    """
    contenido = documento.encode("utf-8") if isinstance(documento, str) else bytes(documento)
    secreto = certificado.encode("utf-8") if isinstance(certificado, str) else bytes(certificado)
    firma = hmac.new(secreto, contenido, hashlib.sha256).hexdigest().encode("ascii")
    return contenido + b"\n<!-- firma-sha256:" + firma + b" -->"