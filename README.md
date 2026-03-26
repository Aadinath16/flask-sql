
# 🚀 Flask + GKE + Cloud SQL + Observability POC

This project demonstrates a complete production-style Proof of Concept (POC) using:

- Flask (Python Web App)
- Google Kubernetes Engine (GKE)
- Cloud SQL (MySQL) with Private IP
- Workload Identity
- Persistent Volumes
- Cloud Logging & Monitoring
- Custom Dashboard UI

---

## 📌 Features

✅ Connect Flask app to Cloud SQL using Workload Identity  
✅ Private IP connectivity (No public exposure)  
✅ Add / Fetch users from database  
✅ Execute custom SQL queries  
✅ Create and store files on Kubernetes volume  
✅ Structured logging (INFO / WARNING / ERROR)  
✅ Monitoring endpoints (200 / 400 / 500)  
✅ Alert-ready logs  
✅ Web-based dashboard  

---

## 📁 Project Structure

```
flask-gke-poc/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── db_config.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── app.js
│   └── style.css
│
└── data/   # Mounted Volume
```

---

## 🗄️ Database Initialization (IMPORTANT)

After infrastructure is ready, initialize the database using SQL file stored in Cloud Storage.

### Upload SQL File

```
gsutil cp init.sql gs://<your-bucket-name>/sql/init.sql
```

### Import SQL

```
gcloud sql import sql <INSTANCE_NAME> gs://<your-bucket-name>/sql/init.sql
```

---

## ☸️ Deploy

```
kubectl apply -f ksa.yaml
```

```
gcloud iam service-accounts add-iam-policy-binding \
  dev-node-sa@gcp-project-id.iam.gserviceaccount.com \
  --project=gcp-project-id \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:gcp-project-id-dev.svc.id.goog[namespace/flask-ksa]"
```

```
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## 📊 Monitoring

Endpoints:

- /api/metrics/200
- /api/metrics/400
- /api/metrics/500

---

## 📜 License

Internal Use
