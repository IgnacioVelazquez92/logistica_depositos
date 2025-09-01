# Logística App (Inventarios & Vencimientos)

Aplicación **Tkinter + SQLite** para gestionar inventarios, vencimientos y sucursales de supermercado.  
Soporta importar archivos Excel exportados del ERP y hacer consultas rápidas de stock.

---

## 🚀 Funcionalidades actuales

- **Importar Excel** (`resumen` + `vencimientos`):
  - Valida duplicados por (nombre + fecha creación + fecha exportación).
  - Registra inventario, stock y movimientos.
- **Sucursales (Maestros)**:
  - Alta y baja de sucursales.
  - Vinculación con responsables.
- **Vencimientos**:
  - Visualización por sucursal.
  - Semáforo de estado (CRÍTICO, PRÓXIMO, OK).
  - Filtro por texto (código, EAN, descripción).
  - Opción para ocultar productos vencidos.
  - Fecha de **última carga** para cruzar con ventas.
- **Herramientas de desarrollo**:
  - `tools/dev_reset.py` para limpiar la base (todo, inventarios, o por ID).

---

## 📂 Estructura

```
logistica/
├── main.py                          # Punto de entrada: crea la ventana y monta las tabs
├── requirements.txt                 # pandas, openpyxl, tkcalendar (opcional), etc.
├── README.md                        # Cómo correr, dependencias y flujo de uso
├── .env                             # (opcional) ruta DB, entorno, etc.
├── config/
│   ├── settings.py                  # Config general (rutas, umbrales por defecto)
│   └── thresholds.ini               # Días críticos/próximos (7/30), por si querés cambiar sin tocar código
├── db/
│   ├── logistica.db                 # SQLite (creada al vuelo)
│   ├── schema.sql                   # Tablas e índices
│   └── migrations/                  # (opcional) migraciones si luego evoluciona el esquema
├── data/
│   ├── inputs/                      # Excels de entrada
│   └── outputs/                     # Reportes exportados (vencimientos/stock)
├── app/
│   ├── __init__.py
│   ├── ui/                          # Solo interfaz (Tkinter). Nada de lógica de negocio acá.
│   │   ├── __init__.py
│   │   ├── ui_main.py               # Ventana raíz + Notebook (tabs)
│   │   ├── ui_import.py             # Tab: importar (archivo, mapeo, sucursal, responsable)
│   │   ├── ui_expiries.py           # Tab: vencimientos (filtros + tabla + exportar)
│   │   ├── ui_movements.py          # Tab: movimientos manuales (recepción/ajuste)
│   │   ├── ui_stock.py              # Tab: stock actual (consulta + export)
│   │   └── ui_masters.py            # Tab: maestros (sucursales, responsables)
│   ├── services/                    # Reglas de negocio (orquesta DAO + validaciones)
│   │   ├── __init__.py
│   │   ├── import_service.py        # Validar duplicado, mapear columnas, consolidar, grabar todo
│   │   ├── expiry_service.py        # Cálculo de días restantes, semáforos, filtros
│   │   ├── stock_service.py         # Querys de stock, agregaciones, exportaciones
│   │   └── movement_service.py      # Alta de movimientos, afectación de stock, trazabilidad
│   ├── dao/                         # Acceso a datos (CRUD plano, sin reglas de negocio)
│   │   ├── __init__.py
│   │   ├── connection.py            # get_conn(), context manager, pragma, etc.
│   │   ├── inventory_dao.py         # inventories, inventory_rows
│   │   ├── item_dao.py              # items
│   │   ├── location_dao.py          # locations (sucursales/depósitos)
│   │   ├── responsible_dao.py       # responsibles
│   │   ├── stock_dao.py             # stock (upsert por clave compuesta)
│   │   └── movement_dao.py          # movements (insert/listado por inventory_id)
│   ├── models/                      # Dataclasses/TypedDicts para tipado y contratos
│   │   ├── __init__.py
│   │   ├── inventory.py             # Inventory, InventoryRow
│   │   ├── item.py                  # Item
│   │   ├── location.py              # Location
│   │   ├── responsible.py           # Responsible
│   │   ├── stock.py                 # StockRecord
│   │   └── movement.py              # Movement
│   ├── excel/                       # Lectura/escritura Excel (aislado de servicios)
│   │   ├── __init__.py
│   │   ├── reader.py                # Cargar hojas, normalizar cabeceras, validar tipos
│   │   └── writer.py                # Exportar a Excel (vistas filtradas, estilos mínimos)
│   └── utils/
│       ├── __init__.py
│       ├── hashing.py               # hash de archivo y/o contenido para anti-duplicados
│       ├── normalize.py             # normalizar nombres de columnas (espacios, tildes, mayúsculas)
│       ├── dates.py                 # parseo robusto (dd/mm/yyyy, datetimes), días_restantes()
│       └── validators.py            # validaciones (campos obligatorios, tipos, rangos)
├── tests/                           # (opcional recomendado) pruebas unitarias
│   ├── test_import_service.py
│   ├── test_expiry_service.py
│   └── test_stock_service.py
└── logs/                            # (opcional) archivo de logs rotativos
    └── app.log
```

---

## ⚙️ Instalación

1. Crear entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Iniciar la aplicación:
   ```bash
   python main.py
   ```

---

## 🧰 Herramientas de desarrollo

Para limpiar datos y reimportar los mismos Excel durante desarrollo:

```bash
# Borrar SOLO inventarios, stock y movimientos
python -m tools.dev_reset --only-inventories

# Borrar TODO y recrear schema
python -m tools.dev_reset --all

# Borrar inventario específico (ej. id=35)
python -m tools.dev_reset --delete-inventory 35
```

---

## 💡 Próximos pasos

- Agregar **Historial**: listar importaciones y permitir eliminarlas desde la UI.
- Asociar sucursales con `erp_id` para integrarse al ERP.
- Módulo de ventas → cruzar fecha de última carga con ventas y calcular stock proyectado.

---

## 📝 Notas

- DB por defecto: `db/logistica.db`
- Config de umbrales: `config/thresholds.ini`
- Semáforo:
  - **CRÍTICO** ≤ 7 días
  - **PRÓXIMO** ≤ 30 días
  - **OK** > 30 días
  - **SIN_FECHA** si no tiene vencimiento
