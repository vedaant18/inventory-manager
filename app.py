import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


app = Flask(__name__)
database_url = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///inventory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Development-only secret key for flashing messages
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

db = SQLAlchemy(app)


class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True, nullable=False)
	quantity = db.Column(db.Integer, nullable=False, default=0)
	unit = db.Column(db.String(32), nullable=False, default="nos")
	category = db.Column(db.String(64), nullable=False, default="Burger")
	reorder_level = db.Column(db.Integer, nullable=False, default=10)
	created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
	updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

	@property
	def is_low_stock(self):
		return self.quantity <= self.reorder_level

	def __repr__(self) -> str:
		return f"<Item id={self.id} name={self.name!r} qty={self.quantity} {self.unit}>"


class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	order_type = db.Column(db.String(64), nullable=False)  # "burger", "fries", "drink", "meal"
	customizations = db.Column(db.String(500), nullable=True)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self) -> str:
		return f"<Order id={self.id} type={self.order_type}>"


# Predefined items for burger restaurant
PREDEFINED_ITEMS = [
	# Burger components (in nos - pieces)
	{"name": "Buns", "unit": "nos", "category": "Burger", "reorder_level": 50},
	{"name": "Lettuce", "unit": "nos", "category": "Burger", "reorder_level": 30},
	{"name": "Tomatoes", "unit": "nos", "category": "Burger", "reorder_level": 30},
	{"name": "Onion", "unit": "nos", "category": "Burger", "reorder_level": 30},
	{"name": "Patty", "unit": "nos", "category": "Burger", "reorder_level": 50},
	{"name": "Cheese", "unit": "nos", "category": "Burger", "reorder_level": 40},
	{"name": "Tomato Sauce", "unit": "nos", "category": "Burger", "reorder_level": 20},
	
	# Fries (in kg)
	{"name": "Potato Fries", "unit": "kg", "category": "Fries", "reorder_level": 10},
	
	# Soft drinks (in bottles)
	{"name": "Cola", "unit": "bottles", "category": "Soft Drinks", "reorder_level": 24},
	{"name": "Lemon Lime", "unit": "bottles", "category": "Soft Drinks", "reorder_level": 24},
	{"name": "Orange", "unit": "bottles", "category": "Soft Drinks", "reorder_level": 24},
	{"name": "Mango", "unit": "bottles", "category": "Soft Drinks", "reorder_level": 24},
]

# Standard burger recipe
STANDARD_BURGER = {
	"Buns": 1,
	"Lettuce": 1,
	"Tomatoes": 1,
	"Onion": 1,
	"Patty": 1,
	"Tomato Sauce": 1,
}

# Items that can be opted out (vegetables)
OPTIONAL_ITEMS = ["Lettuce", "Tomatoes", "Onion"]

# Items that can be added extra
EXTRA_ITEMS = {
	"Cheese": 1,
	"Patty": 1,
}

# Fries conversion: 1 set = 200g, so 5 sets = 1 kg
FRIES_SETS_PER_KG = 5

# Meal definitions (fries in sets, not kg)
MEALS = {
	"Basic Meal": {
		"burger": 1,
		"fries_sets": 1,  # 1 set (200g) = 0.2 kg
		"drink": 1
	},
	"Deluxe Meal": {
		"burger": 1,
		"fries_sets": 2,  # 2 sets (400g) = 0.4 kg
		"drink": 2
	},
	"Family Meal": {
		"burger": 4,
		"fries_sets": 4,  # 4 sets (800g) = 0.8 kg
		"drink": 4
	}
}


def initialize_database() -> None:
	# Create tables if they don't exist (Flask 3.x compatible)
	with app.app_context():
		db.create_all()
		
		# Add predefined items if database is empty
		if Item.query.count() == 0:
			for item_data in PREDEFINED_ITEMS:
				item = Item(**item_data, quantity=10)
				db.session.add(item)
			db.session.commit()
			print("✅ Initialized database with predefined burger restaurant items!")
		
		# Update existing items to have 10 units if they have 0
		items_to_update = Item.query.filter_by(quantity=0).all()
		if items_to_update:
			for item in items_to_update:
				item.quantity = 10
			db.session.commit()
			print(f"✅ Updated {len(items_to_update)} items to have 10 units each!")


