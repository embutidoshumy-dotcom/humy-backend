from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
importar sistema operativo
importar registro
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
importar uuid
from datetime import datetime, timedelta
importar urllib.parse
secretos de importación
importar hashlib


ROOT_DIR = Ruta(__archivo__).padre
cargar_dotenv(ROOT_DIR / '.env')

# Conexión a MongoDB
mongo_url = os.environ['MONGO_URL']
cliente = AsyncIOMotorClient(mongo_url)
db = cliente[os.environ['DB_NAME']]

# Crea la aplicación principal sin prefijo
aplicación = FastAPI()

# Crea un enrutador con el prefijo /api
api_router = APIRouter(prefix="/api")

# Seguridad
seguridad = HTTPBasic()

# Credenciales de administrador
# Credenciales de administrador: cargar desde variables de entorno
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'EmbutidosHumy')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Venezuelateamo101993*')

# Número de WhatsApp para pedidos
NÚMERO DE WHATSAPP = "8299185606"

# Cuentas bancarias
CUENTAS BANCARIAS = {
    "popular": {
        "banco": "Banco Popular",
        "titular": "Mileidy Guevara",
        "cuenta": "823515960",
        "type": "Corriente"
    },
    "banreservas": {
        "banco": "Banreservas",
        "titular": "Mileidy Guevara",
        "cuenta": "9605147823",
        "tipo": "Ahorro"
    }
}

# Datos combinados predeterminados (se migrarán a la base de datos)
COMBOS_PREDETERMINADOS = [
    {
        "id": "combo1",
        "nombre": "Super Combo 1",
        "description": "2 LB Chuleta Ahumada, 1 LB Costilla Ahumada, 1 LB Jamón Cocido, 1 LB Longaniza Fina",
        "precio": 660,
        "image_url": "https://customer-assets.emergentagent.com/job_d0ebc224-4e42-4a7d-b183-a128866ac01c/artifacts/wr5w0v5h_IMG-20260227-WA0021.jpg",
        "activo": Verdadero
    },
    {
        "id": "combo2",
        "nombre": "Super Combo 2",
        "description": "2 LB Chuleta Ahumada, 1 LB Costilla Ahumada, 1 LB JamÃ³n Cocido, 1 LB Queso Cheddar, 1 LB Salami Mallita",
        "precio": 900,
        "image_url": "https://customer-assets.emergentagent.com/job_d0ebc224-4e42-4a7d-b183-a128866ac01c/artifacts/9zucrp2o_IMG-20260227-WA0020.jpg",
        "activo": Verdadero
    },
    {
        "id": "combo3",
        "nombre": "Super Combo 3",
        "description": "2 LB Chuleta Ahumada, 1 LB Costilla Ahumada, 1 LB JamÃ³n Picnic, 1 LB Queso Cheddar, 1 LB Salami Induveca, 1 LB Queso de FreÃr, 1 LB Longaniza Fina",
        "precio": 1290,
        "image_url": "https://customer-assets.emergentagent.com/job_d0ebc224-4e42-4a7d-b183-a128866ac01c/artifacts/xwfllsol_IMG-20260227-WA0023.jpg",
        "activo": Verdadero
    },
    {
        "id": "combo4",
        "nombre": "Super Combo 4",
        "description": "2 LB Chuleta Ahumada, 1 LB Costilla Ahumada, 1 LB Jamón Picnic, 1 LB Queso Cheddar, 1 LB Salami Induveca, 1 LB Queso de Freír, 1 Cartón de Huevo",
        "precio": 1290,
        "image_url": "https://customer-assets.emergentagent.com/job_d0ebc224-4e42-4a7d-b183-a128866ac01c/artifacts/yljz2eqn_IMG-20260227-WA0022.jpg",
        "activo": Verdadero
    }
]

# Definir modelos
clase Combo(BaseModel):
    id: str
    nombre: str
    descripción: str
    precio: int
    URL de la imagen: str
    activo: bool = True

clase ComboCreate(BaseModel):
    nombre: str
    descripción: str
    precio: int
    URL de la imagen: str

clase ComboUpdate(BaseModel):
    nombre: Optional[str] = Ninguno
    Descripción: Opcional[str] = Ninguno
    precio: Opcional[int] = Ninguno
    image_url: Optional[str] = None
    activo: Opcional[bool] = Ninguno

clase BankAccount(BaseModel):
    banco: str
    titular: str
    cuenta: str
    tipo: str

clase OrderItem(BaseModel):
    combo_id: str
    cantidad: int

clase OrderCreate(BaseModel):
    elementos: Lista[OrderItem]
    nombre_cliente: str
    teléfono_cliente: str
    ubicación: str
    location_link: Optional[str] = None
    método_de_pago: str
    imagen_recibo: Opcional[str] = Ninguno
    delivery_method: Optional[str] = "delivery" # retiro o delivery

clase Order(BaseModel):
    id: str = Campo(default_factory=lambda: str(uuid.uuid4()))
    elementos: Lista[OrderItem]
    nombre_cliente: str
    teléfono_cliente: str
    ubicación: str
    location_link: Optional[str] = None
    método_de_pago: Optional[str] = "efectivo"
    método_de_entrega: Opcional[str] = "entrega"
    receipt_url: Opcional[str] = Ninguno
    total: int
    marca de tiempo: datetime = Campo(default_factory=datetime.utcnow)
    url_de_whatsapp: str
    status: str = "pendiente" # pendiente, entregado, cancelado

clase OrderStatusUpdate(BaseModel):
    estado: str

clase AdminLogin(BaseModel):
    nombre de usuario: str
    contraseña: str

clase AdminLoginResponse(BaseModel):
    éxito: booleano
    mensaje: str
    token: Optional[str] = Ninguno

clase ReceiptUpload(BaseModel):
    imagen: str

clase ReceiptResponse(BaseModel):
    receipt_id: str
    receipt_url: str

