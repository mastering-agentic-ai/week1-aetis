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
- **Samiksha AI Agent (Incident & Telemetry Assistant)**:
  - **Conversational Threat Intelligence**: Embedded AI Security Incident Commander grounded on live, multi-dimensionally filtered telemetry.
  - **Bring-Your-Own-Model (OpenRouter / OpenAI compatible)**: In-UI configuration for API Base URL, API Key, and Model (defaults to `openrouter/free`, supports any OpenAI-compatible provider).
  - **Real-Time Streaming & Visual Feedback**: Low-latency token streaming with an animated in-flight dispatch indicator.
  - **One-Click Quick Action Prompts**:
    - `⚡ Triage Briefing`: Automated SOC incident analysis and anomaly assessment.
    - `🎯 Top 3 Offenders`: Offending IP breakdown with MITRE ATT&CK mappings and ready-to-deploy WAF/CLI containment rules (`iptables`, Cloudflare, Nginx).
    - `⏱️ Latency SLA Impact`: Root-cause analysis of requests breaching the 2,000ms SLA threshold.
    - `🛡️ Containment Rules`: Tailored firewall rules, rate-limiting directives, and mitigation playbooks.
  - **Conversational Context**: Multi-turn dialogue with conversation history tracking and instant cache reset (`🧹 Clear Chat`).

## Configuration & Environment Variables

To use the **Samiksha AI Agent**, you can provide your credentials directly in the dashboard UI, or pre-configure them via environment variables:

```bash
# Optional: Set OpenRouter or other Agent API Key in environment
export OPENROUTER_API_KEY="sk-or-v1-..."
```

## Running the Application

Using `uv`:
```bash
uv run streamlit run app.py
```
Or via the package command:
```bash
uv run securityaudit
```
