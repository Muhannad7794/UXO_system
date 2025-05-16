# UXO Risk Prioritization & Assessment System

This project is a modular, Dockerized Django REST API designed to support risk assessment and prioritization of unexploded ordnance (UXO) contamination in conflict-affected regions, with an initial focus on Syria. The system enables automated dataset transformation, structured UXO record management, risk score computation, and citizen report handling.

## 📦 Features

- **Feature Engineering Module**: Automatically extracts and computes derived features such as ordnance age, burial depth, and condition from raw or semi-structured datasets.
- **Risk Scoring Engine**: Calculates and prioritizes UXO threat levels using a standardized model that considers burial depth, ordnance type, environmental impact, and population density.
- **Citizen Reporting System**: Allows users or field agents to submit new UXO sightings for further verification and integration.
- **RESTful API with OpenAPI Documentation**: The backend is built using Django REST Framework and exposes fully documented endpoints through drf-spectacular and Swagger UI.