clase SalesStats(BaseModel):
    pedidos_totales: int
    ingresos_totales: int
    pedidos_hoy: int
    ingresos_hoy: int
    pedidos_semana: int
    ingresos_semana: int
    pedidos_mes: int
    ingresos_mes: int

clase PromoCreate(BaseModel):
    imagen: str # Imagen Base64
    título: Opcional[str] = "Oferta Especial"
    Descripción: Opcional[str] = Ninguno

clase Promo(BaseModel):
    id: str
    URL de la imagen: str
    título: str
    Descripción: Opcional[str] = Ninguno
    activo: bool = True
    creado_en: fecha y hora

# Modelos de categoría y producto
clase CategoryCreate(BaseModel):
    nombre: str
    orden: Optional[int] = 0

Clase Categoría(ModeloBase):
    id: str
    nombre: str
    orden: int = 0
    activo: bool = True

clase ProductCreate(BaseModel):
    nombre: str
    descripción: str
    precio: int
    imagen: str # Imagen Base64
    category_id: str

clase ProductUpdate(BaseModel):
    nombre: Optional[str] = Ninguno
    Descripción: Opcional[str] = Ninguno
    precio: Opcional[int] = Ninguno
    image_url: Optional[str] = None
    activo: Opcional[bool] = Ninguno

clase Producto(ModeloBase):
    id: str
    nombre: str
    descripción: str
    precio: int
    URL de la imagen: str
    category_id: str
    activo: bool = True

clase StoreSettings(BaseModel):
    productos_habilitados: bool = Falso

# Función auxiliar para verificar las credenciales de administrador
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    Si no (es_correcto_nombre_de_usuario y es_correcto_contraseña):
        generar HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            Detail="Credenciales incorrectas",
            encabezados={"WWW-Authenticate": "Basic"},
        )
    devolver credenciales.nombredeusuario

# Inicializar combinaciones en la base de datos
async def init_combos():
    count = await db.combos.count_documents({})
    Si count == 0:
        esperar db.combos.insert_many(DEFAULT_COMBOS)
        logging.info("Combinaciones inicializadas en la base de datos")

@app.on_event("startup")
async def startup_event():
    esperar a inicializar_combos()

# ============== RUTAS PÚBLICAS ==============

@api_router.get("/")
async def root():
    return {"mensaje": "Embutidos Humy API"}

@api_router.get("/combos", response_model=List[Combo])
async def get_combos():
    combos = await db.combos.find({"active": True}).to_list(100)
    Si no hay combinaciones:
        # Si la base de datos está vacía, se vuelve al valor predeterminado.
        devolver COMBOS_PREDETERMINADOS
    devolver [Combo(**combo) para combo en combos]

@api_router.get("/combos/{combo_id}", response_model=Combo)
async def get_combo(combo_id: str):
    combo = await db.combos.find_one({"id": combo_id})
    Si no es una combinación:
        Generar HTTPException(status_code=404, detail="Combo no encontrado")
    devolver Combo(**combo)

@api_router.get("/bank-accounts")
async def get_bank_accounts():
    devolver CUENTAS BANCARIAS

@api_router.get("/store-settings")
async def get_store_settings():
    "Obtén la configuración de la tienda, incluyendo el estado de los productos habilitados y el estado de apertura de la tienda".
    configuración = await db.settings.find_one({"type": "store"})
    Si no hay configuración:
        return {"products_enabled": False, "store_open": True, "closed_message": ""}
    devolver {
        "products_enabled": settings.get("products_enabled", False),
        "store_open": settings.get("store_open", True),
        "closed_message": settings.get("closed_message", "En este momento no contamos con inventario. Estamos anotando pedidos para entregar el día lunes. Recuerda que buscamos mercancía el mismo día lunes y retornamos a las 3:00 PM.")
    }

@api_router.get("/categories")
async def get_categories():
    "Obtener todas las categorías activas"
    configuración = await db.settings.find_one({"type": "store"})
    Si no hay configuración o no hay configuración.get("products_enabled", False):
        devolver []
    categorías = await db.categories.find({"active": True}).sort("order", 1).to_list(100)
    para gatos en categorías:
        si "_id" está en el gato:
            cat["_id"] = str(cat["_id"])
    categorías de retorno

@api_router.get("/products")
async def get_products(category_id: Optional[str] = None):
    "Obtén todos los productos activos, opcionalmente filtrados por categoría"
    configuración = await db.settings.find_one({"type": "store"})
    Si no hay configuración o no hay configuración.get("products_enabled", False):
        devolver []
    
    consulta = {"activa": Verdadero}
    si category_id:
        consulta["category_id"] = category_id
    
    productos = await db.products.find(query).to_list(1000)
    para productos en productos:
        si "_id" está en prod:
            prod["_id"] = str(prod["_id"])
    productos de devolución

@api_router.get("/promo")
async def get_active_promo():
    """Aprovecha la promoción actualmente activa"""
    promo = await db.promos.find_one({"active": True})
    Si no es una promoción:
        devolver Ninguno
    # Convertir ObjectId a cadena
    si "_id" está en promo:
        promo["_id"] = str(promo["_id"])
    promoción de regreso

@api_router.post("/upload-receipt", response_model=ReceiptResponse)
async def upload_receipt(receipt: ReceiptUpload):
    receipt_id = str(uuid.uuid4())
    esperar db.receipts.insert_one({
        "id": receipt_id,
        "imagen": recibo.imagen,
        "marca de tiempo": datetime.utcnow()
    })
    base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://fcm-order-sync.preview.emergentagent.com')
    receipt_url = f"{base_url}/api/receipts/{receipt_id}"
    devolver ReceiptResponse(receipt_id=receipt_id, receipt_url=receipt_url)

