
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import urllib.parse
import secrets
import hashlib


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBasic()

# Admin credentials
# Admin credentials - Load from environment variables
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'EmbutidosHumy')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Venezuelateamo101993*')

# WhatsApp Number for orders
WHATSAPP_NUMBER = "8299185606"

# Bank accounts
BANK_ACCOUNTS = {
    "popular": {
        "bank": "Banco Popular",
        "holder": "Mileidy Guevara",
        "account": "823515960",
        "type": "Corriente"
    },
    "banreservas": {
        "bank": "Banreservas",
        "holder": "Mileidy Guevara",
        "account": "9605147823",
        "type": "Ahorro"
    }
}

# Default Combo data (will be migrated to DB)
DEFAULT_COMBOS = [
    {
        "id": "combo1",
        "name": "Super Combo 1",
        "description": "2 LB Chuleta Ahumada, 1 LB Costilla Ahumada, 1 LB Jamón Cocido, 1 LB Longaniza Fina",
        "price": 660,
        "image_url": "https://customer-assets.emergentagent.com/job_d0ebc224-4e42-4a7d-b183-a128866ac01c/artifacts/wr5w0v5h_IMG-20260227-WA0021.jpg",
        "active": True
    },
    {
        "id": "combo2",
        "name": "Super Combo 2",
        "description": "2 LB Chuleta Ahumada, 1 LB Costilla Ahumada, 1 LB Jamón Cocido, 1 LB Queso Cheddar, 1 LB Salami Mallita",
        "price": 900,
        "image_url": "https://customer-assets.emergentagent.com/job_d0ebc224-4e42-4a7d-b183-a128866ac01c/artifacts/9zucrp2o_IMG-20260227-WA0020.jpg",
        "active": True
    },
    {
        "id": "combo3",
        "name": "Super Combo 3",
        "description": "2 LB Chuleta Ahumada, 1 LB Costilla Ahumada, 1 LB Jamón Picnic, 1 LB Queso Cheddar, 1 LB Salami Induveca, 1 LB Queso de Freír, 1 LB Longaniza Fina",
        "price": 1290,
        "image_url": "https://customer-assets.emergentagent.com/job_d0ebc224-4e42-4a7d-b183-a128866ac01c/artifacts/xwfllsol_IMG-20260227-WA0023.jpg",
        "active": True
    },
    {
        "id": "combo4",
        "name": "Super Combo 4",
        "description": "2 LB Chuleta Ahumada, 1 LB Costilla Ahumada, 1 LB Jamón Picnic, 1 LB Queso Cheddar, 1 LB Salami Induveca, 1 LB Queso de Freír, 1 Cartón de Huevo",
        "price": 1290,
        "image_url": "https://customer-assets.emergentagent.com/job_d0ebc224-4e42-4a7d-b183-a128866ac01c/artifacts/yljz2eqn_IMG-20260227-WA0022.jpg",
        "active": True
    }
]

# Define Models
class Combo(BaseModel):
    id: str
    name: str
    description: str
    price: int
    image_url: str
    active: bool = True

class ComboCreate(BaseModel):
    name: str
    description: str
    price: int
    image_url: str

class ComboUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None

class BankAccount(BaseModel):
    bank: str
    holder: str
    account: str
    type: str

class OrderItem(BaseModel):
    combo_id: str
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItem]
    customer_name: str
    customer_phone: str
    location: str
    location_link: Optional[str] = None
    payment_method: str
    receipt_image: Optional[str] = None
    delivery_method: Optional[str] = "delivery"  # retiro or delivery

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    items: List[OrderItem]
    customer_name: str
    customer_phone: str
    location: str
    location_link: Optional[str] = None
    payment_method: Optional[str] = "efectivo"
    delivery_method: Optional[str] = "delivery"
    receipt_url: Optional[str] = None
    total: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    whatsapp_url: str
    status: str = "pendiente"  # pendiente, entregado, cancelado

class OrderStatusUpdate(BaseModel):
    status: str

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None

class ReceiptUpload(BaseModel):
    image: str

class ReceiptResponse(BaseModel):
    receipt_id: str
    receipt_url: str

class SalesStats(BaseModel):
    total_orders: int
    total_revenue: int
    orders_today: int
    revenue_today: int
    orders_week: int
    revenue_week: int
    orders_month: int
    revenue_month: int

class PromoCreate(BaseModel):
    image: str  # Base64 image
    title: Optional[str] = "Oferta Especial"
    description: Optional[str] = None

