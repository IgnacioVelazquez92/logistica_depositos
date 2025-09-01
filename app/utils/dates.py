# app/utils/dates.py
from __future__ import annotations
from datetime import datetime, date
from typing import Optional

# Formatos comunes que pueden venir en tu Excel
FORMATS = [
    "%d/%m/%Y",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M",
    "%Y/%m/%d",
    "%d-%m-%Y",
]


def to_date(val) -> Optional[date]:
    """Convierte val en date. Tolera strings, datetime, pandas.Timestamp."""
    if val is None or val == "":
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()

    s = str(val).strip()
    # Intentos manuales
    for fmt in FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass

    # Intento con pandas si está disponible (dayfirst=True)
    try:
        from pandas import to_datetime as _pdt
        d = _pdt(s, dayfirst=True, errors="coerce")
        if d is not None and str(d) != "NaT":
            return d.date()
    except Exception:
        pass

    return None


def days_left(d: Optional[date]) -> Optional[int]:
    """Devuelve días restantes desde hoy; None si no hay fecha."""
    if d is None:
        return None
    today = date.today()
    return (d - today).days