@api_router.get("/receipts/{receipt_id}")
async def get_receipt(receipt_id: str):
    from fastapi.responses import HTMLResponse
    recibo = await db.receipts.find_one({"id": receipt_id})
    Si no hay recibo:
        Generar HTTPException(status_code=404, detail="Recibo no encontrado")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comprobante de Pago - Embutidos Humy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            cuerpo {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; text-align: center; }}
            h1 {{ color: #C41E24; font-size: 24px; }}
            img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }}
        </style>
    </head>
    <cuerpo>
        <h1>Comprobante de Pago</h1>
        <img src="{recibo['image']}" alt="Comprobante de pago">
    </body>
    </html>
    """
    devolver HTMLResponse(content=html_content)

@api_router.post("/orders", response_model=Order)
async def crear_pedido(entrada_pedido: OrderCreate):
    # Obtener combinaciones de la base de datos
    combos = await db.combos.find({"active": True}).to_list(100)
    Si no hay combinaciones:
        combos = COMBOS_PREDETERMINADOS
    
    # Obtener productos de la base de datos
    productos = await db.products.find({"active": True}).to_list(1000)
    
    total = 0
    detalles_del_pedido = []
    
    para cada elemento en order_input.items:
        # Primero comprueba si es una combinación
        combo = next((c for c in combos if c["id"] == item.combo_id), None)
        Si combo y item.quantity > 0:
            subtotal = combo["precio"] * item.cantidad
            total += subtotal
            order_details.append(f"{item.quantity}x {combo['name']} - RD${subtotal:,}")
        demás:
            # Comprueba si es un producto
            producto = siguiente((p para p en productos si p["id"] == item.combo_id), Ninguno)
            Si producto y cantidad de artículo > 0:
                subtotal = producto["precio"] * artículo.cantidad
                total += subtotal
                order_details.append(f"{item.quantity}x {product['name']} - RD${subtotal:,}")
    
    # Gestionar la carga del recibo
    receipt_url = Ninguno
    si order_input.receipt_image:
        receipt_id = str(uuid.uuid4())
        esperar db.receipts.insert_one({
            "id": receipt_id,
            "imagen": order_input.receipt_image,
            "marca de tiempo": datetime.utcnow()
        })
        base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://fcm-order-sync.preview.emergentagent.com')
        receipt_url = f"{base_url}/api/receipts/{receipt_id}"
    
    # Texto del método de entrega
    delivery_text = "ðŸ ª Retiro en Local" if order_input.delivery_method == "retiro" else "ðŸš´ Delivery"
    
    # Crear mensaje de WhatsApp
    líneas_de_mensaje = [
        "*NUEVO PEDIDO - EMBUTIDOS HUMY*",
        "",
        f"*ENTREGA:* {texto_de_entrega}",
        "",
        "*CLIENTE:*",
        f"Nombre: {order_input.customer_name}",
        f"Teléfono: {order_input.customer_phone}",
    ]
    
    # Solo agregar ubicación para pedidos de entrega
    Si order_input.delivery_method == "delivery":
        message_lines.append(f"Ubicación: {order_input.location}")
        si order_input.location_link:
            líneas_de_mensaje.append(f"")
            message_lines.append(f"ðŸ“ *Ver ubicación en mapa:*")
            message_lines.append(f"{order_input.location_link}")
    
    message_lines.extend(["", "*PEDIDO:*"])
    líneas_mensaje.extender(detalles_pedido)
    
    texto_pago = "Efectivo" si order_input.payment_method == "efectivo" else "Transferencia"
    líneas_de_mensaje.extender([
        "",
        f"*TOTAL: RD${total:,}*",
        f"*Método de pago:* {paid_text}",
    ])
    
    si receipt_url:
        líneas_de_mensaje.extender([
            "",
            "ðŸ“Ž *Comprobante de pago:*",
            URL del recibo
        ])
    
    mensaje = "\n".join(líneas_de_mensaje)
    mensaje_codificado = urllib.parse.quote(mensaje)
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"
    
    orden = Orden(
        elementos=ordenar_input.elementos,
        nombre_cliente=orden_entrada.nombre_cliente,
        teléfono_cliente=orden_entrada.teléfono_cliente,
        ubicación=orden_entrada.ubicación,
        location_link=order_input.location_link,
        método_de_pago=orden_entrada.método_de_pago,
        método_de_entrega=orden_entrada.método_de_entrega,
        recibo_url=recibo_url,
        total=total,
        url_de_whatsapp=url_de_whatsapp,
        status="pendiente"
    )
    
    # Convertir a diccionario e insertar en la base de datos
    order_dict = order.dict()
    esperar a que db.orders.insert_one(order_dict.copy())
    orden de devolución

@api_router.get("/orders", response_model=List[Order])
async def get_orders():
    pedidos = await db.orders.find().sort("timestamp", -1).to_list(1000)
    # Convertir ObjectId a cadena para evitar problemas de serialización
    resultado = []
    para ordenar en pedidos:
        si "_id" está en orden:
            del orden["_id"]
        resultado.append(Orden(**orden))
    devolver resultado

# ============== RUTAS DE ADMINISTRACIÓN ==============

@api_router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(login: AdminLogin):
    Si login.username == ADMIN_USERNAME y login.password == ADMIN_PASSWORD:
        # Generar un token simple
        token = hashlib.sha256(f"{login.username}{datetime.utcnow().isoformat()}".encode()).hexdigest()
        return AdminLoginResponse(success=True, message="Login exitoso", token=token)
    generar HTTPException(status_code=401, detalle="Credenciales incorrectas")

@api_router.get("/admin/orders")
async def admin_get_orders(admin: str = Depends(verify_admin)):
    pedidos = await db.orders.find().sort("timestamp", -1).to_list(1000)
    # Convertir ObjectId a cadena
    para ordenar en pedidos:
        si "_id" está en orden:
            orden["_id"] = str(orden["_id"])
    devoluciones

@api_router.put("/admin/orders/{order_id}/status")
async def admin_update_order_status(order_id: str, status_update: OrderStatusUpdate, admin: str = Depends(verify_admin)):
    resultado = esperar db.orders.update_one(
        {"id": order_id},
        {"$set": {"status": status_update.status}}
    )
    Si result.modified_count == 0:
        generar HTTPException(status_code=404, detalle="Pedido no encontrado")
    return {"message": "Estado actualizado", "status": status_update.status}

@api_router.get("/admin/combos")
async def admin_get_combos(admin: str = Depends(verify_admin)):
    combos = await db.combos.find().to_list(100)
    # Convertir ObjectId a cadena
    para combo en combos:
        si "_id" está en combo:
            combo["_id"] = str(combo["_id"])
    combinaciones de retorno

@api_router.post("/admin/combos")
async def admin_create_combo(combo: ComboCreate, admin: str = Depends(verify_admin)):
    combo_id = f"combo_{str(uuid.uuid4())[:8]}"
    nuevo_combo = {
        "id": combo_id,
        "nombre": combo.nombre,
        "descripción": combo.descripción,
        "precio": combo.precio,
        "image_url": combo.image_url,
        "activo": Verdadero
    }
    esperar db.combos.insertar_uno(nuevo_combo)
    devolver nuevo_combo

@api_router.put("/admin/combos/{combo_id}")
async def admin_update_combo(combo_id: str, combo_update: ComboUpdate, admin: str = Depends(verify_admin)):
    actualizar_datos = {k: v para k, v en combo_update.dict().items() si v no es None}
    si no se actualizan los datos:
        levantar HTTPException(status_code=400, detalle="No hay datos para actualizar")
    
    resultado = esperar db.combos.update_one(
        {"id": combo_id},
        {"$set": update_data}
    )
    Si result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Combo no encontrado")
    
    updated_combo = await db.combos.find_one({"id": combo_id})
    devolver el combo actualizado

@api_router.delete("/admin/combos/{combo_id}")
async def admin_delete_combo(combo_id: str, admin: str = Depends(verify_admin)):
    resultado = await db.combos.delete_one({"id": combo_id})
    Si result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Combo no encontrado")
    return {"mensaje": "Combo eliminado"}

@api_router.delete("/admin/orders/{order_id}")
async def admin_delete_order(order_id: str, admin: str = Depends(verify_admin)):
    """Eliminar un pedido (solo se pueden eliminar los pedidos cancelados)"""
    orden = esperar db.orders.find_one({"id": order_id})
    Si no se realiza el pedido:
        generar HTTPException(status_code=404, detalle="Pedido no encontrado")
    
    resultado = esperar db.orders.delete_one({"id": order_id})
    Si result.deleted_count == 0:
        elevar HTTPException(status_code=404, Detail="No se pudo eliminar el pedido")
    return {"mensaje": "Pedido eliminado"}

@api_router.get("/admin/stats", response_model=SalesStats)
async def admin_get_stats(admin: str = Depends(verify_admin)):
    ahora = datetime.utcnow()
    inicio_hoy = ahora.reemplazar(hora=0, minuto=0, segundo=0, microsegundo=0)
    inicio_semana = inicio_hoy - diferencia_tiempo(días=ahora.día_semana())
    inicio_mes = inicio_hoy.replace(día=1)
    
    # Solo se contabilizan los pedidos ENTREGADOS como ventas efectivas
    todos_los_pedidos = await db.orders.find({"estado": "entregado"}).to_list(10000)
    pedidos_totales = longitud(todos_los_pedidos)
    ingresos_totales = suma(o.get("total", 0) para o en todos_los_pedidos)
    
    # Hoy - solo entrega a domicilio
    pedidos_hoy = [o para o en todos_pedidos si o.get("timestamp", datetime.min) >= inicio_hoy]
    pedidos_hoy = len(pedidos_hoy)
    ingresos_hoy = suma(o.get("total", 0) para o en pedidos_hoy)
    
    # Esta semana - solo entregas
    pedidos_semana = [o para o en todos_pedidos si o.get("timestamp", datetime.min) >= inicio_semana]
    pedidos_semana = len(pedidos_semana)
    ingresos_semana = suma(o.get("total", 0) para o en pedidos_semanales)
    
    # Este mes - solo entrega a domicilio
    pedidos_del_mes = [o para o en todos_los_pedidos si o.get("timestamp", datetime.min) >= inicio_del_mes]
    pedidos_mes = len(pedidos_mes)
    ingresos_mes = suma(o.get("total", 0) para o en pedidos_mes)
    
    devolver Estadísticas de ventas(
        pedidos_totales=pedidos_totales,
        ingresos_totales=ingresos_totales,
        pedidos_hoy=pedidos_hoy,
        ingresos_hoy=ingresos_hoy,
        orders_week=orders_week,
        ingresos_semana=ingresos_semana,
        pedidos_mes=pedidos_mes,
        ingresos_mes=ingresos_mes
    )

@api_router.get("/admin/sales-history")
async def admin_get_sales_history(admin: str = Depends(verify_admin)):
    "Obtenga un historial de ventas detallado agrupado por día, mes y año, solo pedidos entregados"
    # Recibe todos los pedidos entregados
    todos_los_pedidos = await db.orders.find({"estado": "entregado"}).to_list(10000)
    
    # Obtén combinaciones de nombres
    combos = await db.combos.find().to_list(100)
    combo_names = {c["id"]: c["name"] para c en combos}
    
    # Agrupar por día
    ventas_diarias = {}
    ventas_mensuales = {}
    ventas_anuales = {}
    
    para cada pedido en todos los pedidos:
        marca de tiempo = orden.get("marca de tiempo", datetime.utcnow())
        Si isinstance(timestamp, str):
            marca de tiempo = datetime.fromisoformat(marca de tiempo.replace('Z', '+00:00'))
        
        day_key = timestamp.strftime("%Y-%m-%d")
        month_key = timestamp.strftime("%Y-%m")
        year_key = timestamp.strftime("%Y")
        
        total = order.get("total", 0)
        artículos = pedido.get("artículos", [])
        
        # Procesar elementos para desglose combinado
        desglose_combinado = {}
        para cada elemento en elementos:
            combo_id = item.get("combo_id")
            cantidad = item.get("cantidad", 0)
            combo_name = combo_names.get(combo_id, combo_id)
            Si combo_name no está en combo_breakdown:
                combo_breakdown[combo_name] = 0
            combo_breakdown[combo_name] += cantidad
        
        # A diario
        Si day_key no está en daily_sales:
            ventas_diarias[clave_día] = {"fecha": clave_día, "pedidos": 0, "ingresos": 0, "combos": {}}
        ventas_diarias[clave_día]["pedidos"] += 1
        ventas_diarias[clave_día]["ingresos"] += total
        para combo, qty en combo_breakdown.items():
            Si combo no está en daily_sales[day_key]["combos"]:
                ventas_diarias[clave_día]["combos"][combo] = 0
            ventas_diarias[clave_día]["combinaciones"][combinación] += cantidad
        
        # Mensual
        Si month_key no está en monthly_sales:
            ventas_mensuales[clave_mes] = {"mes": clave_mes, "pedidos": 0, "ingresos": 0, "combos": {}}
        ventas_mensuales[clave_mes]["pedidos"] += 1
        ventas_mensuales[clave_mes]["ingresos"] += total
        para combo, qty en combo_breakdown.items():
            Si combo no está en monthly_sales[month_key]["combos"]:
                ventas_mensuales[clave_mes]["combos"][combo] = 0
            ventas_mensuales[clave_mes]["combinaciones"][combinación] += cantidad
        
        # Anual
        Si year_key no está en yearly_sales:
            ventas_anuales[clave_año] = {"año": clave_año, "pedidos": 0, "ingresos": 0, "combos": {}}
        ventas_anuales[clave_año]["pedidos"] += 1
        ventas_anuales[clave_año]["ingresos"] += total
        para combo, qty en combo_breakdown.items():
            Si combo no está en yearly_sales[year_key]["combos"]:
                ventas_anuales[clave_año]["combinaciones"][combinación] = 0
            ventas_anuales[clave_año]["combinaciones"][combinación] += cantidad
    
    # Ordenar por fecha descendente
    lista_diaria = ordenado(ventas_diarias.valores(), clave=lambda x: x["fecha"], inverso=verdadero)
    lista_mensual = ordenado(ventas_mensuales.valores(), clave=lambda x: x["mes"], inverso=verdadero)
    lista_anual = ordenado(ventas_anuales.valores(), clave=lambda x: x["año"], inverso=Verdadero)
    
    devolver {
        "diario": lista_diaria[:30], # Últimos 30 días
        "mensual": monthly_list[:12], # Últimos 12 meses
        "anual": lista_anual # Todos los años
    }

@api_router.post("/admin/upload-image")
async def admin_upload_image(image_data: dict, admin: str = Depends(verify_admin)):
    """Sube una imagen y devuelve una URL"""
    image_id = str(uuid.uuid4())
    esperar db.images.insert_one({
        "id": image_id,
        "imagen": image_data.get("imagen"),
        "marca de tiempo": datetime.utcnow()
    })
    base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://fcm-order-sync.preview.emergentagent.com')
    image_url = f"{base_url}/api/images/{image_id}"
    devolver {"image_url": image_url}

@api_router.get("/images/{image_id}")
async def get_image(image_id: str):
    from fastapi.responses import HTMLResponse
    imagen = await db.images.find_one({"id": image_id})
    si no hay imagen:
        Generar HTTPException(status_code=404, detail="Imagen no encontrada")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Imagen - Embutidos Humy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            cuerpo {{ margen: 0; relleno: 0; mostrar: flex; justificar contenido: centro; alinear elementos: centro; altura mínima: 100vh; fondo: #f5f5f5; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <cuerpo>
        <img src="{image['image']}" alt="Imagen">
    </body>
    </html>
    """
    devolver HTMLResponse(content=html_content)