class Promo(BaseModel):
    id: str
    image_url: str
    title: str
    description: Optional[str] = None
    active: bool = True
    created_at: datetime

# Category and Product models
class CategoryCreate(BaseModel):
    name: str
    order: Optional[int] = 0

class Category(BaseModel):
    id: str
    name: str
    order: int = 0
    active: bool = True

class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    image: str  # Base64 image
    category_id: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: int
    image_url: str
    category_id: str
    active: bool = True

class StoreSettings(BaseModel):
    products_enabled: bool = False

# Helper function to verify admin credentials
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Initialize combos in database
async def init_combos():
    count = await db.combos.count_documents({})
    if count == 0:
        await db.combos.insert_many(DEFAULT_COMBOS)
        logging.info("Combos initialized in database")

@app.on_event("startup")
async def startup_event():
    await init_combos()

# ============== PUBLIC ROUTES ==============

@api_router.get("/")
async def root():
    return {"message": "Embutidos Humy API"}

@api_router.get("/combos", response_model=List[Combo])
async def get_combos():
    combos = await db.combos.find({"active": True}).to_list(100)
    if not combos:
        # Fallback to default if DB is empty
        return DEFAULT_COMBOS
    return [Combo(**combo) for combo in combos]

@api_router.get("/combos/{combo_id}", response_model=Combo)
async def get_combo(combo_id: str):
    combo = await db.combos.find_one({"id": combo_id})
    if not combo:
        raise HTTPException(status_code=404, detail="Combo not found")
    return Combo(**combo)

@api_router.get("/bank-accounts")
async def get_bank_accounts():
    return BANK_ACCOUNTS

@api_router.get("/store-settings")
async def get_store_settings():
    """Get store settings including products enabled status and store open status"""
    settings = await db.settings.find_one({"type": "store"})
    if not settings:
        return {"products_enabled": False, "store_open": True, "closed_message": ""}
    return {
        "products_enabled": settings.get("products_enabled", False),
        "store_open": settings.get("store_open", True),
        "closed_message": settings.get("closed_message", "En este momento no contamos con inventario. Estamos anotando pedidos para entregar el día lunes. Recuerda que buscamos mercancía el mismo día lunes y retornamos a las 3:00 PM.")
    }

@api_router.get("/categories")
async def get_categories():
    """Get all active categories"""
    settings = await db.settings.find_one({"type": "store"})
    if not settings or not settings.get("products_enabled", False):
        return []
    categories = await db.categories.find({"active": True}).sort("order", 1).to_list(100)
    for cat in categories:
        if "_id" in cat:
            cat["_id"] = str(cat["_id"])
    return categories

@api_router.get("/products")
async def get_products(category_id: Optional[str] = None):
    """Get all active products, optionally filtered by category"""
    settings = await db.settings.find_one({"type": "store"})
    if not settings or not settings.get("products_enabled", False):
        return []
    
    query = {"active": True}
    if category_id:
        query["category_id"] = category_id
    
    products = await db.products.find(query).to_list(1000)
    for prod in products:
        if "_id" in prod:
            prod["_id"] = str(prod["_id"])
    return products

@api_router.get("/promo")
async def get_active_promo():
    """Get the currently active promotion"""
    promo = await db.promos.find_one({"active": True})
    if not promo:
        return None
    # Convert ObjectId to string
    if "_id" in promo:
        promo["_id"] = str(promo["_id"])
    return promo

@api_router.post("/upload-receipt", response_model=ReceiptResponse)
async def upload_receipt(receipt: ReceiptUpload):
    receipt_id = str(uuid.uuid4())
    await db.receipts.insert_one({
        "id": receipt_id,
        "image": receipt.image,
        "timestamp": datetime.utcnow()
    })
    base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://humy-embutidos-2.preview.emergentagent.com')
    receipt_url = f"{base_url}/api/receipts/{receipt_id}"
    return ReceiptResponse(receipt_id=receipt_id, receipt_url=receipt_url)

