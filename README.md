# Autonomous Enterprise Telemetry & Incident System (AETIS)

An enterprise-grade Streamlit telemetry and security audit analytics dashboard for distributed microservices.

## Overview

The dashboard monitors, filters, and correlates telemetry events across enterprise microservices, detecting anomalous security incidents (e.g., SQL Injection, Brute Force, Slowloris DoS, L7 DDoS, Infiltration, Heartbleed, Privilege Abuse).

## Key Features

- **Cached Ingestion**: High-performance pandas ingestion with `@st.cache_data` for instant reload.
- **Dynamic Theming**: Dark theme by default with seamless toggle to Light theme.
- **Top KPI Metric Cards**:
  - **Total Requests**
  - **Average Latency (ms)**
  - **Error Rate (HTTP 4xx/5xx %)**
  - **Total Anomalous Events detected**
- **Sidebar Multidimensional Filters**:
  - `service_name` (Multi-select)
  - `region` (Multi-select)
  - `latency_ms` (Range Slider)
- **Deep-Dive Analytics**:
  - Threat & Anomaly Intelligence (attack vectors, service vulnerabilities, regional distributions, origin IP rankings).
  - Telemetry & Service Health (latency profiles, HTTP response code breakdowns, time-series volume).
  - Audit Log Explorer (free-text search, anomaly category filters, CSV export).

## Running the Application

Using `uv`:
```bash
uv run streamlit run app.py
```
Or via the package command:
```bash
uv run securityaudit
```