# ============== RUTAS DE ADMINISTRACIÓN DE PROMOCIÓN ==============

@api_router.get("/admin/promo")
async def admin_get_promo(admin: str = Depends(verify_admin)):
    """Obtén la promoción actual (activa o no)"""
    promo = await db.promos.find_one({}, sort=[("created_at", -1)])
    si promoción:
        si "_id" está en promo:
            promo["_id"] = str(promo["_id"])
    promoción de regreso

@api_router.post("/admin/promo")
async def admin_create_promo(promo_data: PromoCreate, admin: str = Depends(verify_admin)):
    "Crear o actualizar promoción"
    # Desactivar todas las promociones existentes
    await db.promos.update_many({}, {"$set": {"active": False}})
    
    # Subir imagen
    image_id = str(uuid.uuid4())
    esperar db.images.insert_one({
        "id": image_id,
        "imagen": promo_data.image,
        "marca de tiempo": datetime.utcnow()
    })
    base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://fcm-order-sync.preview.emergentagent.com')
    image_url = f"{base_url}/api/images/{image_id}"
    
    # Crear nueva promoción
    promo_id = str(uuid.uuid4())
    nueva_promoción = {
        "id": promo_id,
        "image_url": image_url,
        "image_base64": promo_data.image, # Almacenar base64 para visualización directa
        "title": promo_data.title o "Oferta Especial",
        "descripción": promo_data.description,
        "activo": Verdadero,
        "created_at": datetime.utcnow()
    }
    esperar db.promos.insert_one(new_promo)
    
    return {"message": "Promoción creada", "promo_id": promo_id}

