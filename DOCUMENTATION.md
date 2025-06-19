# IRAI Fishery Business Management System - Full Documentation

## 1. Project Overview
IRAI is a Django-based business management system designed to streamline the operations of a fishery company. It manages fishermen, fish catches, payments, advances, royalties, managers, owners, and miscellaneous expenses. The system automates financial transactions, catch logging, and reporting to improve operational efficiency and transparency.

## 2. Installation and Setup

### Prerequisites
- Python 3.x
- Django (version as per requirements.txt)
- SQLite (default database)

### Setup Steps
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd IRAI/mySite
   ```
3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # Linux/Mac
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Apply database migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser for admin access:
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```
8. Access the application at:
   ```
   http://localhost:8000/
   ```

## 3. Data Models Explanation

### Owner
- Represents the business owner.
- Linked to Django User model.

### Manager
- Represents managers who handle financial transactions.
- Has a balance field to track available funds.

### OwnerToManagerTransaction
- Records transactions where owners transfer money to managers.

### Fish
- Represents types of fish.
- Stores price and royalty amount per fish.

### Fisherman
- Represents fishermen who catch fish.
- Tracks phone number and related catches.

### Catch
- Records fish caught by fishermen.
- Includes catch date, weight, and payment status.

### Advance
- Records advances given to fishermen.
- Includes amount, reason, date, and manager who authorized.

### Payment
- Records payments made to fishermen for catches or advances.
- Linked to manager who processed the payment.

### RoyaltyFisherman
- Represents fishermen who receive royalties.

### CatchRoyalty
- Records catches for royalty fishermen.
- Automatically creates PaymentRoyalty records on save.

### PaymentRoyalty
- Records royalty payments due to royalty fishermen.

### PaymentRoyaltyReceived
- Records royalty payments received by royalty fishermen.

### MiscellaneousExpense
- Records various expenses made by users.
- Deducts amount from manager balance if spender is a manager.

## 4. Features and Usage

### Home Page
- Landing page of the application.

### Payment Summary
- View summary of payments due and paid for fishermen.

### Unpaid Catches
- View and manage unpaid catches for a specific fisherman.
- Process payments and advances.

### Log Catch
- Log new fish catches for fishermen.

### Give Advance
- Record advances given to fishermen.

### Log Catch Royalty
- Log catches for royalty fishermen.

### Fisherman Royalty Summary and Detail
- View summaries and details of royalty payments.

### Manager List and Detail
- View list of managers and their balances.
- View detailed payments sent and received by managers.

### Give Money to Manager
- Owners can transfer money to managers.

### Add Money to Manager
- Record money added to managers by owners.

### Add Miscellaneous Expense
- Record miscellaneous expenses and adjust manager balances.

### Master Transaction View
- View combined transactions including payments, royalties, and expenses.

### Add Fisherman and Add Royalty Fisherman
- Add new fishermen and royalty fishermen.

### Edit Fish Prices
- Edit prices and royalty amounts for fish.
- Add or delete fish types.

## 5. User Roles and Permissions
- Owners: Can transfer money to managers.
- Managers: Handle payments, advances, and expenses.
- Fishermen: Have catches and payments tracked.
- Royalty Fishermen: Receive royalty payments.

## 6. Running the Project
- Use Django's development server for local testing.
- Run `python manage.py runserver` and access via browser.

## 7. Additional Notes
- The project uses Django's built-in User model for authentication.
- Financial transactions update balances and payment records automatically.
- Templates and static files provide the UI for managing the system.
- Further customization can be done by extending models and views.

---

This documentation provides a detailed overview and guide to the IRAI Fishery Business Management System. For further assistance, refer to the source code and Django documentation.
