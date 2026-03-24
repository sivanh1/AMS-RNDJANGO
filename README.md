# AMS — Attendance Management System
Simple version built with Django REST + React Native Expo + MySQL

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# MySQL — run in MySQL shell:
# CREATE DATABASE ams_db CHARACTER SET utf8mb4;

# Edit settings.py — set your MySQL root password

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
# Edit src/services/api.js — set BASE_URL to http://localhost:8000
npx expo start --web --clear
```

## Features
- Employee: Register, Login, Mark attendance (Present/WFH), Request Leave
- Admin: View today's attendance stats, Approve/Reject leave requests
- JWT authentication
- MySQL database
