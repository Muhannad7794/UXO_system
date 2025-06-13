# UXO Prioritization & Risk Assessment System

This project is a modular, Dockerized Django application designed to support the risk assessment and prioritization of Unexploded Ordnance (UXO) in post-conflict regions, with an initial focus on Syria. The system provides a data-driven, evidence-based platform to help humanitarian demining agencies allocate resources effectively and save lives.

The widespread contamination of land with UXO poses a severe and immediate threat to civilian life and reconstruction efforts. This system addresses the critical need for a systematic method to standardize risk assessment and provide clear, actionable intelligence to guide clearance operations.

---

## ✨ Key Features

The system is architected as a Modular Monolith, providing clear separation of concerns while maintaining ease of deployment. Its key features are divided into several domains:

---

### 📊 Data Management & Ingestion

- **Dual Ingestion Pipelines**: Supports two distinct data flows: a public-facing pipeline for citizen-sourced reports requiring administrative verification, and a direct ingestion path for trusted, authoritative data.
- **Bulk CSV Upload**: A UI-driven feature for authenticated administrators to bulk-upload UXO records directly, with backend validation and processing.
- **Geospatial Linking**: Automatically links new records to their correct administrative region by performing a spatial join at the database level.
- **RESTful API**: A comprehensive REST API built with Django REST Framework provides full CRUD (Create, Read, Update, Delete) operations for all core data models.

---

### ☢️ Risk Assessment Engine

- **Standard-Based Model**: Implements a sophisticated risk model based on the principle of `Risk = f(Threat, Vulnerability)`, which is aligned with the International Mine Action Standards (IMAS).
- **Automated Scoring**: Utilizes Django Signals to automatically calculate a granular `DangerScore` for every UXO record the moment it is created or updated, ensuring data consistency.
- **Decoupled Logic**: The scoring engine is a self-contained Django app (`danger_score`), allowing the risk model to be updated or calibrated in the future with minimal impact on the rest of the system.

---

### 📈 Advanced Analytics & Visualization

- **Interactive Geospatial Dashboard**: A frontend dashboard built with Leaflet.js displays all UXO records on an interactive map. Markers are dynamically colour-coded based on their `danger_score`.
- **Dynamic "Hot Zone" Analysis**: Leverages PostGIS's `ST_ClusterDBSCAN` function to identify and visualize statistically significant clusters of high-risk incidents, which are pre-calculated for high performance.
- **Risk Heatmaps**: Generates and displays intensity-based heatmaps based on the concentration and danger scores of UXO records.
- **Multi-Modal Statistics Engine**: An interactive "Reports & Statistics" page allows administrators to perform complex data analysis on demand:
  - **Grouped Analysis**: Generates aggregate statistics (Count, Average, etc.) for any categorical field.
  - **Bivariate & Regression Analysis**: Performs linear regression to quantify the relationship between any two numeric variables, returning key metrics like R-squared, slope, and intercept.
  - **K-Means Clustering**: Uses unsupervised machine learning to partition records into logistical zones or discover hidden "risk profiles" in the dataset.

---

### ⚙️ DevOps & Professional Practices

- **Containerized Environment**: The entire application stack is containerized with Docker and orchestrated with Docker Compose, ensuring a consistent and reproducible environment for development and deployment.
- **CI/CD Pipeline**: A Continuous Integration pipeline using GitHub Actions automatically runs linters and executes the test suite, ensuring code quality and preventing regressions.
- **Automated API Documentation**: Integrates `drf-spectacular` to automatically generate an OpenAPI 3.0 specification, providing interactive Swagger and Redoc API documentation.

---

## 🛠️ Technology Stack

| Category     | Technology                                                   |
|--------------|--------------------------------------------------------------|
| **Backend**  | Python, Django, Django REST Framework, GeoDjango, Pandas, Scikit-learn |
| **Database** | PostgreSQL with PostGIS extension                            |
| **Frontend** | Django Templates, JavaScript (Vanilla), Chart.js, Leaflet.js |
| **DevOps**   | Docker, Docker Compose, GitHub Actions                       |
| **API Docs** | drf-spectacular (OpenAPI 3.0)                                |

---

## 🚀 Getting Started

To get the project up and running locally, follow these steps.

### Prerequisites

- Git  
- Docker  
- Docker Compose

---

### 1. Clone the Repository

```bash
git clone https://github.com/Muhannad7794/UXO-system.git
cd UXO-system
```

---

### 2. Create Environment File

Create a `.env` file in the project root. This file will hold your secret keys and database credentials.

```bash
touch env.example .env
```

Now, open the `.env` file and fill in the correct values.

---

### 3. Build and Run the Containers

Use Docker Compose to build the images and start the Django backend and PostgreSQL database services.

```bash
docker compose up --build -d
```

> The `-d` flag runs the containers in detached mode.

---

### 4. Initialize the Database

Run the initial database migrations and create an administrative superuser.

```bash
# Run migrations
docker compose exec backend python manage.py migrate

# Create a superuser
docker compose exec backend python manage.py createsuperuser
```

Follow the prompts to create your admin user.

---

### 5. Load Initial Data (Optional)

The repository should contain sample CSV files for regions and initial UXO records. You can load this data using the custom management commands.

```bash
# Load region polygons
docker compose exec backend python manage.py import_regions

# Load initial UXO records
docker compose exec backend python manage.py import_uxo_data
```

---

### 6. Access the Application

You should now be able to access the application and its components:

- **Web Application**: [http://localhost:8001](http://localhost:8001)  
- **API Documentation (Swagger UI)**: [http://localhost:8001/api/docs/](http://localhost:8001/api/docs/)

---

## ⚖️ License

This project is licensed under custom license issued for this repo. For further details check the LICENSE file.
