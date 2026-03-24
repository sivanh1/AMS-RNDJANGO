# AMS — Attendance Management System

---


##  Screenshots

| User Dashboard                             | Apply WFH                             |
| ------------------------------------------ | ------------------------------------- |
| ![User Dashboard](./screenshots/img1.jpeg) | ![Apply WFH](./screenshots/img2.jpeg) |

| Pending Requests                             | Admin Dashboard                             |
| -------------------------------------------- | ------------------------------------------- |
| ![Pending Requests](./screenshots/img3.jpeg) | ![Admin Dashboard](./screenshots/img4.jpeg) |

---
##  Overview

A full-stack Attendance Management System built using **Django REST Framework**, **React Native (Expo)**, and **MySQL**.

This system allows employees to mark attendance, apply for leave or work-from-home (WFH), and enables admins to manage and approve requests.

---


##  Tech Stack

* **Backend:** Django REST Framework
* **Frontend:** React Native (Expo)
* **Database:** MySQL
* **Authentication:** JWT (JSON Web Tokens)

---



## Features

###  Authentication

* User Registration
* Login with JWT

---

###  Employee Features

* Mark Attendance (Present / WFH)
* Apply for Leave
* Apply for Work From Home
* View Attendance History

---

###  Admin Features

* View dashboard statistics
* Approve / Reject Leave Requests
* Approve / Reject WFH Requests
* Monitor employee attendance

---

##  Setup Instructions

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

### MySQL Setup

```sql
CREATE DATABASE ams_db CHARACTER SET utf8mb4;
```

Update MySQL credentials in `settings.py`

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

---

###  Frontend Setup

```bash
cd frontend
npm install --legacy-peer-deps
```

 Update API URL in:

```
src/services/api.js
```

```js
BASE_URL = "http://localhost:8000"
```

Run app:

```bash
npx expo start --clear
```

