# 🤖 ThingOne AI - Intelligent Voice Assistant

**ThingOne AI** is a professional, full-stack AI Voice Assistant built with **Django**, **Python**, and **MongoDB**. It features a modern, responsive UI that supports seamless voice interaction in English and Hinglish, making it a perfect companion for natural conversations.



---

## 🚀 Key Features

* **🎙️ Voice-First Interaction:** Integrated Speech-to-Text and Text-to-Speech engine.
* **🗣️ Hinglish Support:** Smart language detection that handles mixed Hindi and English responses naturally.
* **📱 Fully Responsive UI:** Professional mobile-first design with a slide-in overlay sidebar.
* **🌙 Dark Mode Aesthetic:** Futuristic deep-space theme with smooth CSS animations.
* **📂 Chat Management:** Save, clear, and manage multiple chat histories securely.
* **👁️ Security:** Secure JWT-based authentication with a "Password Visibility" toggle.
* **🧠 AI Powered:** Leveraging advanced LLMs for context-aware and intelligent replies.

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | Python, Django |
| **Frontend** | HTML5, CSS3 (Modern Flexbox/Grid), JavaScript (ES6+) |
| **Database** | MongoDB (NoSQL) |
| **Authentication** | JWT (JSON Web Tokens) |
| **APIs** | OpenAI/Gemini API, Web Speech API |

---

## 📦 Project Structure

```text
THING_ONE_V1/
├── backend/            # Django Project Settings & WSGI
├── api/                # Core Logic, Views, and Chat Endpoints
├── static/             # Images (thingone-logo.jpeg), CSS, JS
├── templates/          # Responsive HTML Files (home, login, signup)
├── .env                # Secret Keys (OpenAI, Mongo URL)
├── requirements.txt    # Project Dependencies
└── Procfile            # Deployment Configuration
⚙️ Installation & Setup
Clone the repository:


git clone [https://github.com/yourusername/thingone-ai.git](https://github.com/yourusername/thingone-ai.git)
cd thingone-ai
Create a Virtual Environment:


python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:


pip install -r requirements.txt
Environment Variables: Create a .env file in the root directory:

Code snippet
SECRET_KEY=your_django_secret_key
OPENAI_API_KEY=your_api_key
MONGO_URL=your_mongodb_connection_string
DEBUG=True
Run the Server:


python manage.py runserver
🌐 Deployment
This project is optimized for Render and Railway.

Build Command: pip install -r requirements.txt

Start Command: gunicorn backend.wsgi

🤝 Contributing
Contributions are welcome! If you have ideas for new features or UI improvements, feel free to fork the repo and submit a pull request.
