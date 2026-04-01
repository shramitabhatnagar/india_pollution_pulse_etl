# India Pollution Pulse
**A Real-Time Air Quality Monitoring Dashboard for India**

**Project Documentation**

**Prepared by:** Shramita  
**Date:** April 01, 2026

---

## Table of Contents
1. Executive Summary  
2. Project Objectives  
3. System Architecture  
4. Technologies Used  
5. Database Design  
6. Dashboard Features (Tab-by-Tab)  
7. Special Features  
8. Key Technical Highlights  
9. How to Run Locally  
10. Deployment on Azure  
11. Challenges Faced & Solutions  
12. Future Enhancements  
13. Conclusion  

---

## 1. Executive Summary

India Pollution Pulse is a live, interactive, and production-ready web dashboard that provides real-time air quality insights across India. It visualizes pollution data from hundreds of government monitoring stations on a dynamic 3D map, automatically calculates the official Air Quality Index (AQI) using CPCB standards, and delivers powerful analytical views.

Designed with a modern dark theme, the dashboard is intuitive for general citizens while offering in-depth analytics for researchers, environmental agencies, and policymakers. Data is fetched hourly through an automated Azure pipeline and displayed instantly.

**Live Dashboard:**  
https://pollutionui-hvckfzekfvfyhqcw.canadacentral-01.azurewebsites.net/

---

## 2. Project Objectives

- Deliver a user-friendly, real-time visualization of air pollution across India.
- Automatically compute and display the official CPCB Air Quality Index (AQI).
- Enable flexible filtering by pollutant, region, state, and station.
- Provide multiple analytical perspectives through interactive charts and maps.
- Build a scalable, secure, and fully cloud-native system on Microsoft Azure.

---

## 3. System Architecture

### 3.1 High-Level Architecture

```mermaid
flowchart TD
    A[Government Air Quality API<br>data.gov.in] --> B[Azure Function<br>Timer Trigger - Every Hour]
    B --> C[Azure SQL Database]
    C --> D[Streamlit Dashboard<br>Azure Web App]
    D --> E[End Users]
    
    subgraph "Data Pipeline Layer"
    B
    end
    subgraph "Storage Layer"
    C
    end
    subgraph "Presentation Layer"
    D
    end