@api_router.put("/admin/promo/{promo_id}/toggle")
async def admin_toggle_promo(promo_id: str, admin: str = Depends(verify_admin)):
    "Alternar estado de la promoción activa"
    promo = await db.promos.find_one({"id": promo_id})
    Si no es una promoción:
        levantar HTTPException(status_code=404, detalle="Promoción no encontrada")
    
    nuevo_estado = no promo.get("activo", Falso)
    await db.promos.update_one({"id": promo_id}, {"$set": {"active": new_status}})
    
    return {"message": "Estado actualizado", "active": new_status}

@api_router.delete("/admin/promo/{promo_id}")
async def admin_delete_promo(promo_id: str, admin: str = Depends(verify_admin)):
    "Eliminar una promoción"
    resultado = await db.promos.delete_one({"id": promo_id})
    Si result.deleted_count == 0:
        levantar HTTPException(status_code=404, detalle="Promoción no encontrada")
    return {"message": "Promoción eliminada"}

# ============== RUTAS DE ADMINISTRACIÓN DE PRODUCTOS Y CATEGORÍAS ==============

@api_router.get("/admin/store-settings")
async def admin_get_store_settings(admin: str = Depends(verify_admin)):
    "Obtener la configuración de la tienda"
    configuración = await db.settings.find_one({"type": "store"})
    Si no hay configuración:
        return {"products_enabled": False, "store_open": True, "closed_message": "En este momento no contamos con inventario. Estamos anotando pedidos para entregar el día lunes. Recuerda que buscamos mercancía el mismo día lunes y retornamos a las 3:00 PM."}
    devolver {
        "products_enabled": settings.get("products_enabled", False),
        "store_open": settings.get("store_open", True),
        "closed_message": settings.get("closed_message", "En este momento no contamos con inventario. Estamos anotando pedidos para entregar el día lunes. Recuerda que buscamos mercancía el mismo día lunes y retornamos a las 3:00 PM.")
    }

