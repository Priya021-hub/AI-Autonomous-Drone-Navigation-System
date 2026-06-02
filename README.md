# AI Autonomous Drone Navigation System

Real-time autonomous drone navigation system using YOLOv8 object detection, A* path planning, FastAPI, and React.

## Features

* Real-time object detection using YOLOv8
* Dynamic obstacle avoidance
* A* path planning visualization
* Safe path coordinate generation
* Voice navigation alerts
* Live camera feed
* Obstacle counting
* FastAPI backend
* React frontend dashboard

## Technology Stack

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* FastAPI
* OpenCV
* Python

### AI & Algorithms

* YOLOv8
* A* Path Planning

## Screenshots

### Main Dashboard

![Dashboard](Screenshot%20\(87\).png)

### Path Planning

![Path Planning](Screenshot%20\(88\).png)

### Backend API

![FastAPI](Screenshot%20\(85\).png)

## Future Improvements

* Real drone integration
* GPS-based navigation
* SLAM mapping
* Multi-drone coordination

## Installation

### Clone Repository

```bash
git clone https://github.com/Priya021-hub/AI-Autonomous-Drone-Navigation-System.git
cd AI-Autonomous-Drone-Navigation-System
```

### Backend Setup

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend will start at:

```text
http://127.0.0.1:8000
```

### Frontend Setup

```bash
cd src

npm install

npm run dev
```

Frontend will start at:

```text
http://localhost:5173
```

## Usage

1. Start FastAPI backend.
2. Start React frontend.
3. Open the frontend in your browser.
4. Allow camera access.
5. YOLOv8 detects obstacles in real time.
6. A* Path Planning generates a safe route.
7. Voice alerts provide navigation instructions.
8. Safe path coordinates and mini-map update automatically.

## Project Structure

```text
AI-Autonomous-Drone-Navigation-System
│
├── backend
│   ├── main.py
│   ├── services
│   │   └── path_planning.py
│
├── src
│   ├── App.jsx
│   ├── main.jsx
│
├── requirements.txt
├── README.md
```


## Author

Priya Kumari
