"""Customer-facing pages: home, restaurants, menu, cart, orders, reviews, tickets."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from auth_utils import login_required, safe_next
from errors import ServiceError
from services import catalog_service as catalog
from services import order_service as orders
from services import review_service as reviews
from services import support_service as support

bp = Blueprint("shop", __name__)

def resolve_food_image(item_name: str, category_name: str = "") -> str:
    """Accurately maps every food item to its unique, high-resolution Unsplash image.
    Guarantees no duplicate images between items in the same category."""
    n = (item_name or "").lower().strip()
    c = (category_name or "").lower().strip()

    # 1. Seafood & Fish
    if "fish" in n or "seafood" in n or "prawn" in n or c == "seafood":
        return "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500&auto=format&fit=crop&q=60"

    # 2. Desserts (distinct from drinks and each other)
    if "brownie" in n or "lava" in n:
        return "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=60"
    if "gulab" in n or "jamun" in n:
        return "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=60"

    # 2. Biryani & Rice Items (Student vs Beef/Dum vs Chicken)
    if "student" in n or "pulao" in n:
        return "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500&auto=format&fit=crop&q=60"
    if ("beef" in n or "mutton" in n or "dum" in n or "handi" in n) and ("biryani" in n or "rice" in n or c == "biryani"):
        return "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60"
    if "biryani" in n or "rice" in n or c == "biryani":
        return "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=60"

    # 3. Pizzas (distinct styles)
    if "tikka" in n and ("pizza" in n or c == "pizza"):
        return "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&auto=format&fit=crop&q=60"
    if "pepperoni" in n or "fajita" in n:
        return "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=500&auto=format&fit=crop&q=60"
    if "pizza" in n or c == "pizza":
        return "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60"

    # 4. Burgers (Zinger vs Beef/Gourmet vs Chicken)
    if "zinger" in n:
        return "https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?w=500&auto=format&fit=crop&q=60"
    if ("beef" in n or "double" in n or "patty" in n or "smash" in n or "gourmet" in n) and ("burger" in n or c in ("burger", "burgers")):
        return "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60"
    if "burger" in n or c in ("burger", "burgers"):
        return "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60"

    # 5. Drinks (Soda/Can vs Lemonade vs Shake)
    if "milkshake" in n or "shake" in n or "coffee" in n:
        return "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=60"
    if "lemonade" in n or "margarita" in n or "mint" in n or "lime" in n:
        return "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&auto=format&fit=crop&q=60"
    if "soft drink" in n or "soda" in n or "cola" in n or "can" in n or "sprite" in n or "dew" in n or c == "drinks":
        return "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60"

    # 6. Sides & BBQ (Wings vs Fries vs Kabab vs Malai Boti/Tikka)
    if "wing" in n or "nugget" in n:
        return "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60"
    if "fries" in n:
        return "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=60"
    if "reshmi" in n or "kabab" in n or "seekh" in n or "tikka" in n or "boti" in n or "bbq" in n or "malai" in n:
        return "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60"

    if c == "desserts":
        return "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=60"
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60"


PARTNER_KITCHENS = {
    1: {
        "restaurant_id": 1,
        "name": "Spice Garden",
        "address": "Shop 4, Tariq Road",
        "city": "Karachi",
        "phone": "021-34567890",
        "status": "Open",
        "avg_rating": 4.8,
        "review_count": 124,
        "cuisine": "Handi Biryani, Italian Pizza, BBQ & Seafood",
        "banner_image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1000&auto=format&fit=crop&q=80",
        "foods": [
            {
                "food_id": 101,
                "item_name": "Handi Dum Biryani",
                "restaurant_id": 1,
                "restaurant_name": "Spice Garden",
                "category_name": "Biryani",
                "price": 680,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.9,
                "prep_time": "25 min",
                "badge": "Signature Handi 🔥",
                "description": "Slow-cooked saffron dum basmati rice layered with tender marinated meat, baby potatoes, aromatic spices & mint raita.",
                "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 1,
                "item_name": "Chicken Biryani",
                "restaurant_id": 1,
                "restaurant_name": "Spice Garden",
                "category_name": "Biryani",
                "price": 450,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.8,
                "prep_time": "20 min",
                "badge": "Popular",
                "description": "Classic fragrant basmati rice cooked with succulent chicken pieces and spices.",
                "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 2,
                "item_name": "Beef Biryani",
                "restaurant_id": 1,
                "restaurant_name": "Spice Garden",
                "category_name": "Biryani",
                "price": 520,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.8,
                "prep_time": "25 min",
                "badge": "Spicy Veal",
                "description": "Richly spiced Karachi-style beef biryani with tender cuts and golden potatoes.",
                "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 102,
                "item_name": "Classic Italian Pizza",
                "restaurant_id": 1,
                "restaurant_name": "Spice Garden",
                "category_name": "Pizza",
                "price": 1150,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.8,
                "prep_time": "30 min",
                "badge": "Wood-Fired Crust",
                "description": "Thin Italian crust baked over oak embers with rich marinara sauce, fresh buffalo mozzarella, and aromatic basil.",
                "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 103,
                "item_name": "Chicken Seekh Kabab",
                "restaurant_id": 1,
                "restaurant_name": "Spice Garden",
                "category_name": "BBQ & Sides",
                "price": 590,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.9,
                "prep_time": "20 min",
                "badge": "Melt in Mouth",
                "description": "Tender minced chicken skewers char-grilled over open coals with fresh spices and mint chutney.",
                "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 104,
                "item_name": "Crispy Finger Fish",
                "restaurant_id": 1,
                "restaurant_name": "Spice Garden",
                "category_name": "Seafood",
                "price": 650,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.8,
                "prep_time": "20 min",
                "badge": "Golden Crispy 🐟",
                "description": "Golden crispy fried fish fillets served with spicy tartar sauce and lemon wedges.",
                "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 3,
                "item_name": "Soft Drink",
                "restaurant_id": 1,
                "restaurant_name": "Spice Garden",
                "category_name": "Drinks",
                "price": 120,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.7,
                "prep_time": "5 min",
                "badge": "Chilled Can",
                "description": "345ml chilled soft drink served ice-cold.",
                "image_url": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60"
            }
        ],
        "reviews": [
            {"full_name": "Hamza Ali", "rating": 5, "review_date": "2026-11-04", "review_comment": "Handi Dum Biryani was rich, aromatic and authentic. Classic Italian pizza was great too."},
            {"full_name": "Farhan Raza", "rating": 5, "review_date": "2026-11-02", "review_comment": "Melt-in-mouth Chicken Seekh kababs and crispy finger fish. Highly recommended!"}
        ]
    },
    2: {
        "restaurant_id": 2,
        "name": "Food Palace",
        "address": "12 Clifton Block 5",
        "city": "Karachi",
        "phone": "021-35871234",
        "status": "Open",
        "avg_rating": 4.9,
        "review_count": 186,
        "cuisine": "Special Beef Biryani, Gourmet Burgers & Fries",
        "banner_image": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=1000&auto=format&fit=crop&q=80",
        "foods": [
            {
                "food_id": 201,
                "item_name": "Special Beef Biryani",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Biryani",
                "price": 550,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.9,
                "prep_time": "25 min",
                "badge": "Clifton Favorite 🔥",
                "description": "Richly spiced Karachi-style beef biryani cooked with tender prime veal cuts, saffron grains, and mint cucumber raita.",
                "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 202,
                "item_name": "Cheesy Gourmet Burger",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Burger",
                "price": 620,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.8,
                "prep_time": "20 min",
                "badge": "Double Cheese",
                "description": "Thick grilled prime beef patty topped with molten Wisconsin cheddar, caramelized mushrooms, and truffle aioli.",
                "image_url": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 7,
                "item_name": "Chicken Burger",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Burger",
                "price": 450,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.7,
                "prep_time": "15 min",
                "badge": "Classic",
                "description": "Crispy golden chicken fillet burger with crisp iceberg lettuce and creamy mayo.",
                "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 9,
                "item_name": "Spicy Zinger Burger",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Burger",
                "price": 480,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.8,
                "prep_time": "15 min",
                "badge": "Fiery Crunch",
                "description": "Hot and spicy crispy chicken zinger patty with zesty house sauce.",
                "image_url": "https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 5,
                "item_name": "Chicken Pizza",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Pizza",
                "price": 950,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.8,
                "prep_time": "25 min",
                "badge": "Classic Cheese",
                "description": "Medium hand-stretched pizza loaded with seasoned grilled chicken, mozzarella, and herb marinara.",
                "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 6,
                "item_name": "Spicy Chicken Tikka Pizza",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Pizza",
                "price": 1100,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.9,
                "prep_time": "25 min",
                "badge": "Tikka Feast 🍕",
                "description": "Artisan pizza topped with charcoal chicken tikka cubes, onions, spicy peppers, and molten cheese.",
                "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 203,
                "item_name": "Loaded Fries",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Sides",
                "price": 320,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.8,
                "prep_time": "15 min",
                "badge": "Loaded & Crispy",
                "description": "Golden skin-on potato fries loaded with warm liquid cheddar, smoky chicken bits, sliced jalapeños and ranch drizzle.",
                "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 204,
                "item_name": "Mint Lemonade",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Drinks",
                "price": 180,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.9,
                "prep_time": "5 min",
                "badge": "Refreshing 🍃",
                "description": "Hand-blended fresh garden mint leaves, freshly squeezed lime juice, rock salt, and crushed ice.",
                "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 10,
                "item_name": "Soft Drink",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Drinks",
                "price": 110,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.6,
                "prep_time": "5 min",
                "badge": "Chilled Can",
                "description": "345ml ice-cold soft drink can (Cola, Sprite, Fanta).",
                "image_url": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 15,
                "item_name": "Chocolate Brownie",
                "restaurant_id": 2,
                "restaurant_name": "Food Palace",
                "category_name": "Desserts",
                "price": 300,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.9,
                "prep_time": "10 min",
                "badge": "Rich Chocolate 🍫",
                "description": "Warm Belgian chocolate fudge brownie drizzled with hot melted cocoa fudge sauce.",
                "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=60"
            }
        ],
        "reviews": [
            {"full_name": "Tariq Mehmood", "rating": 5, "review_date": "2026-11-05", "review_comment": "The Special Beef Biryani was outstanding! Arrived steaming hot and fragrant."},
            {"full_name": "Ayesha Khan", "rating": 5, "review_date": "2026-11-03", "review_comment": "Best cheesy gourmet burger in Clifton. The molten cheese and loaded fries were top tier."}
        ]
    },
    3: {
        "restaurant_id": 3,
        "name": "Karachi Bites",
        "address": "Plot 9, Gulshan-e-Iqbal",
        "city": "Karachi",
        "phone": "021-34981122",
        "status": "Open",
        "avg_rating": 4.7,
        "review_count": 94,
        "cuisine": "Student Biryani, Crispy Zinger & Malai Boti",
        "banner_image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1000&auto=format&fit=crop&q=80",
        "foods": [
            {
                "food_id": 301,
                "item_name": "Student Chicken Biryani",
                "restaurant_id": 3,
                "restaurant_name": "Karachi Bites",
                "category_name": "Biryani",
                "price": 420,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.8,
                "prep_time": "20 min",
                "badge": "Value Deal ⭐",
                "description": "Authentic Karachi student-style spicy chicken biryani served piping hot with golden roasted potatoes & spicy raita.",
                "image_url": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 302,
                "item_name": "Crispy Zinger Burger",
                "restaurant_id": 3,
                "restaurant_name": "Karachi Bites",
                "category_name": "Burger",
                "price": 480,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.7,
                "prep_time": "15 min",
                "badge": "Hot & Crunchy",
                "description": "Extra large crispy batter-fried chicken thigh fillet with fiery chili seasoning, shredded lettuce & creamy mayo.",
                "image_url": "https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 11,
                "item_name": "Chicken Burger",
                "restaurant_id": 3,
                "restaurant_name": "Karachi Bites",
                "category_name": "Burger",
                "price": 400,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.6,
                "prep_time": "15 min",
                "badge": "Everyday Classic",
                "description": "Classic chicken burger patty with mayo, fresh cucumber and soft toasted sesame bun.",
                "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 13,
                "item_name": "French Fries",
                "restaurant_id": 3,
                "restaurant_name": "Karachi Bites",
                "category_name": "Sides",
                "price": 200,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.7,
                "prep_time": "10 min",
                "badge": "Crispy Salted",
                "description": "Crispy salted potato fries served with ketchup and spicy mayo.",
                "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 14,
                "item_name": "Spicy Chicken Wings",
                "restaurant_id": 3,
                "restaurant_name": "Karachi Bites",
                "category_name": "Sides",
                "price": 550,
                "is_available": 1,
                "is_spicy": 1,
                "rating": 4.8,
                "prep_time": "15 min",
                "badge": "Hot Wings 🔥",
                "description": "Six crispy buffalo wings glazed in spicy garlic peri glaze.",
                "image_url": "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 303,
                "item_name": "Chicken Malai Boti",
                "restaurant_id": 3,
                "restaurant_name": "Karachi Bites",
                "category_name": "Sides",
                "price": 580,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.9,
                "prep_time": "20 min",
                "badge": "BBQ Special",
                "description": "Boneless succulent chicken cubes marinated in fresh clotted cream, white pepper, and mild spices, charcoal-grilled.",
                "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60"
            },
            {
                "food_id": 304,
                "item_name": "Soft Drink 500ml",
                "restaurant_id": 3,
                "restaurant_name": "Karachi Bites",
                "category_name": "Drinks",
                "price": 120,
                "is_available": 1,
                "is_spicy": 0,
                "rating": 4.6,
                "prep_time": "5 min",
                "badge": "Ice Chilled 🧊",
                "description": "Chilled 500ml bottle of your choice (Cola, Sprite, Dew) served ice-cold with fresh lemon slice.",
                "image_url": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60"
            }
        ],
        "reviews": [
            {"full_name": "Bilal Ahmed", "rating": 5, "review_date": "2026-11-04", "review_comment": "Student chicken biryani is absolute value for money. Loved the crispy zinger burger!"},
            {"full_name": "Sara Malik", "rating": 4, "review_date": "2026-11-01", "review_comment": "Chicken malai boti was tender and flavorful. Rapid delivery to Gulshan."}
        ]
    }
}


@bp.route("/")
def index():
    try:
        rests = catalog.list_restaurants()[:3]
        popular = catalog.search_food(limit=8)
    except Exception:
        rests = [v for v in PARTNER_KITCHENS.values()]
        popular = []
    if not rests:
        rests = [v for v in PARTNER_KITCHENS.values()]
    for f in popular:
        if not f.get("image_url"):
            f["image_url"] = resolve_food_image(f.get("item_name"), f.get("category_name"))
    return render_template("index.html", restaurants=rests, popular=popular)


@bp.route("/restaurants")
def restaurants():
    q = request.args.get("q", "")
    try:
        rests = catalog.list_restaurants(q)
    except Exception:
        rests = []
    if not rests:
        rests = [v for v in PARTNER_KITCHENS.values()]
        if q and q.strip():
            sq = q.strip().lower()
            rests = [r for r in rests if sq in r["name"].lower() or sq in r["address"].lower() or sq in r["city"].lower()]
    return render_template("restaurants.html", restaurants=rests, q=q)


@bp.route("/restaurants/<int:rid>")
def restaurant_detail(rid):
    partner = PARTNER_KITCHENS.get(rid)
    try:
        r = catalog.get_restaurant(rid)
        foods = catalog.search_food(restaurant_id=rid, available_only=False, limit=50)
        reviews_list = catalog.restaurant_reviews(rid)
    except Exception:
        r, foods, reviews_list = None, [], []

    if not r and partner:
        r = partner
        foods = partner["foods"]
        reviews_list = partner["reviews"]
    elif r and partner and not foods:
        foods = partner["foods"]
        reviews_list = partner["reviews"]

    if not r:
        flash("Restaurant not found.", "danger")
        return redirect(url_for("shop.restaurants"))

    # Ensure every single food card has its accurate, unique image URL
    for f in foods:
        if not f.get("image_url"):
            f["image_url"] = resolve_food_image(f.get("item_name"), f.get("category_name"))

    return render_template("restaurant_detail.html", r=r, foods=foods, reviews=reviews_list, partner=partner)


@bp.route("/menu")
def menu():
    a = request.args
    try:
        foods = catalog.search_food(q=a.get("q"), category=a.get("category"), restaurant_id=a.get("restaurant") or None,
                                    max_price=a.get("max_price"), spicy=a.get("spicy") == "1",
                                    available_only=a.get("show_all") != "1", limit=60)
        categories = catalog.list_categories()
        restaurants = catalog.list_restaurants()
    except Exception:
        all_partner_foods = []
        for pk in PARTNER_KITCHENS.values():
            all_partner_foods.extend(pk["foods"])
        
        foods = all_partner_foods
        q = (a.get("q") or "").strip().lower()
        if q:
            foods = [f for f in foods if q in f["item_name"].lower() or q in f["description"].lower() or q in f["category_name"].lower()]
        cat = (a.get("category") or "").strip().lower()
        if cat:
            if cat in ("sides", "bbq", "bbq & sides"):
                foods = [f for f in foods if "sides" in f["category_name"].lower() or "bbq" in f["category_name"].lower() or "seafood" in f["category_name"].lower()]
            elif cat == "seafood":
                foods = [f for f in foods if "seafood" in f["category_name"].lower() or "sides" in f["category_name"].lower()]
            else:
                foods = [f for f in foods if cat in f["category_name"].lower()]
        rest = a.get("restaurant")
        if rest:
            try:
                rid = int(rest)
                foods = [f for f in foods if f["restaurant_id"] == rid]
            except ValueError:
                pass
        mp = a.get("max_price")
        if mp:
            try:
                foods = [f for f in foods if f["price"] <= float(mp)]
            except ValueError:
                pass
        if a.get("spicy") == "1":
            foods = [f for f in foods if f.get("is_spicy")]

        categories = [
            {"category_id": 1, "category_name": "Biryani"},
            {"category_id": 2, "category_name": "Burger"},
            {"category_id": 3, "category_name": "Pizza"},
            {"category_id": 4, "category_name": "Sides"},
            {"category_id": 5, "category_name": "Desserts"},
            {"category_id": 6, "category_name": "Drinks"},
            {"category_id": 7, "category_name": "Seafood"}
        ]
        restaurants = [
            {"restaurant_id": 1, "name": "Spice Garden"},
            {"restaurant_id": 2, "name": "Food Palace"},
            {"restaurant_id": 3, "name": "Karachi Bites"}
        ]

    # Ensure every single food card has its accurate, unique image URL
    for f in foods:
        if not f.get("image_url"):
            f["image_url"] = resolve_food_image(f.get("item_name"), f.get("category_name"))

    return render_template("menu.html", foods=foods, categories=categories,
                           restaurants=restaurants, f=a)


# ------------------------------------------------------------- cart
def _cart():
    return dict(session.get("cart", {}))


@bp.route("/cart")
@login_required
def cart():
    lines, total = [], 0
    for fid, qty in _cart().items():
        food = None
        try:
            food = catalog.get_food(fid)
        except Exception:
            pass
        if not food:
            for pk in PARTNER_KITCHENS.values():
                for dish in pk["foods"]:
                    if str(dish["food_id"]) == str(fid):
                        food = dish
                        break
                if food:
                    break
        if food:
            line = food["price"] * qty
            total += line
            lines.append({"food": food, "qty": qty, "line": line})
    from services import customer_service
    cust = None
    try:
        cust = customer_service.get_customer(session["customer_id"])
    except Exception:
        cust = {"city": "Karachi", "full_name": session.get("customer_name", "Customer")}
    return render_template("cart.html", lines=lines, total=total, methods=orders.PAYMENT_METHODS,
                           customer=cust)


@bp.post("/cart/add")
@login_required
def cart_add():
    back = safe_next(url_for("shop.menu"))
    try:
        qty = int(request.form.get("qty", 1))
        food = catalog.get_food(request.form.get("food_id"))
    except (TypeError, ValueError):
        flash("Invalid item.", "danger")
        return redirect(back)
    if not food:
        flash("That food item does not exist.", "danger")
    elif not food["is_available"] or food["restaurant_status"] != "Open":
        flash(f"{food['item_name']} is currently unavailable.", "warning")
    elif not 1 <= qty <= 20:
        flash("Quantity must be between 1 and 20.", "danger")
    else:
        cart = _cart()
        other = next((catalog.get_food(k) for k in cart if str(k) != str(food["food_id"])), None)
        if other and other["restaurant_id"] != food["restaurant_id"]:
            flash(f"Your cart has items from {other['restaurant_name']}. Clear the cart to order from "
                  f"{food['restaurant_name']}.", "warning")
        else:
            key = str(food["food_id"])
            cart[key] = min(20, cart.get(key, 0) + qty)
            session["cart"] = cart
            flash(f"Added {food['item_name']} to your cart.", "success")
    return redirect(back)


@bp.post("/cart/update")
@login_required
def cart_update():
    cart, key = _cart(), request.form.get("food_id", "")
    try:
        qty = int(request.form.get("qty", 0))
    except ValueError:
        qty = -1
    if key in cart:
        if qty <= 0:
            cart.pop(key)
        elif qty <= 20:
            cart[key] = qty
        else:
            flash("Quantity must be between 1 and 20.", "danger")
    session["cart"] = cart
    return redirect(url_for("shop.cart"))


@bp.post("/cart/clear")
@login_required
def cart_clear():
    session.pop("cart", None)
    return redirect(url_for("shop.cart"))


@bp.post("/checkout")
@login_required
def checkout():
    try:
        oid = orders.place_order(session["customer_id"], _cart(), request.form.get("address"),
                                 request.form.get("method"))
    except ServiceError as e:
        flash(str(e), "danger")
        return redirect(url_for("shop.cart"))
    session.pop("cart", None)
    flash(f"Order #{oid} placed successfully.", "success")
    return redirect(url_for("shop.order_detail", oid=oid))


# ------------------------------------------------------------- orders
@bp.route("/orders")
@login_required
def my_orders():
    q, st = request.args.get("q", ""), request.args.get("status", "")
    return render_template("orders.html", orders=orders.get_orders(session["customer_id"], st, q),
                           q=q, status=st, statuses=orders.ORDER_STATUSES)


@bp.route("/order/<int:oid>")
@login_required
def order_detail(oid):
    o = orders.get_order(oid, session["customer_id"])   # ownership enforced in SQL
    if not o:
        flash("Order not found.", "danger")
        return redirect(url_for("shop.my_orders"))
    return render_template("order_details.html", o=o, cancellable=o["order_status"] in orders.CANCELLABLE)


@bp.post("/order/<int:oid>/cancel")
@login_required
def order_cancel(oid):
    try:
        orders.cancel_order(session["customer_id"], oid)
        flash(f"Order #{oid} has been cancelled.", "success")
    except ServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("shop.order_detail", oid=oid))


# ------------------------------------------------------------- reviews & tickets
@bp.route("/reviews", methods=["GET", "POST"])
@login_required
def my_reviews():
    cid = session["customer_id"]
    if request.method == "POST":
        try:
            reviews.add_review(cid, request.form.get("restaurant_id"), request.form.get("rating"),
                               request.form.get("comment"))
            flash("Thanks for your review!", "success")
            return redirect(url_for("shop.my_reviews"))
        except ServiceError as e:
            flash(str(e), "danger")
    return render_template("reviews.html", reviews=reviews.customer_reviews(cid),
                           eligible=reviews.eligible_restaurants(cid))


@bp.route("/tickets", methods=["GET", "POST"])
@login_required
def tickets():
    cid = session["customer_id"]
    if request.method == "POST":
        try:
            tid = support.create_ticket(cid, request.form.get("order_id") or None,
                                        request.form.get("issue_type"), request.form.get("description"))
            flash(f"Support ticket #{tid} created.", "success")
            return redirect(url_for("shop.tickets"))
        except ServiceError as e:
            flash(str(e), "danger")
    return render_template("tickets.html", tickets=support.customer_tickets(cid), types=support.ISSUE_TYPES,
                           orders=orders.get_orders(cid))