@api_router.put("/admin/store-settings")
async def admin_update_store_settings(settings: dict, admin: str = Depends(verify_admin)):
    "Actualizar la configuración de la tienda"
    actualizar_datos = {}
    Si "products_enabled" está en la configuración:
        update_data["products_enabled"] = settings["products_enabled"]
    Si "store_open" está en la configuración:
        actualizar_datos["store_open"] = configuración["store_open"]
    Si "closed_message" está en la configuración:
        actualizar_datos["mensaje_cerrado"] = configuración["mensaje_cerrado"]
    
    esperar db.settings.update_one(
        {"tipo": "tienda"},
        {"$set": update_data},
        upsert=Verdadero
    )
    
    # Obtener ajustes actualizados
    actualizado = await db.settings.find_one({"type": "store"})
    devolver {
        "message": "Configuración actualizada",
        "products_enabled": updated.get("products_enabled", False),
        "store_open": actualizado.get("store_open", True),
        "closed_message": updated.get("closed_message", "")
    }

@api_router.get("/admin/categories")
async def admin_get_categories(admin: str = Depends(verify_admin)):
    "Obtener todas las categorías"
    categorías = await db.categories.find().sort("order", 1).to_list(100)
    para gatos en categorías:
        si "_id" está en el gato:
            cat["_id"] = str(cat["_id"])
    categorías de retorno

@api_router.post("/admin/categories")
async def admin_create_category(category: CategoryCreate, admin: str = Depends(verify_admin)):
    "Crear una nueva categoría"
    cat_id = f"cat_{str(uuid.uuid4())[:8]}"
    nuevo_gato = {
        "id": cat_id,
        "nombre": nombre.categoría,
        "orden": categoría.orden o 0,
        "activo": Verdadero
    }
    esperar db.categories.insert_one(new_cat)
    devolver nuevo_cat

@api_router.put("/admin/categories/{category_id}")
async def admin_update_category(category_id: str, data: dict, admin: str = Depends(verify_admin)):
    ""Actualizar una categoría""
    actualizar_datos = {k: v para k, v en data.items() si v no es None y k != "id"}
    si no se actualizan los datos:
        levantar HTTPException(status_code=400, detalle="No hay datos para actualizar")
    
    resultado = await db.categories.update_one({"id": category_id}, {"$set": update_data})
    Si result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    actualizado = await db.categories.find_one({"id": category_id})
    si "_id" está actualizado:
        actualizado["_id"] = str(actualizado["_id"])
    regreso actualizado

@api_router.delete("/admin/categories/{category_id}")
async def admin_delete_category(category_id: str, admin: str = Depends(verify_admin)):
    "Eliminar una categoría y sus productos"
    resultado = esperar db.categories.delete_one({"id": category_id})
    Si result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    # Eliminar también los productos de esta categoría
    await db.products.delete_many({"category_id": category_id})
    return {"mensaje": "Categoría eliminada"}

@api_router.get("/admin/products")
async def admin_get_products(category_id: Optional[str] = None, admin: str = Depends(verify_admin)):
    "Obtener todos los productos"
    consulta = {}
    si category_id:
        consulta["category_id"] = category_id
    productos = await db.products.find(query).to_list(1000)
    para productos en productos:
        si "_id" está en prod:
            prod["_id"] = str(prod["_id"])
    productos de devolución

@api_router.post("/admin/products")
async def admin_create_product(product: ProductCreate, admin: str = Depends(verify_admin)):
    "Crear un nuevo producto"
    # Subir imagen
    image_id = str(uuid.uuid4())
    esperar db.images.insert_one({
        "id": image_id,
        "imagen": imagen.producto,
        "marca de tiempo": datetime.utcnow()
    })
    base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://fcm-order-sync.preview.emergentagent.com')
    image_url = f"{base_url}/api/images/{image_id}"
    
    prod_id = f"prod_{str(uuid.uuid4())[:8]}"
    nuevo_producto = {
        "id": prod_id,
        "nombre": nombre.del.producto,
        "descripción": descripción.del.producto,
        "precio": precio.producto,
        "image_url": image_url,
        "image_base64": producto.imagen,
        "category_id": product.category_id,
        "activo": Verdadero
    }
    esperar a que db.products.insert_one(new_product)
    devolver nuevo_producto

