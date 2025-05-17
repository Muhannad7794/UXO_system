# UXO Risk Prioritization & Assessment System

This project is a modular, Dockerized Django REST API designed to support risk assessment and prioritization of unexploded ordnance (UXO) contamination in conflict-affected regions, with an initial focus on Syria. The system enables automated dataset transformation, structured UXO record management, risk score computation, and citizen report handling.

## 📦 Features

- **UXO records Module**: Central data management module for storing structured UXO records. It acts as the core dataset source used in risk analysis, linking metadata like location, ordnance type, and population impact.
- **Risk Scoring Engine**: Calculates and prioritizes UXO threat levels using a standardized model that considers burial depth, ordnance type, environmental impact, and population density.
- **Citizen Reporting System**: Allows users or field agents to submit new UXO sightings for further verification and integration.
- **RESTful API with OpenAPI Documentation**: The backend is built using Django REST Framework and exposes fully documented endpoints through drf-spectacular and Swagger UI.
