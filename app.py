import oracledb
import uuid
from flask import Flask, request, render_template, session
from twilio.twiml.messaging_response import MessagingResponse, Message

app = Flask(__name__)


def get_db_connection():
    oracledb.init_oracle_client(lib_dir=r"C:\instantclient-basic-windows.x64-21.8.0.0.0dbru\instantclient_21_8")
    conn = oracledb.connect("system/Sm28@LAPTOP-RMR5K4N4:1522/xe")
    print("Connected to Oracle DB")
    return conn


def get_products_by_category(category):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, image_url FROM products WHERE category = :category", {"category": category})
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products


def get_product_by_id(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, price, description, image_url FROM products WHERE id = :product_id", {"product_id": product_id})
    product = cur.fetchone()
    cur.close()
    conn.close()
    return product

def get_category_by_id(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT category FROM products WHERE id = :product_id", {"product_id": product_id})
    category = cur.fetchone()
    cur.close()
    conn.close()

    return category[0] if category else "not found"


def get_user_state(phone):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT state FROM user_sessions WHERE phone = :phone", {"phone": phone})
    state = cur.fetchone()
    cur.close()
    conn.close()
    return state[0] if state else "main_menu"


def set_user_state(phone, state):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        MERGE INTO user_sessions us
        USING (SELECT :phone AS phone, :state AS state FROM dual) src
        ON (us.phone = src.phone)
        WHEN MATCHED THEN
            UPDATE SET us.state = src.state
        WHEN NOT MATCHED THEN
            INSERT (phone, state) VALUES (src.phone, src.state)
    """, {"phone": phone, "state": state})
    conn.commit()
    cur.close()
    conn.close()


def get_order_status(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT status FROM order_data WHERE id = :order_id", {"order_id": order_id})
        status = cur.fetchone()
        cur.close()
        conn.close()
        return status[0] if status else "Order not found"
    except Exception as e:
        cur.close()
        conn.close()
        return f"An error occurred: {str(e)}"


@app.route("/complete_order", methods=["GET", "POST"])
def complete_order():
    product_id = request.form.get("product_id")
    payment_method = request.form.get("payment_method")
    address = request.form.get("address")
    user_phone = request.form.get("user_phone")  

    id = str(uuid.uuid4())  
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO order_data (id, user_phone, product_id, payment_method, address, status)
            VALUES (:id, :user_phone, :product_id, :payment_method, :address, 'Pending')
        """, {
            "id": id,
            "user_phone": user_phone,
            "product_id": product_id,
            "payment_method": payment_method,
            "address": address
        })
        conn.commit()
        cur.close()
        conn.close()
        return f"Thank you! Your order has been placed successfully. Your order ID is {id}.", 200
    
    except Exception as e:
        cur.close()
        conn.close()
        return f"An error occurred while processing your order: {str(e)}", 500


@app.route("/payment/<int:product_id>", methods=["GET", "POST"])
def payment_page(product_id):
    product = get_product_by_id(product_id)
    user_phone = session.get('user_phone')  
    
    if product:
        name, price, description, image_url = product
        return render_template("index.html", name=name, price=price, description=description, image_url=image_url, product_id=product_id, user_phone=user_phone)
    else:
        return "Product not found", 404

@app.route("/bot", methods=["POST"])
def bot():
    user_phone = request.values.get("From")
    incoming_msg = request.values.get("Body", "").strip().lower()

    
    user_state = get_user_state(user_phone)

    response = MessagingResponse()
    msg = response.message()

    
    if user_state == "main_menu":
        if "hi" in incoming_msg or "hello" in incoming_msg:
            msg.body("Hi there! 🌟 I’m your e-commerce assistant. How can I help you today?\n\n1. View Categories\n2. Check Order Status\n3. Contact Support\n\nReply with the option number.")
        elif "1" in incoming_msg or "view products" in incoming_msg:
            msg.body("Great choice! Here are our product categories:")
            user_state = "view_categories"
            category_msg = Message()
            category_msg.body("1. Electronics\n2. Accessories")
            response.append(category_msg)
            if "back" in incoming_msg:
                user_state = "main_menu"
                msg.body("Taking you back to the main menu.\n\n1. View Products\n2. Check Order Status\n3. Contact Support\n\nReply with the option number.")

        elif "2" in incoming_msg or "check order" in incoming_msg:
            msg.body("Please provide your Order ID.\nType 'back' to return to the main menu.")
            user_state = "order_status"
        elif "3" in incoming_msg or "contact support" in incoming_msg:
            msg.body("You can reach our support team at:\n📧 smitgondaliya03@gmail.com\n📞 +919265690030")
        else:
            msg.body("Sorry, I didn’t understand that.\n\n Please reply with:\n1. View Products\n2. Check Order Status\n3. Contact Support")

   
    elif user_state == "view_categories":
        if incoming_msg == "1":
            msg.body("Here are our Electronics products:")
            user_state = "view_products_electronics"
            products = get_products_by_category("Electronics")
            for id, name, price, image_url in products:
                product_msg = Message()
                product_msg.media(image_url)
                product_msg.body(f"{id}. {name} - {price}\nType '{id}' for more details.")
                response.append(product_msg)
            msg.body("\nType 'back' to return to categories.")


        elif incoming_msg == "2":
            msg.body("Here are our Accessories products:")
            user_state = "view_products_accessories"
            products = get_products_by_category("Accessories")
            for id, name, price, image_url in products:
                product_msg = Message()
                product_msg.media(image_url)
                product_msg.body(f"{id}. {name} - {price}\nType '{id}' for more details.")
                response.append(product_msg)
            msg.body("\nType 'back' to return to categories.")
        
        elif "back" in incoming_msg:
            user_state="main_menu"
            msg.body("Taking you back to the main menu.\n\n1. View Products\n2. Check Order Status\n3. Contact Support\n\nReply with the option number.")
           
        else:
            msg.body("Sorry, I didn’t understand that. \n\nPlease reply with the category number.")

    
    elif user_state.startswith("view_products_"):
        if incoming_msg.isdigit():
            product_id = int(incoming_msg)
            product = get_product_by_id(product_id)
            category = get_category_by_id(product_id)
            if product:
                name, price, description, image_url = product
                product_msg = Message()
                product_msg.media(image_url)
                product_msg.body(f"**{name}**\nPrice: {price}\nWould you like to:\n1. View Product Details\n2. Buy This Product")
                response.append(product_msg)
                user_state = f"product_detail_{product_id}"
                msg.body(f"\nType 'back' to return to {category} category.")
            else:
                msg.body("Invalid product ID. Please select a valid product ID.")
        elif "back" in incoming_msg:
                user_state = "view_categories"
                
                msg.body("1. Electronics\n2. Accessories")
                
        else:
            msg.body("Sorry, I didn’t understand that. Please reply with the product number for more details.")

   
    elif user_state.startswith("product_detail_"):
        product_id = int(user_state.split("_")[-1])
        product = get_product_by_id(product_id)
        category=get_category_by_id(product_id)

        if product:
            name, price, description, image_url = product
            if incoming_msg == "1":  
                
                msg.body(f"Product Name: {name}\nDescription: {description}")
                
            elif incoming_msg == "2":  
                msg.body(f"Click the link below to proceed to payment for {name}:\n{request.url_root}payment/{product_id}")
            elif incoming_msg == "back":
                user_state = f"view_products_{category}"
                msg.body(f"Here are our {category} products:")
               
                products = get_products_by_category(category)
                for id, name, price, image_url in products:
                    product_msg = Message()
                    product_msg.media(image_url)
                    product_msg.body(f"{id}. {name} - {price}\nType '{id}' for more details.")
                    response.append(product_msg)
                msg.body(f"\nType 'back' to return to categories.")

            else:
                msg.body("Sorry, I didn’t understand that. Please reply with '1' to view product details, '2' to buy, or 'back' to return.")

   
    elif user_state == "order_status":
        if "back" in incoming_msg:
            user_state = "main_menu"
            msg.body("Taking you back to the main menu.\n\n1. View Products\n2. Check Order Status\n3. Contact Support\n\nReply with the option number.")

        order_id = incoming_msg.split()[-1]
        status = get_order_status(order_id)
        if status and order_id!="back":
            msg.body(f"Your order status for ID {order_id} is: {status}\n\nType 'back' to return to the main menu.")
            

   
    set_user_state(user_phone, user_state)
    return str(response)


if __name__ == "__main__":
    app.run(port=5000)
