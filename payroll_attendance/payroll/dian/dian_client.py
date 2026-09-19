"""Cliente de transmisión de documentos a la DIAN."""

import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def send_document(documento_firmado):
    """Envía el documento a ``DIAN_API_URL`` cuando está configurado.

    Sin URL configurada devuelve una respuesta local para permitir desarrollo y pruebas.
    """
    url = os.getenv("DIAN_API_URL")
    if not url:
        return {"enviado": False, "modo": "desarrollo", "detalle": "DIAN_API_URL no está configurada"}
    content = documento_firmado.encode("utf-8") if isinstance(documento_firmado, str) else bytes(documento_firmado)
    request = Request(url, data=content, headers={"Content-Type": "application/xml"}, method="POST")
    try:
        with urlopen(request, timeout=30) as response:
            return {"enviado": True, "status_code": response.status, "respuesta": response.read().decode("utf-8")}
    except URLError as exc:
        return {"enviado": False, "error": str(exc.reason)}