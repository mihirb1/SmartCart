# **SmartCart**

SmartCart is a virtual grocery shopping assistant designed to help users find the best prices and value deals on grocery items. It uses advanced web scraping techniques to gather real-time pricing data and makes intelligent recommendations to maximize savings. Additionally, it uses user authentication to ensure data is only accessed by someone with an account.

---

## **Features**
- 🛒 Compare prices across multiple grocery stores.
- 💰 Find the best value deals based on price per unit.
- 📈 Access real-time data through web scraping.
- 🎯 Intuitive interface for seamless grocery shopping assistance.

---

## **Requirements**
SmartCart has the following dependencies, which are listed in the `requirements.txt` file:
- **Flask**: For running the web application.
- **BeautifulSoup4**: For web scraping HTML data.
- **Requests**: For making HTTP requests to fetch data.
- **Pandas**: For handling and analyzing tabular data.
- **Selenium (optional)**: For scraping JavaScript-rendered websites.

To install all required dependencies, run:
```bash
pip install -r requirements.txt
```
# **How to Run**
1. Clone the repository to your local machine:
   git clone https://github.com/your-username/SmartCart.git
   cd SmartCart
2. Install the required dependencies:
   pip install -r requirements.txt
3. Run the Flask application:
   python app.py
4. Open your web browser and go to:
   htpp://localhost:5000

# **Data**
- amazon_products1.csv: Contains all product data gathered through web scraping, including prices, product names, units, and availability.
- Refer to SmartCart1: For details on web scraping logic, review the code in the SmartCart1 directory. It includes implementations using BeautifulSoup and Pandas for extracting and storing data into a SQL database.

# **Contributors**
- Mihir Borkar
- Gaurav Kriplani
- James Donckels

# **License**
This project is licensed under the MIT License. See LICENSE for more details.