@api_router.get("/receipts/{receipt_id}")
async def get_receipt(receipt_id: str):
    from fastapi.responses import HTMLResponse
    receipt = await db.receipts.find_one({"id": receipt_id})
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comprobante de Pago - Embutidos Humy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; text-align: center; }}
            h1 {{ color: #C41E24; font-size: 24px; }}
            img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }}
        </style>
    </head>
    <body>
        <h1>Comprobante de Pago</h1>
        <img src="{receipt['image']}" alt="Comprobante de pago">
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@api_router.post("/orders", response_model=Order)
async def create_order(order_input: OrderCreate):
    # Get combos from database
    combos = await db.combos.find({"active": True}).to_list(100)
    if not combos:
        combos = DEFAULT_COMBOS
    
    # Get products from database
    products = await db.products.find({"active": True}).to_list(1000)
    
    total = 0
    order_details = []
    
    for item in order_input.items:
        # First check if it's a combo
        combo = next((c for c in combos if c["id"] == item.combo_id), None)
        if combo and item.quantity > 0:
            subtotal = combo["price"] * item.quantity
            total += subtotal
            order_details.append(f"{item.quantity}x {combo['name']} - RD${subtotal:,}")
        else:
            # Check if it's a product
            product = next((p for p in products if p["id"] == item.combo_id), None)
            if product and item.quantity > 0:
                subtotal = product["price"] * item.quantity
                total += subtotal
                order_details.append(f"{item.quantity}x {product['name']} - RD${subtotal:,}")
    
    # Handle receipt upload
    receipt_url = None
    if order_input.receipt_image:
        receipt_id = str(uuid.uuid4())
        await db.receipts.insert_one({
            "id": receipt_id,
            "image": order_input.receipt_image,
            "timestamp": datetime.utcnow()
        })
        base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://humy-embutidos-2.preview.emergentagent.com')
        receipt_url = f"{base_url}/api/receipts/{receipt_id}"
    
    # Delivery method text
    delivery_text = "🏪 Retiro en Local" if order_input.delivery_method == "retiro" else "🚴 Delivery"
    
    # Create WhatsApp message
    message_lines = [
        "*NUEVO PEDIDO - EMBUTIDOS HUMY*",
        "",
        f"*ENTREGA:* {delivery_text}",
        "",
        "*CLIENTE:*",
        f"Nombre: {order_input.customer_name}",
        f"Teléfono: {order_input.customer_phone}",
    ]
    
    # Only add location for delivery orders
    if order_input.delivery_method == "delivery":
        message_lines.append(f"Ubicación: {order_input.location}")
        if order_input.location_link:
            message_lines.append(f"")
            message_lines.append(f"📍 *Ver ubicación en mapa:*")
            message_lines.append(f"{order_input.location_link}")
    
    message_lines.extend(["", "*PEDIDO:*"])
    message_lines.extend(order_details)
    
    payment_text = "Efectivo" if order_input.payment_method == "efectivo" else "Transferencia"
    message_lines.extend([
        "",
        f"*TOTAL: RD${total:,}*",
        f"*Método de pago:* {payment_text}",
    ])
    
    if receipt_url:
        message_lines.extend([
            "",
            "📎 *Comprobante de pago:*",
            receipt_url
        ])
    
    message = "\n".join(message_lines)
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"
    
    order = Order(
        items=order_input.items,
        customer_name=order_input.customer_name,
        customer_phone=order_input.customer_phone,
        location=order_input.location,
        location_link=order_input.location_link,
        payment_method=order_input.payment_method,
        delivery_method=order_input.delivery_method,
        receipt_url=receipt_url,
        total=total,
        whatsapp_url=whatsapp_url,
        status="pendiente"
    )
    
    # Convert to dict and insert into database
    order_dict = order.dict()
    await db.orders.insert_one(order_dict.copy())
    return order

@api_router.get("/orders", response_model=List[Order])
async def get_orders():
    orders = await db.orders.find().sort("timestamp", -1).to_list(1000)
    # Convert ObjectId to string to avoid serialization issues
    result = []
    for order in orders:
        if "_id" in order:
            del order["_id"]
        result.append(Order(**order))
    return result

# ============== ADMIN ROUTES ==============

@api_router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(login: AdminLogin):
    if login.username == ADMIN_USERNAME and login.password == ADMIN_PASSWORD:
        # Generate a simple token
        token = hashlib.sha256(f"{login.username}{datetime.utcnow().isoformat()}".encode()).hexdigest()
        return AdminLoginResponse(success=True, message="Login exitoso", token=token)
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@api_router.get("/admin/orders")
async def admin_get_orders(admin: str = Depends(verify_admin)):
    orders = await db.orders.find().sort("timestamp", -1).to_list(1000)
    # Convert ObjectId to string
    for order in orders:
        if "_id" in order:
            order["_id"] = str(order["_id"])
    return orders

