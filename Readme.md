# Smart Inventory Management System

my id - 230103143

## Project Description

Smart Inventory Management System is a web-based inventory management application designed for small businesses. The system helps users track products, manage stock quantities, identify low-stock items, and generate inventory reports.

The main goal of this project is to reduce manual inventory tracking errors and help managers make faster restocking decisions.

## Deployed Project URL

https://smart-inventory-system-eqf2.onrender.com/login

## GitHub Repository

https://github.com/greysmirtsea/smart-inventory-system

## Main Features

- User registration and login
- Add new products
- View all products in inventory
- Edit product information
- Delete products
- Search products by name, category, or barcode
- Automatic stock status detection
- Low-stock and out-of-stock alerts
- Dashboard with inventory analytics
- Barcode input simulation
- Stock quantity update simulation
- Export inventory data to CSV
- Basic validation and error handling

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- Jinja Templates
- Gunicorn
- Render for deployment
- GitHub for version control

## System Architecture

The project follows a simple web application architecture:

User Interface → Flask Backend → SQLite Database → Response displayed in browser

- `app.py` contains the backend logic and routes.
- `templates/` contains HTML pages.
- `static/style.css` contains the design and styling.
- `inventory.db` stores product and user data.
- `requirements.txt` contains project dependencies.
- `Procfile` is used for deployment.

## Database Tables

### products

The products table stores inventory data:

- id
- name
- category
- quantity
- threshold
- price
- barcode

### users

The users table stores registered users:

- id
- username
- password

Passwords are stored using password hashing.

## Stock Status Logic

The system automatically checks product quantity and displays the correct status:

- If quantity is 0, the status is Out of Stock.
- If quantity is below the threshold, the status is Low Stock.
- If quantity is equal to or above the threshold, the status is In Stock.

## Demo Login Credentials

Username: admin  
Password: admin123

## How to Run Locally

1. Clone the repository:

```bash
git clone https://github.com/greysmirtsea/smart-inventory-system.git
