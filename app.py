import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, Response       
import csv
import io

app = Flask(__name__)
app.secret_key = "inventory_secret_key"

DATABASE = "inventory.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            threshold INTEGER NOT NULL,
            price REAL NOT NULL,
            barcode TEXT UNIQUE
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def index():
    search_query = request.args.get("search", "")

    connection = get_db_connection()

    if search_query:
        products = connection.execute("""
            SELECT * FROM products
            WHERE name LIKE ?
               OR category LIKE ?
               OR barcode LIKE ?
        """, (
            f"%{search_query}%",
            f"%{search_query}%",
            f"%{search_query}%"
        )).fetchall()
    else:
        products = connection.execute("SELECT * FROM products").fetchall()

    connection.close()

    return render_template(
        "index.html",
        products=products,
        search_query=search_query
    )


@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form["category"].strip()
        quantity = int(request.form["quantity"])
        threshold = int(request.form["threshold"])
        price = float(request.form["price"])
        barcode = request.form["barcode"].strip()

        if quantity < 0 or threshold < 0 or price < 0:
            flash("Quantity, threshold, and price cannot be negative.", "error")
            return redirect(url_for("add_product"))

        connection = get_db_connection()

        try:
            connection.execute("""
                INSERT INTO products (name, category, quantity, threshold, price, barcode)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, category, quantity, threshold, price, barcode))

            connection.commit()
            flash("Product added successfully.", "success")

        except sqlite3.IntegrityError:
            flash("Barcode already exists. Please use a unique barcode.", "error")

        finally:
            connection.close()

        return redirect(url_for("add_product"))

    return render_template("add_product.html")


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    connection = get_db_connection()
    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        connection.close()
        return "Product not found", 404

    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form["category"].strip()
        quantity = int(request.form["quantity"])
        threshold = int(request.form["threshold"])
        price = float(request.form["price"])
        barcode = request.form["barcode"].strip()

        if quantity < 0 or threshold < 0 or price < 0:
            connection.close()
            flash("Quantity, threshold, and price cannot be negative.", "error")
            return redirect(url_for("edit_product", product_id=product_id))

        try:
            connection.execute("""
                UPDATE products
                SET name = ?, category = ?, quantity = ?, threshold = ?, price = ?, barcode = ?
                WHERE id = ?
            """, (name, category, quantity, threshold, price, barcode, product_id))

            connection.commit()
            flash("Product updated successfully.", "success")

        except sqlite3.IntegrityError:
            flash("Barcode already exists. Please use a unique barcode.", "error")

        finally:
            connection.close()

        return redirect(url_for("index"))

    connection.close()
    return render_template("edit_product.html", product=product)


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    connection = get_db_connection()
    connection.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()
    connection.close()

    flash("Product deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    connection = get_db_connection()

    total_products = connection.execute("""
        SELECT COUNT(*) FROM products
    """).fetchone()[0]

    total_quantity = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0) FROM products
    """).fetchone()[0]

    low_stock_items = connection.execute("""
        SELECT COUNT(*) FROM products
        WHERE quantity > 0 AND quantity < threshold
    """).fetchone()[0]

    out_of_stock_items = connection.execute("""
        SELECT COUNT(*) FROM products
        WHERE quantity = 0
    """).fetchone()[0]

    total_inventory_value = connection.execute("""
        SELECT COALESCE(SUM(quantity * price), 0) FROM products
    """).fetchone()[0]

    low_stock_products = connection.execute("""
        SELECT * FROM products
        WHERE quantity < threshold
        ORDER BY quantity ASC
    """).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_quantity=total_quantity,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        total_inventory_value=total_inventory_value,
        low_stock_products=low_stock_products
    )


@app.route("/barcode", methods=["GET", "POST"])
def barcode_lookup():
    product = None
    searched_barcode = ""

    if request.method == "POST":
        searched_barcode = request.form["barcode"].strip()

        connection = get_db_connection()
        product = connection.execute(
            "SELECT * FROM products WHERE barcode = ?",
            (searched_barcode,)
        ).fetchone()
        connection.close()

    return render_template(
        "barcode.html",
        product=product,
        searched_barcode=searched_barcode
    )

@app.route("/update_stock/<int:product_id>", methods=["POST"])
def update_stock(product_id):
    change_amount = int(request.form["change_amount"])

    connection = get_db_connection()

    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        connection.close()
        flash("Product not found.", "error")
        return redirect(url_for("index"))

    new_quantity = product["quantity"] + change_amount

    if new_quantity < 0:
        connection.close()
        flash("Stock quantity cannot be negative.", "error")
        return redirect(url_for("index"))

    connection.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, product_id)
    )

    connection.commit()
    connection.close()

    flash("Stock quantity updated successfully.", "success")
    return redirect(url_for("index"))

@app.route("/export")
def export_csv():
    connection = get_db_connection()
    products = connection.execute("SELECT * FROM products").fetchall()
    connection.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Product Name",
        "Category",
        "Quantity",
        "Threshold",
        "Price",
        "Barcode",
        "Status"
    ])

    for product in products:
        if product["quantity"] == 0:
            status = "Out of Stock"
        elif product["quantity"] < product["threshold"]:
            status = "Low Stock"
        else:
            status = "In Stock"

        writer.writerow([
            product["id"],
            product["name"],
            product["category"],
            product["quantity"],
            product["threshold"],
            product["price"],
            product["barcode"],
            status
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = "attachment; filename=inventory_report.csv"

    return response

if __name__ == "__main__":
    init_db()
    app.run(debug=True)