@api_router.put("/admin/orders/{order_id}/status")
async def admin_update_order_status(order_id: str, status_update: OrderStatusUpdate, admin: str = Depends(verify_admin)):
    result = await db.orders.update_one(
        {"id": order_id},
        {"$set": {"status": status_update.status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {"message": "Estado actualizado", "status": status_update.status}

@api_router.get("/admin/combos")
async def admin_get_combos(admin: str = Depends(verify_admin)):
    combos = await db.combos.find().to_list(100)
    # Convert ObjectId to string
    for combo in combos:
        if "_id" in combo:
            combo["_id"] = str(combo["_id"])
    return combos

@api_router.post("/admin/combos")
async def admin_create_combo(combo: ComboCreate, admin: str = Depends(verify_admin)):
    combo_id = f"combo_{str(uuid.uuid4())[:8]}"
    new_combo = {
        "id": combo_id,
        "name": combo.name,
        "description": combo.description,
        "price": combo.price,
        "image_url": combo.image_url,
        "active": True
    }
    await db.combos.insert_one(new_combo)
    return new_combo

@api_router.put("/admin/combos/{combo_id}")
async def admin_update_combo(combo_id: str, combo_update: ComboUpdate, admin: str = Depends(verify_admin)):
    update_data = {k: v for k, v in combo_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = await db.combos.update_one(
        {"id": combo_id},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Combo no encontrado")
    
    updated_combo = await db.combos.find_one({"id": combo_id})
    return updated_combo

@api_router.delete("/admin/combos/{combo_id}")
async def admin_delete_combo(combo_id: str, admin: str = Depends(verify_admin)):
    result = await db.combos.delete_one({"id": combo_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Combo no encontrado")
    return {"message": "Combo eliminado"}

@api_router.delete("/admin/orders/{order_id}")
async def admin_delete_order(order_id: str, admin: str = Depends(verify_admin)):
    """Delete an order (only cancelled orders can be deleted)"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    result = await db.orders.delete_one({"id": order_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No se pudo eliminar el pedido")
    return {"message": "Pedido eliminado"}

@api_router.get("/admin/stats", response_model=SalesStats)
async def admin_get_stats(admin: str = Depends(verify_admin)):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)
    
    # Only count DELIVERED orders as effective sales
    all_orders = await db.orders.find({"status": "entregado"}).to_list(10000)
    total_orders = len(all_orders)
    total_revenue = sum(o.get("total", 0) for o in all_orders)
    
    # Today - only delivered
    today_orders = [o for o in all_orders if o.get("timestamp", datetime.min) >= today_start]
    orders_today = len(today_orders)
    revenue_today = sum(o.get("total", 0) for o in today_orders)
    
    # This week - only delivered
    week_orders = [o for o in all_orders if o.get("timestamp", datetime.min) >= week_start]
    orders_week = len(week_orders)
    revenue_week = sum(o.get("total", 0) for o in week_orders)
    
    # This month - only delivered
    month_orders = [o for o in all_orders if o.get("timestamp", datetime.min) >= month_start]
    orders_month = len(month_orders)
    revenue_month = sum(o.get("total", 0) for o in month_orders)
    
    return SalesStats(
        total_orders=total_orders,
        total_revenue=total_revenue,
        orders_today=orders_today,
        revenue_today=revenue_today,
        orders_week=orders_week,
        revenue_week=revenue_week,
        orders_month=orders_month,
        revenue_month=revenue_month
    )

@api_router.get("/admin/sales-history")
async def admin_get_sales_history(admin: str = Depends(verify_admin)):
    """Get detailed sales history grouped by day, month, year - only delivered orders"""
    # Get all delivered orders
    all_orders = await db.orders.find({"status": "entregado"}).to_list(10000)
    
    # Get combos for names
    combos = await db.combos.find().to_list(100)
    combo_names = {c["id"]: c["name"] for c in combos}
    
    # Group by day
    daily_sales = {}
    monthly_sales = {}
    yearly_sales = {}
    
    for order in all_orders:
        timestamp = order.get("timestamp", datetime.utcnow())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        day_key = timestamp.strftime("%Y-%m-%d")
        month_key = timestamp.strftime("%Y-%m")
        year_key = timestamp.strftime("%Y")
        
        total = order.get("total", 0)
        items = order.get("items", [])
        
        # Process items for combo breakdown
        combo_breakdown = {}
        for item in items:
            combo_id = item.get("combo_id")
            qty = item.get("quantity", 0)
            combo_name = combo_names.get(combo_id, combo_id)
            if combo_name not in combo_breakdown:
                combo_breakdown[combo_name] = 0
            combo_breakdown[combo_name] += qty
        
        # Daily
        if day_key not in daily_sales:
            daily_sales[day_key] = {"date": day_key, "orders": 0, "revenue": 0, "combos": {}}
        daily_sales[day_key]["orders"] += 1
        daily_sales[day_key]["revenue"] += total
        for combo, qty in combo_breakdown.items():
            if combo not in daily_sales[day_key]["combos"]:
                daily_sales[day_key]["combos"][combo] = 0
            daily_sales[day_key]["combos"][combo] += qty
        
        # Monthly
        if month_key not in monthly_sales:
            monthly_sales[month_key] = {"month": month_key, "orders": 0, "revenue": 0, "combos": {}}
        monthly_sales[month_key]["orders"] += 1
        monthly_sales[month_key]["revenue"] += total
        for combo, qty in combo_breakdown.items():
            if combo not in monthly_sales[month_key]["combos"]:
                monthly_sales[month_key]["combos"][combo] = 0
            monthly_sales[month_key]["combos"][combo] += qty
        
        # Yearly
        if year_key not in yearly_sales:
            yearly_sales[year_key] = {"year": year_key, "orders": 0, "revenue": 0, "combos": {}}
        yearly_sales[year_key]["orders"] += 1
        yearly_sales[year_key]["revenue"] += total
        for combo, qty in combo_breakdown.items():
            if combo not in yearly_sales[year_key]["combos"]:
                yearly_sales[year_key]["combos"][combo] = 0
            yearly_sales[year_key]["combos"][combo] += qty
    
    # Sort by date descending
    daily_list = sorted(daily_sales.values(), key=lambda x: x["date"], reverse=True)
    monthly_list = sorted(monthly_sales.values(), key=lambda x: x["month"], reverse=True)
    yearly_list = sorted(yearly_sales.values(), key=lambda x: x["year"], reverse=True)
    
    return {
        "daily": daily_list[:30],  # Last 30 days
        "monthly": monthly_list[:12],  # Last 12 months
        "yearly": yearly_list  # All years
    }

@api_router.post("/admin/upload-image")
async def admin_upload_image(image_data: dict, admin: str = Depends(verify_admin)):
    """Upload an image and return a URL"""
    image_id = str(uuid.uuid4())
    await db.images.insert_one({
        "id": image_id,
        "image": image_data.get("image"),
        "timestamp": datetime.utcnow()
    })
    base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://humy-embutidos-2.preview.emergentagent.com')
    image_url = f"{base_url}/api/images/{image_id}"
    return {"image_url": image_url}

@api_router.get("/images/{image_id}")
async def get_image(image_id: str):
    from fastapi.responses import HTMLResponse
    image = await db.images.find_one({"id": image_id})
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Imagen - Embutidos Humy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f5f5f5; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <img src="{image['image']}" alt="Imagen">
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ============== PROMO ADMIN ROUTES ==============

@api_router.get("/admin/promo")
async def admin_get_promo(admin: str = Depends(verify_admin)):
    """Get the current promo (active or not)"""
    promo = await db.promos.find_one({}, sort=[("created_at", -1)])
    if promo:
        if "_id" in promo:
            promo["_id"] = str(promo["_id"])
    return promo

@api_router.post("/admin/promo")
async def admin_create_promo(promo_data: PromoCreate, admin: str = Depends(verify_admin)):
    """Create or update promotion"""
    # Deactivate all existing promos
    await db.promos.update_many({}, {"$set": {"active": False}})
    
    # Upload image
    image_id = str(uuid.uuid4())
    await db.images.insert_one({
        "id": image_id,
        "image": promo_data.image,
        "timestamp": datetime.utcnow()
    })
    base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://humy-embutidos-2.preview.emergentagent.com')
    image_url = f"{base_url}/api/images/{image_id}"
    
    # Create new promo
    promo_id = str(uuid.uuid4())
    new_promo = {
        "id": promo_id,
        "image_url": image_url,
        "image_base64": promo_data.image,  # Store base64 for direct display
        "title": promo_data.title or "Oferta Especial",
        "description": promo_data.description,
        "active": True,
        "created_at": datetime.utcnow()
    }
    await db.promos.insert_one(new_promo)
    
    return {"message": "Promoción creada", "promo_id": promo_id}

@api_router.put("/admin/promo/{promo_id}/toggle")
async def admin_toggle_promo(promo_id: str, admin: str = Depends(verify_admin)):
    """Toggle promo active status"""
    promo = await db.promos.find_one({"id": promo_id})
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    
    new_status = not promo.get("active", False)
    await db.promos.update_one({"id": promo_id}, {"$set": {"active": new_status}})
    
    return {"message": "Estado actualizado", "active": new_status}

@api_router.delete("/admin/promo/{promo_id}")
async def admin_delete_promo(promo_id: str, admin: str = Depends(verify_admin)):
    """Delete a promotion"""
    result = await db.promos.delete_one({"id": promo_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
    return {"message": "Promoción eliminada"}

# ============== PRODUCTS & CATEGORIES ADMIN ROUTES ==============

@api_router.get("/admin/store-settings")
async def admin_get_store_settings(admin: str = Depends(verify_admin)):
    """Get store settings"""
    settings = await db.settings.find_one({"type": "store"})
    if not settings:
        return {"products_enabled": False, "store_open": True, "closed_message": "En este momento no contamos con inventario. Estamos anotando pedidos para entregar el día lunes. Recuerda que buscamos mercancía el mismo día lunes y retornamos a las 3:00 PM."}
    return {
        "products_enabled": settings.get("products_enabled", False),
        "store_open": settings.get("store_open", True),
        "closed_message": settings.get("closed_message", "En este momento no contamos con inventario. Estamos anotando pedidos para entregar el día lunes. Recuerda que buscamos mercancía el mismo día lunes y retornamos a las 3:00 PM.")
    }

@api_router.put("/admin/store-settings")
async def admin_update_store_settings(settings: dict, admin: str = Depends(verify_admin)):
    """Update store settings"""
    update_data = {}
    if "products_enabled" in settings:
        update_data["products_enabled"] = settings["products_enabled"]
    if "store_open" in settings:
        update_data["store_open"] = settings["store_open"]
    if "closed_message" in settings:
        update_data["closed_message"] = settings["closed_message"]
    
    await db.settings.update_one(
        {"type": "store"},
        {"$set": update_data},
        upsert=True
    )
    
    # Get updated settings
    updated = await db.settings.find_one({"type": "store"})
    return {
        "message": "Configuración actualizada",
        "products_enabled": updated.get("products_enabled", False),
        "store_open": updated.get("store_open", True),
        "closed_message": updated.get("closed_message", "")
    }

@api_router.get("/admin/categories")
async def admin_get_categories(admin: str = Depends(verify_admin)):
    """Get all categories"""
    categories = await db.categories.find().sort("order", 1).to_list(100)
    for cat in categories:
        if "_id" in cat:
            cat["_id"] = str(cat["_id"])
    return categories

@api_router.post("/admin/categories")
async def admin_create_category(category: CategoryCreate, admin: str = Depends(verify_admin)):
    """Create a new category"""
    cat_id = f"cat_{str(uuid.uuid4())[:8]}"
    new_cat = {
        "id": cat_id,
        "name": category.name,
        "order": category.order or 0,
        "active": True
    }
    await db.categories.insert_one(new_cat)
    return new_cat

@api_router.put("/admin/categories/{category_id}")
async def admin_update_category(category_id: str, data: dict, admin: str = Depends(verify_admin)):
    """Update a category"""
    update_data = {k: v for k, v in data.items() if v is not None and k != "id"}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = await db.categories.update_one({"id": category_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    updated = await db.categories.find_one({"id": category_id})
    if "_id" in updated:
        updated["_id"] = str(updated["_id"])
    return updated

@api_router.delete("/admin/categories/{category_id}")
async def admin_delete_category(category_id: str, admin: str = Depends(verify_admin)):
    """Delete a category and its products"""
    result = await db.categories.delete_one({"id": category_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    # Also delete products in this category
    await db.products.delete_many({"category_id": category_id})
    return {"message": "Categoría eliminada"}

@api_router.get("/admin/products")
async def admin_get_products(category_id: Optional[str] = None, admin: str = Depends(verify_admin)):
    """Get all products"""
    query = {}
    if category_id:
        query["category_id"] = category_id
    products = await db.products.find(query).to_list(1000)
    for prod in products:
        if "_id" in prod:
            prod["_id"] = str(prod["_id"])
    return products

@api_router.post("/admin/products")
async def admin_create_product(product: ProductCreate, admin: str = Depends(verify_admin)):
    """Create a new product"""
    # Upload image
    image_id = str(uuid.uuid4())
    await db.images.insert_one({
        "id": image_id,
        "image": product.image,
        "timestamp": datetime.utcnow()
    })
    base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://humy-embutidos-2.preview.emergentagent.com')
    image_url = f"{base_url}/api/images/{image_id}"
    
    prod_id = f"prod_{str(uuid.uuid4())[:8]}"
    new_product = {
        "id": prod_id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image_url": image_url,
        "image_base64": product.image,
        "category_id": product.category_id,
        "active": True
    }
    await db.products.insert_one(new_product)
    return new_product

@api_router.put("/admin/products/{product_id}")
async def admin_update_product(product_id: str, data: dict, admin: str = Depends(verify_admin)):
    """Update a product"""
    update_data = {}
    
    # Handle image update if provided
    if data.get("image") and data["image"].startswith("data:image"):
        image_id = str(uuid.uuid4())
        await db.images.insert_one({
            "id": image_id,
            "image": data["image"],
            "timestamp": datetime.utcnow()
        })
        base_url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://humy-embutidos-2.preview.emergentagent.com')
        update_data["image_url"] = f"{base_url}/api/images/{image_id}"
        update_data["image_base64"] = data["image"]
    
    # Add other fields
    for k in ["name", "description", "price", "active"]:
        if k in data and data[k] is not None:
            update_data[k] = data[k]
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = await db.products.update_one({"id": product_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    updated = await db.products.find_one({"id": product_id})
    if "_id" in updated:
        updated["_id"] = str(updated["_id"])
    return updated

@api_router.delete("/admin/products/{product_id}")
async def admin_delete_product(product_id: str, admin: str = Depends(verify_admin)):
    """Delete a product"""
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado"}

# ============================================
# LANDING PAGE / WEBSITE CONFIGURATION
# ============================================

class SocialButton(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # WhatsApp, Instagram, Facebook, etc.
    icon: str  # Nombre del icono (whatsapp, instagram, facebook, map-marker, etc.)
    url: str
    color: str = "#333333"
    active: bool = True
    order: int = 0

class PopupImage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_url: str
    image_base64: Optional[str] = None
    title: Optional[str] = None
    link_url: Optional[str] = None
    active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class LandingConfig(BaseModel):
    app_download_url: str = ""
    app_download_text: str = "Descarga nuestra App"
    hero_title: str = "Humy Embutidos"
    hero_subtitle: str = "Los mejores embutidos de República Dominicana"
    show_app_button: bool = True
    social_buttons: List[SocialButton] = []
    popup_images: List[PopupImage] = []

# Default landing configuration
DEFAULT_LANDING_CONFIG = {
    "app_download_url": "https://play.google.com/store/apps/details?id=com.arzlmno.humyembutidos",
    "app_download_text": "📲 Descarga nuestra App",
    "hero_title": "Humy Embutidos",
    "hero_subtitle": "Los mejores embutidos de República Dominicana",
    "show_app_button": True,
    "social_buttons": [
        {
            "id": "whatsapp",
            "name": "WhatsApp",
            "icon": "whatsapp",
            "url": "https://wa.me/18299185606",
            "color": "#25D366",
            "active": True,
            "order": 0
        },
        {
            "id": "instagram",
            "name": "Instagram",
            "icon": "instagram",
            "url": "https://www.instagram.com/embutidoshumy/",
            "color": "#E4405F",
            "active": True,
            "order": 1
        },
        {
            "id": "facebook",
            "name": "Facebook",
            "icon": "facebook",
            "url": "https://www.facebook.com/profile.php?id=61572445319735",
            "color": "#1877F2",
            "active": True,
            "order": 2
        },
        {
            "id": "ubicacion",
            "name": "Ubicación",
            "icon": "map-marker",
            "url": "https://maps.app.goo.gl/e8G8tVgrkxx9YPik6",
            "color": "#EA4335",
            "active": True,
            "order": 3
        }
    ],
    "popup_images": []
}

# Get landing page configuration (public)
@api_router.get("/landing/config")
async def get_landing_config():
    config = await db.landing_config.find_one({"_id": "main"})
    if not config:
        # Initialize with defaults
        default_config = {**DEFAULT_LANDING_CONFIG, "_id": "main"}
        await db.landing_config.insert_one(default_config)
        config = default_config
    
    # Remove MongoDB _id for response
    if "_id" in config:
        del config["_id"]
    return config

# Update landing page configuration (admin only)
@api_router.put("/admin/landing/config")
async def update_landing_config(config: LandingConfig, credentials: HTTPBasicCredentials = Depends(security)):
    verify_admin(credentials)
    
    config_dict = config.dict()
    config_dict["_id"] = "main"
    
    await db.landing_config.replace_one(
        {"_id": "main"},
        config_dict,
        upsert=True
    )
    return {"message": "Configuración actualizada", "config": config.dict()}

# Add/Update social button (admin only)
@api_router.post("/admin/landing/social-button")
async def add_social_button(button: SocialButton, credentials: HTTPBasicCredentials = Depends(security)):
    verify_admin(credentials)
    
    config = await db.landing_config.find_one({"_id": "main"})
    if not config:
        config = {**DEFAULT_LANDING_CONFIG, "_id": "main"}
    
    buttons = config.get("social_buttons", [])
    
    # Check if button with same ID exists
    existing_idx = next((i for i, b in enumerate(buttons) if b["id"] == button.id), None)
    if existing_idx is not None:
        buttons[existing_idx] = button.dict()
    else:
        buttons.append(button.dict())
    
    await db.landing_config.update_one(
        {"_id": "main"},
        {"$set": {"social_buttons": buttons}},
        upsert=True
    )
    return {"message": "Botón guardado", "button": button.dict()}

# Delete social button (admin only)
@api_router.delete("/admin/landing/social-button/{button_id}")
async def delete_social_button(button_id: str, credentials: HTTPBasicCredentials = Depends(security)):
    verify_admin(credentials)
    
    result = await db.landing_config.update_one(
        {"_id": "main"},
        {"$pull": {"social_buttons": {"id": button_id}}}
    )
    return {"message": "Botón eliminado"}

# Add popup image (admin only)
@api_router.post("/admin/landing/popup")
async def add_popup_image(popup: PopupImage, credentials: HTTPBasicCredentials = Depends(security)):
    verify_admin(credentials)
    
    # Handle base64 image
    if popup.image_base64 and not popup.image_url:
        popup.image_url = popup.image_base64
    
    config = await db.landing_config.find_one({"_id": "main"})
    if not config:
        config = {**DEFAULT_LANDING_CONFIG, "_id": "main"}
    
    popups = config.get("popup_images", [])
    popups.append(popup.dict())
    
    await db.landing_config.update_one(
        {"_id": "main"},
        {"$set": {"popup_images": popups}},
        upsert=True
    )
    return {"message": "Popup agregado", "popup": popup.dict()}

# Update popup image (admin only)
@api_router.put("/admin/landing/popup/{popup_id}")
async def update_popup_image(popup_id: str, popup: PopupImage, credentials: HTTPBasicCredentials = Depends(security)):
    verify_admin(credentials)
    
    config = await db.landing_config.find_one({"_id": "main"})
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    popups = config.get("popup_images", [])
    popup_idx = next((i for i, p in enumerate(popups) if p["id"] == popup_id), None)
    
    if popup_idx is None:
        raise HTTPException(status_code=404, detail="Popup no encontrado")
    
    popup.id = popup_id
    if popup.image_base64 and not popup.image_url:
        popup.image_url = popup.image_base64
    
    popups[popup_idx] = popup.dict()
    
    await db.landing_config.update_one(
        {"_id": "main"},
        {"$set": {"popup_images": popups}}
    )
    return {"message": "Popup actualizado", "popup": popup.dict()}

# Delete popup image (admin only)
@api_router.delete("/admin/landing/popup/{popup_id}")
async def delete_popup_image(popup_id: str, credentials: HTTPBasicCredentials = Depends(security)):
    verify_admin(credentials)
    
    result = await db.landing_config.update_one(
        {"_id": "main"},
        {"$pull": {"popup_images": {"id": popup_id}}}
    )
    return {"message": "Popup eliminado"}

# Toggle popup active status (admin only)
@api_router.patch("/admin/landing/popup/{popup_id}/toggle")
async def toggle_popup(popup_id: str, credentials: HTTPBasicCredentials = Depends(security)):
    verify_admin(credentials)
    
    config = await db.landing_config.find_one({"_id": "main"})
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    popups = config.get("popup_images", [])
    for popup in popups:
        if popup["id"] == popup_id:
            popup["active"] = not popup.get("active", True)
            break
    
    await db.landing_config.update_one(
        {"_id": "main"},
        {"$set": {"popup_images": popups}}
    )
    return {"message": "Estado del popup cambiado"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
