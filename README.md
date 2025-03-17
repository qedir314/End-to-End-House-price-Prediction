# House Price Prediction

## 📌 Project Overview
This project is an **end-to-end house price prediction system** for real estate in **Azerbaijan**. It involves **data collection, preprocessing, machine learning modeling, and deployment** on a web application.

## 📂 Folder Structure
```
📾 House-Price-Prediction
👇 Data/                # Processed dataset
👇 Deployment/          # Deployment files
👇 Models/              # Trained machine learning models
👇 Notebooks/           # Jupyter notebooks for EDA and model training
👇 Web-Scraping/        # Web scraper for collecting house data
👇 requirements.txt        # Required Python packages
👇 README.md               # Project documentation
```

## 🚀 Features
- **Web Scraper:** Uses BeautifulSoup & Selenium to collect house listing data.
- **Data Preprocessing:** Categorical encoding and feature scaling.
- **Machine Learning Model:** Uses regression models (Random Forest, XGBoost, etc.) to predict house prices.
- **Web Application:** A Flask-based web app with a frontend to input house details and get price predictions.
- **Deployment:** Hosted on **Heroku**: [House Price Prediction App](https://house-prediction-app-3032a14def7e.herokuapp.com/)

## 📊 Data Collection
The dataset consists of **~50k house listings** with the following features:
- `Item_id`: Unique house identifier
- `Location`: District and village name
- `room_size`: Number of rooms
- `area`: Total area (m²)
- `current_floor`: House floor (if in a building)
- `total_floor`: Total floors in the building
- `building_type`: New or old building
- `repair_status`: Whether the house is repaired
- `bill_of_sale`: Whether the house has proper documentation
- `price (AZN)`: House price in Azerbaijani Manat

## ⚙️ Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/House-Price-Prediction.git
   cd House-Price-Prediction
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🔥 Usage
### **1️⃣ Running the Web Scraper**
```bash
python Web-Scraping/WebScraper.py
```
This will collect fresh real estate data and save it in the `Data/` folder.

### **2️⃣ Training the Model**
```bash
python Models/model_training.py
```
Trains the machine learning model and saves it in the `Models/` folder.

### **3️⃣ Running the Web App**
```bash
python Deployment/app.py
```
The app will be available at `http://localhost:5000/`.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Acknowledgments
- **BeautifulSoup & Selenium** for web scraping
- **Scikit-learn, XGBoost** for machine learning
- **Flask/Django** for web development

---
💡 **Developed by Qedir** | GitHub: [qedir314](https://github.com/qedir314)

