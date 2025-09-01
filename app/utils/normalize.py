# app/utils/normalize.py
import re
import unicodedata

# Alias para mapear cabeceras de Excel a nombres canónicos
ALIASES = {
    "ean": ["ean", "codigo de barras", "código de barras"],
    "codigo articulo": ["codigo articulo", "codigo", "cod_articulo", "cod articulo", "código", "código articulo"],
    "descripcion": ["descripcion", "descripción"],
    "unidades por bulto": ["unidades por bulto", "unid por bulto", "upb"],
    "bultos": ["bultos"],
    "cantidad": ["cantidad", "kilos"],
    "fecha de vencimiento": ["fecha de vencimiento", "vencimiento"],
    "fecha de ingreso": ["fecha de ingreso", "ingreso"],
    "nombre": ["nombre"],
    "fecha de creacion": ["fecha de creacion", "fecha creación"],
    "fecha de exportacion": ["fecha de exportacion", "fecha exportación"],
    "total filas": ["total filas", "total_filas"],
    "tipo": ["tipo"],
    "observacion": ["observacion", "observación"],
    "inventario_id": ["inventario_id", "id inventario"],
    # ventas
    "sucursal": ["sucursal"],
    "fecha": ["fecha"],
    # si alguien trae "presentacion", "costo", "venta", los ignoramos; no son obligatorios
}

def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def clean_header(s: str) -> str:
    """Limpia y normaliza una cabecera (lower, quita espacios extra y acentos)."""
    s = s.strip()
    s = _strip_accents(s)            # <<< quita tildes
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s

def canonicalize_columns(cols):
    """
    Dada una lista de cabeceras de Excel,
    devuelve la lista en versión canónica usando ALIASES.
    """
    out = []
    for c in cols:
        cc = clean_header(c)
        mapped = None
        for key, variants in ALIASES.items():
            if cc in [clean_header(v) for v in variants]:
                mapped = key
                break
        out.append(mapped if mapped else cc)
    return out