def check_and_deduct_inventory(items_needed):
	"""Check if items are available and deduct from inventory"""
	# First check if all items are available
	for item_name, qty_needed in items_needed.items():
		item = Item.query.filter_by(name=item_name).first()
		if not item:
			return False, f"Item '{item_name}' not found in inventory"
		if item.quantity < qty_needed:
			return False, f"Not enough {item_name}. Need {qty_needed}, have {item.quantity}"
	
	# All items available, deduct them
	for item_name, qty_needed in items_needed.items():
		item = Item.query.filter_by(name=item_name).first()
		item.quantity -= qty_needed
	
	db.session.commit()
	return True, "Order completed successfully"


# Routes
@app.get("/")
def index():
	return redirect(url_for("inventory"))


@app.get("/inventory")
def inventory():
	category_filter = request.args.get("category")
	if category_filter and category_filter != "All":
		items = Item.query.filter_by(category=category_filter).order_by(Item.name.asc()).all()
	else:
		items = Item.query.order_by(Item.category.asc(), Item.name.asc()).all()
	
	# Get all unique categories for filter dropdown
	categories = db.session.query(Item.category).distinct().order_by(Item.category).all()
	categories = [cat[0] for cat in categories]
	
	# Calculate statistics
	total_items = Item.query.count()
	low_stock_items = [item for item in Item.query.all() if item.is_low_stock]
	
	return render_template("inventory.html", 
		items=items, 
		categories=categories,
		selected_category=category_filter or "All",
		total_items=total_items,
		low_stock_count=len(low_stock_items))


@app.get("/add-stock")
def add_stock_page():
	all_items = Item.query.order_by(Item.category.asc(), Item.name.asc()).all()
	return render_template("add_stock.html", all_items=all_items)


@app.post("/add-stock")
def add_stock():
	item_name = (request.form.get("item_name") or "").strip()
	quantity_raw = (request.form.get("quantity") or "0").strip()
	
	if not item_name:
		flash("Please select an item.", "error")
		return redirect(url_for("add_stock_page"))
	
	try:
		quantity = int(quantity_raw)
		if quantity <= 0:
			raise ValueError()
	except ValueError:
		flash("Quantity must be a positive whole number.", "error")
		return redirect(url_for("add_stock_page"))
	
	item = Item.query.filter_by(name=item_name).first()
	if not item:
		flash(f"Item '{item_name}' not found.", "error")
		return redirect(url_for("add_stock_page"))
	
	item.quantity += quantity
	db.session.commit()
	flash(f"✅ Added {quantity} {item.unit} to '{item.name}'. New total: {item.quantity}", "success")
	return redirect(url_for("add_stock_page"))


@app.get("/orders")
def orders_page():
	drinks = Item.query.filter_by(category="Soft Drinks").all()
	return render_template("orders.html", 
		optional_items=OPTIONAL_ITEMS,
		extra_items=EXTRA_ITEMS,
		meals=MEALS,
		drinks=drinks)


@app.post("/orders/burger")
def order_burger():
	# Start with standard burger recipe
	items_needed = STANDARD_BURGER.copy()
	customization_details = []
	
	# Handle opt-outs (vegetables)
	for item in OPTIONAL_ITEMS:
		if not request.form.get(f"include_{item.lower().replace(' ', '_')}"):
			items_needed[item] = 0
			customization_details.append(f"No {item}")
	
	# Handle extras
	for item, base_qty in EXTRA_ITEMS.items():
		extra_count = int(request.form.get(f"extra_{item.lower()}", 0))
		if extra_count > 0:
			items_needed[item] = items_needed.get(item, 0) + (base_qty * extra_count)
			customization_details.append(f"Extra {item} x{extra_count}")
	
	# Remove items with 0 quantity
	items_needed = {k: v for k, v in items_needed.items() if v > 0}
	
	# Check and deduct inventory
	success, message = check_and_deduct_inventory(items_needed)
	
	if success:
		# Record order
		order = Order(
			order_type="burger",
			customizations=", ".join(customization_details) if customization_details else "Standard"
		)
		db.session.add(order)
		db.session.commit()
		flash(f"✅ Burger order completed! {message}", "success")
	else:
		flash(f"❌ Order failed: {message}", "error")
	
	return redirect(url_for("orders_page"))


