# 🌊 IRAI Fishery Business Management System

## 📌 Overview

**IRAI** is a comprehensive business management system tailored for fishery companies. Built with **Python** and **Django**, it streamlines operational and financial workflows — from tracking fish catches and managing payments to handling royalties and expenses.

The platform includes role-based access and is designed to improve transparency, efficiency, and accountability across the business.

---

## 🚀 Key Features

- 🧑‍✈️ Manage fishermen and log daily catch records  
- 🐟 Track fish catches and auto-calculate payments based on weight and prices  
- 💸 Handle advance payments and catch settlements  
- 👑 Manage royalty fishermen and calculate royalty payouts  
- 🧾 Record miscellaneous business expenses  
- 📊 Access detailed summaries:
  - Unpaid catches  
  - Payment histories  
  - Transaction reports  
- 🛠️ Edit fish prices and royalty values as needed  
- 🔐 Role-based secure access for:
  - Owners  
  - Managers  
  - Fishermen  

---

## 🧱 Core Entities

| Entity               | Description |
|----------------------|-------------|
| **Fishermen**         | Track catch records and payments for individual fishermen. |
| **Fish**              | Different species with associated prices and royalty rates. |
| **Catches**           | Daily records of fish caught, including weight and payment status. |
| **Payments**          | Advance and catch-related payments made to fishermen. |
| **Royalty Fishermen** | Special group earning royalty payments based on total catches. |
| **Managers**          | Oversee finances, approve expenses, and manage balances. |
| **Owners**            | Top-level users who can allocate funds and monitor transactions. |
| **Expenses**          | Miscellaneous costs tracked and attributed to users or roles. |

---

## 🛠️ Tech Stack

- 🐍 **Python 3**
- 🌐 **Django Web Framework**
- 🗄️ **SQLite** (default database)
- 🎨 **HTML/CSS** for frontend templates and UI

---

## 🎯 Benefits to the Business

With IRAI, fishery operations can:

- ✅ Automate catch logging and financial calculations  
- ✅ Track advances, royalties, and deductions with transparency  
- ✅ Maintain detailed and auditable financial records  
- ✅ Reduce manual errors and administrative workload  
- ✅ Generate reports and summaries for decision-making  
- ✅ Control access with role-specific views and permissions  

---

## 🧪 Getting Started

Follow the steps below to set up and run the project locally:

```bash
# Clone the repository
git clone https://github.com/your-username/irai-fishery.git
cd irai-fishery

# Create and activate a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Now open your browser and go to:

```
http://localhost:8000/
```

To access the Django admin panel:

```
http://localhost:8000/admin/
```

---

## 📚 Documentation

This README provides a high-level overview. For advanced usage, deployment, and customization, please refer to the full project documentation or explore the source code.

---

## 🐠 Happy fishing with IRAI!