@api_router.put("/admin/products/{product_id}")
async def admin_update_product(product_id: str, data: dict, admin: str = Depends(verify_admin)):
    ""Actualizar un producto""
    actualizar_datos = {}
    
    # Gestionar la actualización de la imagen si se proporciona
    Si data.get("image") y data["image"].startswith("data:image"):
        image_id = str(uuid.uuid4())
        esperar db.images.insert_one({
            "id": image_id,
            "imagen": datos["imagen"],
            "marca de tiempo": datetime.utcnow()
        })
        base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://fcm-order-sync.preview.emergentagent.com')
        update_data["image_url"] = f"{base_url}/api/images/{image_id}"
        actualizar_datos["imagen_base64"] = datos["imagen"]
    
    # Agregar otros campos
    para k en ["nombre", "descripción", "precio", "activo"]:
        Si k está en datos y data[k] no es None:
            actualizar_datos[k] = datos[k]
    
    si no se actualizan los datos:
        levantar HTTPException(status_code=400, detalle="No hay datos para actualizar")
    
    resultado = await db.products.update_one({"id": product_id}, {"$set": update_data})
    Si result.modified_count == 0:
        generar HTTPException(status_code=404, detalle="Producto no encontrado")
    
    actualizado = await db.products.find_one({"id": product_id})
    si "_id" está actualizado:
        actualizado["_id"] = str(actualizado["_id"])
    regreso actualizado

@api_router.delete("/admin/products/{product_id}")
async def admin_delete_product(product_id: str, admin: str = Depends(verify_admin)):
    "Eliminar un producto"
    resultado = await db.products.delete_one({"id": product_id})
    Si result.deleted_count == 0:
        generar HTTPException(status_code=404, detalle="Producto no encontrado")
    return {"mensaje": "Producto eliminado"}

# ============================================
# PÁGINA DE INICIO / CONFIGURACIÓN DEL SITIO WEB
# ============================================

clase SocialButton(BaseModel):
    id: str = Campo(default_factory=lambda: str(uuid.uuid4()))
    nombre: str # WhatsApp, Instagram, Facebook, etc.
    icon: str # Nombre del icono (whatsapp, instagram, facebook, map-marker, etc.)
    URL: str
    color: str = "#333333"
    activo: bool = True
    orden: int = 0

clase PopupImage(BaseModel):
    id: str = Campo(default_factory=lambda: str(uuid.uuid4()))
    URL de la imagen: str
    imagen_base64: Optional[str] = None
    Título: Optional[str] = Ninguno
    link_url: Opcional[str] = Ninguno
    activo: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

clase LandingConfig(BaseModel):
    app_download_url: str = ""
    app_download_text: str = "Descarga nuestra aplicación"
    hero_title: str = "Humy Embutidos"
    hero_subtitle: str = "Los mejores embutidos de República Dominicana"
    mostrar_botón_aplicación: bool = Verdadero
    botones_sociales: Lista[BotónSocial] = []
    imágenes_populares: Lista[ImagenPopular] = []

# Configuración de aterrizaje predeterminada
CONFIGURACIÓN_DE_ATERRIZAJE_PREDETERMINADA = {
    "app_download_url": "https://play.google.com/store/apps/details?id=com.arzlmno.humyembutidos",
    "app_download_text": "ðŸ“² Descarga nuestra aplicación",
    "hero_title": "Humy Embutidos",
    "hero_subtitle": "Los mejores embutidos de República Dominicana",
    "show_app_button": Verdadero,
    "social_buttons": [
        {
            "id": "whatsapp",
            "nombre": "WhatsApp",
            "icono": "whatsapp",
            "url": "https://wa.me/18299185606",
            "color": "#25D366",
            "activo": Verdadero,
            "orden": 0
        },
        {
            "id": "instagram",
            "nombre": "Instagram",
            "icono": "instagram",
            "url": "https://www.instagram.com/embotudoshumy/",
            "color": "#E4405F",
            "activo": Verdadero,
            "orden": 1
        },
        {
            "id": "facebook",
            "nombre": "Facebook",
            "icono": "facebook",
            "url": "https://www.facebook.com/profile.php?id=61572445319735",
            "color": "#1877F2",
            "activo": Verdadero,
            "orden": 2
        },
        {
            "id": "ubicacion",
            "nombre": "UbicaciÃ³n",
            "icono": "marcador de mapa",
            "url": "https://maps.app.goo.gl/e8G8tVgrkxx9YPik6",
            "color": "#EA4335",
            "activo": Verdadero,
            "orden": 3
        }
    ],
    "popup_images": []
}

# Obtener la configuración de la página de destino (pública)
@api_router.get("/landing/config")
async def get_landing_config():
    config = await db.landing_config.find_one({"_id": "main"})
    si no está configurado:
        # Inicializar con valores predeterminados
        default_config = {**DEFAULT_LANDING_CONFIG, "_id": "main"}
        await db.landing_config.insert_one(default_config)
        configuración = configuración_predeterminada
    
    # Eliminar el _id de MongoDB para la respuesta
    si "_id" en la configuración:
        del config["_id"]
    configuración de retorno

# Actualizar la configuración de la página de inicio (solo para administradores)
@api_router.put("/admin/landing/config")
async def update_landing_config(config: LandingConfig, credentials: HTTPBasicCredentials = Depends(security)):
    verificar_admin(credenciales)
    
    config_dict = config.dict()
    config_dict["_id"] = "main"
    
    esperar db.landing_config.replace_one(
        {"_id": "main"},
        config_dict,
        upsert=Verdadero
    )
    return {"message": "Configuración actualizada", "config": config.dict()}