@app.post("/orders/fries")
def order_fries():
	sets = int(request.form.get("quantity", 1))
	
	# Calculate kg needed from inventory (5 sets = 1 kg)
	kg_needed = sets / FRIES_SETS_PER_KG
	
	# Check if we have enough kg in inventory
	potato_fries = Item.query.filter_by(name="Potato Fries").first()
	if not potato_fries or potato_fries.quantity < kg_needed:
		available_sets = int(potato_fries.quantity * FRIES_SETS_PER_KG) if potato_fries else 0
		flash(f"❌ Not enough fries! Need {sets} sets ({kg_needed:.1f} kg), but only have {available_sets} sets ({potato_fries.quantity if potato_fries else 0} kg) available.", "error")
		return redirect(url_for("orders_page"))
	
	# Deduct from inventory
	potato_fries.quantity -= int(kg_needed)
	db.session.commit()
	
	order = Order(order_type="fries", customizations=f"{sets} sets ({kg_needed:.1f} kg)")
	db.session.add(order)
	db.session.commit()
	flash(f"✅ Fries order completed! {sets} sets ({kg_needed:.1f} kg deducted from inventory)", "success")
	
	return redirect(url_for("orders_page"))


@app.post("/orders/drink")
def order_drink():
	drink_name = request.form.get("drink_name")
	quantity = int(request.form.get("quantity", 1))
	
	if not drink_name:
		flash("Please select a drink.", "error")
		return redirect(url_for("orders_page"))
	
	items_needed = {drink_name: quantity}
	success, message = check_and_deduct_inventory(items_needed)
	
	if success:
		order = Order(order_type="drink", customizations=f"{drink_name} x{quantity}")
		db.session.add(order)
		db.session.commit()
		flash(f"✅ Drink order completed! {drink_name} x{quantity}", "success")
	else:
		flash(f"❌ Order failed: {message}", "error")
	
	return redirect(url_for("orders_page"))


@app.post("/orders/meal")
def order_meal():
	meal_type = request.form.get("meal_type")
	drink_name = request.form.get("meal_drink")
	meal_quantity = int(request.form.get("meal_quantity", 1))
	
	if not meal_type or meal_type not in MEALS:
		flash("Please select a valid meal.", "error")
		return redirect(url_for("orders_page"))
	
	if not drink_name:
		flash("Please select a drink for the meal.", "error")
		return redirect(url_for("orders_page"))
	
	if meal_quantity < 1:
		flash("Meal quantity must be at least 1.", "error")
		return redirect(url_for("orders_page"))
	
	meal = MEALS[meal_type]
	items_needed = {}
	
	# Calculate burger ingredients (multiplied by meal quantity)
	burger_count = meal["burger"] * meal_quantity
	for item, qty in STANDARD_BURGER.items():
		items_needed[item] = qty * burger_count
	
	# Calculate fries kg needed (sets / 5, multiplied by meal quantity)
	fries_sets = meal["fries_sets"] * meal_quantity
	kg_needed = fries_sets / FRIES_SETS_PER_KG
	items_needed["Potato Fries"] = kg_needed
	
	# Add drinks (multiplied by meal quantity)
	items_needed[drink_name] = meal["drink"] * meal_quantity
	
	success, message = check_and_deduct_inventory(items_needed)
	
	if success:
		order = Order(
			order_type="meal",
			customizations=f"{meal_quantity}x {meal_type} with {drink_name}"
		)
		db.session.add(order)
		db.session.commit()
		flash(f"✅ {meal_quantity}x {meal_type} completed! Total: {burger_count} burger(s), {fries_sets} fries set(s) ({kg_needed:.1f} kg), {meal['drink'] * meal_quantity} drink(s)", "success")
	else:
		flash(f"❌ Order failed: {message}", "error")
	
	return redirect(url_for("orders_page"))


if __name__ == "__main__":
	initialize_database()
	app.run(debug=True)
