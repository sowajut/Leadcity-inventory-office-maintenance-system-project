# Inventory and Maintenance Management System (LCU)

This is a custom-built inventory and office maintenance web app created for Lead City University. The system allows departments (like Library, Senate, Medical Hospital) to manage their items, report maintenance issues, and track updates.

## 🔧 Features

- Department-based inventory tracking
- Submit and view maintenance reports
- User authentication (login/register)
- Admin access for status updates and role-based control
- Dashboard overview of reports and statistics
- No JavaScript used — fully built with Python (Flask), HTML, and CSS

## 🛠️ Built With

- Python (Flask)
- SQLite (simple local database)
- HTML & CSS (no JS)
- Flask Sessions (for login/auth)
- Git & GitHub (version control)

## 📸 Screenshots

| Login Page                         | Inventory Page                        |
|------------------------------------|---------------------------------------|
| ![Login](images/login.jpeg)        | ![Inventory](images/inventory-app1.jpeg) |

## 🚀 How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/sowajut/LCU-IOMS.git
   cd LCU-IOMS
(Optional) Create and activate a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install dependencies:

bash
Copy
Edit
pip install flask
Run the app:

bash
Copy
Edit
flask run
Open your browser and go to: http://localhost:5000

🧠 What I Learned
How to build full web apps with Flask

User login and session handling

Role-based access (Admin vs Staff)

Data storage with SQLite

Building UI with pure HTML and CSS

Structuring a scalable Flask project

📂 Folder Structure
csharp
Copy
Edit
LCU-IOMS/
│
├── static/               # CSS and images
│   └── images/
├── templates/            # HTML templates
│   └── ...
├── app.py                # Main Flask application
├── README.md             # Project info (this file)
└── requirements.txt      # Python dependencies
🏫 Developed For
Lead City University – for use by departments including:

Library

Medical Hospital

Senate

Faculty of Medicine

Faculty of Computer Science

📬 Contact
If you'd like to learn more or collaborate:

GitHub: @sowajut

Portfolio: https://sowajut.github.io/Elijahishomeyang/

Email: sowajut@gmail.com
