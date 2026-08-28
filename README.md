Credit Risk Early Warning System (EWS)
An enterprise-grade, dual-architecture machine learning pipeline for assessing credit risk. This system handles real-time single applicant predictions using scikit-learn, and highly scalable asynchronous bulk predictions using PyTorch and Apache Kafka.

Live Production Access (AWS)
The application is unified behind a single AWS Elastic IP using Nginx as a reverse proxy. Both the frontend web interface and the backend API are accessible via this single entry point.

Production URL: [http://54.123.45.67](http://54.123.45.67) (Replace with your actual AWS Elastic IP)



Architecture & Features
This application resolves the standard machine learning bottleneck—server timeouts during massive batch predictions—by splitting the architecture into two distinct pipelines:

Synchronous Real-Time Pipeline (Single Applicant)

Tech: React → Django API (PredictRiskView) → Sklearn

Flow: Validates user input via Django REST Framework serializers, instantly transforms data using saved .pkl artifacts, and returns a real-time risk score and decision.

Asynchronous Event-Driven Pipeline (Bulk Upload)

Tech: React → Django API → Apache Kafka → PyTorch Worker (consumer.py) → PostgreSQL

Flow: Django acts as a lightweight dispatcher, instantly dumping massive CSV uploads into a Kafka queue and freeing up the web server. A background PyTorch consumer processes the queue, makes neural network predictions, and saves the results to PostgreSQL. The React frontend dynamically polls the database and provides a live progress bar until the CSV is ready for download.

🛠️ Technology Stack
Frontend: React.js, Vite, Axios

Backend: Django, Django REST Framework (DRF)

Machine Learning: PyTorch (Deep Learning), Scikit-Learn (Traditional ML), Joblib

Message Broker: Apache Kafka (Dockerized)

Database: PostgreSQL

Deployment: AWS EC2, Nginx, Gunicorn, systemd
credit_risk_ews/
├── artifacts/              # Contains shared ML artifacts (scaler.pkl, encoders.pkl, model.pkl, .pth)
├── data/                   # Contains raw historical training data
├── ews-frontend/           # React.js application
├── src/
│   ├── ews_backend/        # Main Django configuration & settings.py
│   ├── risk_model/         # Django app (models, views, urls, serializers)
│   ├── consumer.py         # PyTorch background worker (Kafka consumer)
│   ├── train_pytorch.py    # Offline ML training script
│   └── manage.py
└── docker-compose.yml      # Kraft local containers
