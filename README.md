# 🏥 Hospital Network Optimization System

### 📍 Graph-Based Logistics & Appointment Management
**Academic Project | BUAP - Faculty of Computer Science**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Algorithms](https://img.shields.io/badge/Algorithms-Dijkstra-orange?style=for-the-badge)
![Data Structure](https://img.shields.io/badge/Data_Structure-Graphs-purple?style=for-the-badge)

---

## 📖 Overview
This project is a robust digital platform designed to optimize the management of the **Ángeles Hospital Network** (25 locations across Mexico).

Beyond simple appointment scheduling, this system implements **Graph Theory** and geospatial algorithms to solve logistical problems, such as finding the nearest hospital for a patient and calculating optimal routes between medical centers.

## ⚙️ Key Features & Algorithms
The core logic relies on advanced Data Structures and Algorithms:

### 1. 🌐 Graph Construction (Network Modeling)
- Modeled the 25 hospitals as **Nodes** and the routes as **Edges**.
- Developed a dynamic graph structure to represent the connectivity of the entire hospital network.

### 2. 🛣️ Shortest Path Optimization (Dijkstra's Algorithm)
- Implemented **Dijkstra’s Algorithm** from scratch to calculate the most efficient route between hospitals.
- Allows the system to recommend optimal transfers based on real distance weights.

### 3. 🌍 Geospatial Analysis (Haversine Formula)
- Integration of the **Haversine Formula** to calculate real-world spherical distances between patients and hospitals using GPS coordinates (Latitude/Longitude).
- Automatically detects the nearest facility to the user's location.

### 4. 📅 Data Management
- Processing and validation of complex datasets:
    - `pacientes.csv` (Patient records)
    - `doctores.csv` (Specialists and availability)
    - `rutas_hospitales.csv` (Network topology)
- Data cleaning module to handle missing coordinates and normalize hospital names.

---

## 🛠️ Project Structure
The system is organized into functional modules for better maintainability:

```text
├── datos/                      # Folder containing CSV Datasets
├── inicio.py                   # 🚀 Main execution entry point
├── hospital_cercano.py         # 🌍 Geospatial Logic (Haversine Formula)
├── rutas_hospitales_doctor.py  # 📍 Graph Logic & Route Optimization (Dijkstra)
├── agendar_cita.py             # Appointment scheduling logic
├── buscar_doctores.py          # Search & Filtering algorithms
├── login_paciente.py           # Patient Authentication
├── login_doctor.py             # Doctor Authentication
├── menu_paciente.py            # User Interface Navigation
├── ui_tema.py                  # UI/UX Theme configurations
└── utils.py                    # Helper functions for data loading
```

---

## 👥 Contributors
Developed by the Engineering Team at **Benemérita Universidad Autónoma de Puebla (BUAP)**:

- **Danna Patricia Riveroll Martínez** 🐺
- Abraham Fuentes López
- Gabriela Nicolás Torres
- Lidia Gizem Sánchez Montiel