# Agregar/Actualizar botón de redes sociales (solo administrador)
@api_router.post("/admin/landing/social-button")
async def add_social_button(button: SocialButton, credentials: HTTPBasicCredentials = Depends(security)):
    verificar_admin(credenciales)
    
    config = await db.landing_config.find_one({"_id": "main"})
    si no está configurado:
        config = {**DEFAULT_LANDING_CONFIG, "_id": "main"}
    
    botones = config.get("social_buttons", [])
    
    # Comprobar si existe un botón con el mismo ID
    existing_idx = next((i para i, b en enumerate(buttons) si b["id"] == button.id), None)
    Si existing_idx no es None:
        botones[index_existente] = botón.dict()
    demás:
        botones.append(botón.dict())
    
    esperar db.landing_config.update_one(
        {"_id": "main"},
        {"$set": {"social_buttons": buttons}},
        upsert=Verdadero
    )
    return {"message": "Botón guardado", "button": button.dict()}

# Eliminar botón de redes sociales (solo administrador)
@api_router.delete("/admin/landing/social-button/{button_id}")
async def delete_social_button(button_id: str, credentials: HTTPBasicCredentials = Depends(security)):
    verificar_admin(credenciales)
    
    resultado = esperar db.landing_config.update_one(
        {"_id": "main"},
        {"$pull": {"social_buttons": {"id": button_id}}}
    )
    return {"message": "Botón eliminado"}

# Agregar imagen emergente (solo administrador)
@api_router.post("/admin/landing/popup")
async def add_popup_image(popup: PopupImage, credentials: HTTPBasicCredentials = Depends(security)):
    verificar_admin(credenciales)
    
    # Manejar imagen base64
    Si popup.image_base64 y no popup.image_url:
        popup.image_url = popup.image_base64
    
    config = await db.landing_config.find_one({"_id": "main"})
    si no está configurado:
        config = {**DEFAULT_LANDING_CONFIG, "_id": "main"}
    
    ventanas emergentes = config.get("popup_images", [])
    popups.append(popup.dict())
    
    esperar db.landing_config.update_one(
        {"_id": "main"},
        {"$set": {"popup_images": popups}},
        upsert=Verdadero
    )
    return {"mensaje": "Ventana emergente agregada", "ventana emergente": ventana emergente.dict()}

# Actualizar imagen emergente (solo administrador)
@api_router.put("/admin/landing/popup/{popup_id}")
async def update_popup_image(popup_id: str, popup: PopupImage, credentials: HTTPBasicCredentials = Depends(security)):
    verificar_admin(credenciales)
    
    config = await db.landing_config.find_one({"_id": "main"})
    si no está configurado:
        levantar HTTPException(status_code=404, detalle="Configuración no encontrada")
    
    ventanas emergentes = config.get("popup_images", [])
    popup_idx = next((i para i, p en enumerate(popups) si p["id"] == popup_id), None)
    
    Si popup_idx es None:
        raise HTTPException(status_code=404, detail="Popup no encontrado")
    
    popup.id = popup_id
    Si popup.image_base64 y no popup.image_url:
        popup.image_url = popup.image_base64
    
    popups[popup_idx] = popup.dict()
    
    esperar db.landing_config.update_one(
        {"_id": "main"},
        {"$set": {"popup_images": popups}}
    )
    return {"message": "Popup actualizado", "popup": popup.dict()}

# Eliminar imagen emergente (solo administrador)
@api_router.delete("/admin/landing/popup/{popup_id}")
async def delete_popup_image(popup_id: str, credentials: HTTPBasicCredentials = Depends(security)):
    verificar_admin(credenciales)
    
    resultado = esperar db.landing_config.update_one(
        {"_id": "main"},
        {"$pull": {"popup_images": {"id": popup_id}}}
    )
    return {"mensaje": "Popup eliminado"}

# Mostrar/ocultar el estado de la ventana emergente (solo para administradores)
@api_router.patch("/admin/landing/popup/{popup_id}/toggle")
async def toggle_popup(popup_id: str, credentials: HTTPBasicCredentials = Depends(security)):
    verificar_admin(credenciales)
    
    config = await db.landing_config.find_one({"_id": "main"})
    si no está configurado:
        levantar HTTPException(status_code=404, detalle="Configuración no encontrada")
    
    ventanas emergentes = config.get("popup_images", [])
    para ventanas emergentes en ventanas emergentes:
        Si popup["id"] == popup_id:
            popup["active"] = no popup.get("active", True)
            romper
    
    esperar db.landing_config.update_one(
        {"_id": "main"},
        {"$set": {"popup_images": popups}}
    )
    return {"message": "Estado del popup cambiado"}

# ===== CONTADOR DE VISITAS =====
@api_router.post("/visits/track")
async def track_visit():
    """Incrementa el contador de visitas y devuelve el recuento actual"""
    resultado = esperar db.site_stats.find_one_and_update(
        {"_id": "visitas"},
        {"$inc": {"count": 1}},
        upsert=Verdadero,
        return_document=Verdadero
    )
    return {"count": result.get("count", 1)}

@api_router.get("/visits/count")
async def get_visit_count():
    "Obtener el número de visitas actual sin incrementarlo"
    estadísticas = await db.site_stats.find_one({"_id": "visitas"})
    contador = estadísticas.get("contador", 0) si estadísticas sino 0
    devolver {"count": count}

# Incluir el enrutador en la aplicación principal
app.include_router(api_router)

aplicación.add_middleware(
    CORSMiddleware,
    permitir_credenciales=Verdadero,
    permitir_orígenes=["*"],
    permitir_métodos=["*"],
    permitir_encabezados=["*"],
)

# Configurar el registro
logging.basicConfig(
    nivel=registro.INFO,
    formato='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
registrador = registro.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    cliente.close() 
