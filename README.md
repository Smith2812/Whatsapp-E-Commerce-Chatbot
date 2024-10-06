# Whatsapp-E-Commerce-Chatbot



This is a Flask-based e-commerce chatbot application that allows users to browse products, check order statuses, and make purchases through a conversational interface using Twilio. The backend integrates with an Oracle database to manage product listings and user sessions.

## Features

- **Product Browsing**: Users can view products by category and get details about individual products.
- **Order Management**: Users can place orders and check the status of their orders.
- **User State Management**: The chatbot remembers the user's current state in the conversation.
- **Twilio Integration**: Utilizes Twilio's messaging API for seamless interaction via SMS.

## Technologies Used

- **Flask**: A micro web framework for Python.
- **OracleDB**: Database management system to store product and order information.
- **Twilio**: Cloud communications platform for sending and receiving SMS messages.
- **UUID**: For generating unique order IDs.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ecommerce-chatbot.git
   cd ecommerce-chatbot
   
2. **Create a Virtual Environment**: <br/>
Set up a virtual environment to manage dependencies:
   ```bash
   python -m venv venv

3. **Activate the Virtual Environment**:
- On Windows
   ```bash
   venv\Scripts\activate
   
- On macOS/Linux
   ```bash
   source venv/bin/activate

4. **Install Required Packages**: <br/>
Install the necessary Python packages <br>
   ```bash
   pip install Flask oracledb twilio
5. **Install Oracle Instant Client** <br/>
- Download the Instant Client: Go to Oracle Instant Client Downloads and download the basic package for your platform.
- Extract the Files: Extract the downloaded ZIP file to a location on your computer. 
- Set the Path: Update the get_db_connection function in the application code to point to the Instant Client directory <br>
  ```bash
  oracledb.init_oracle_client(lib_dir=r"C:\path\to\instantclient")
6. **Install Ngrok**:
- Download Ngrok: Go to ngrok.com and download the appropriate version for your operating system.
- Unzip Ngrok: Extract the downloaded ZIP file to a directory of your choice.
- Add Ngrok to your PATH: (Optional) To use ngrok from any terminal window, add the extracted directory to your system's PATH.
7. **Twilio Setup**:
- Create a Twilio Account: Sign up at Twilio.
- Get a Twilio Phone Number:
- After logging in, navigate to the Phone Numbers section in the Twilio console.
- Click on Get a Number and follow the prompts to purchase a number.
- **Set Up Messaging**
- Click on your purchased phone number in the Phone Numbers section.
- In the Messaging section, locate the A MESSAGE COMES IN field.
- Set the Webhook URL to the Ngrok URL (see Ngrok section below), appending /bot to the end, like so:
   ``` arduino
   https://<ngrok-id>.ngrok.io/bot
- Make sure the HTTP method is set to POST.

## Running the Application

1. **Run the Flask Application**<br>
In the terminal, execute the following command to start the Flask server:<br>
The application will run on http://127.0.0.1:5000.
   ```bash
   python app.py

2. Expose the Application Using Ngrok

- Open a new terminal window and navigate to the directory where you extracted Ngrok.
- Run the following command to expose your Flask application:

  ```bash
   ngrok http 5000
- Ngrok will provide a public URL that tunnels to your local server. Copy this URL for use in your Twilio configuration.

3. Update Twilio Webhook:
- Go back to your Twilio console and update the "Webhook URL" for your phone number with the public URL provided by Ngrok, appending /bot to the end, like so:
   ```bash
   https://<ngrok-id>.ngrok.io/bot

### Interacting with the Chatbot
1. Send a message to your Twilio phone number to initiate the chatbot conversation.
2. Use the options provided by the chatbot to browse products, check order status, or contact support.
### API Endpoints
1. GET /payment/<product_id>: Renders the payment page for a specific product.
2. POST /complete_order: Completes the order and stores the order details in the database.
3. POST /bot: Handles incoming messages from Twilio and manages user interactions.

### Database Schema
#### Products Table Structure

| Column Name | Data Type  |
|-------------|------------|
| id          | VARCHAR2   |
| name        | VARCHAR2   |
| price       | NUMBER     |
| image_url   | VARCHAR2   |
| category    | VARCHAR2   |

#### Order Data Table Structure

| Column Name    | Data Type  |
|----------------|------------|
| id             | VARCHAR2   |
| user_phone     | VARCHAR2   |
| product_id     | VARCHAR2   |
| payment_method | VARCHAR2   |
| address        | VARCHAR2   |
| status         | VARCHAR2   |

#### User Sessions Table Structure

| Column Name | Data Type  |
|-------------|------------|
| phone       | VARCHAR2   |
| state       | VARCHAR2   |



   





  

