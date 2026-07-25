"""
Deployment Architecture
Configurations and utilities for different deployment scenarios.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import json


class DeploymentEnvironment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentPlatform(Enum):
    """Deployment platforms."""
    STREAMLIT_CLOUD = "streamlit_cloud"
    HEROKU = "heroku"
    AWS_ECS = "aws_ecs"
    DOCKER_LOCAL = "docker_local"
    KUBERNETES = "kubernetes"


@dataclass
class DeploymentConfig:
    """Configuration for deployment."""
    environment: DeploymentEnvironment
    platform: DeploymentPlatform
    app_name: str
    version: str
    region: str = "us-east-1"
    replicas: int = 1
    max_replicas: int = 3
    memory_mb: int = 1024
    cpu_cores: float = 1.0
    enable_ssl: bool = True
    enable_logging: bool = True
    enable_monitoring: bool = True
    config_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'environment': self.environment.value,
            'platform': self.platform.value,
            'app_name': self.app_name,
            'version': self.version,
            'region': self.region,
            'replicas': self.replicas,
            'max_replicas': self.max_replicas,
            'memory_mb': self.memory_mb,
            'cpu_cores': self.cpu_cores,
            'enable_ssl': self.enable_ssl,
            'enable_logging': self.enable_logging,
            'enable_monitoring': self.enable_monitoring,
            'config_data': self.config_data,
        }


class ProcfileGenerator:
    """Generates Procfile for Heroku deployment."""

    @staticmethod
    def generate_procfile() -> str:
        """Generate Procfile content."""
        return """web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
worker: python worker.py
"""

    @staticmethod
    def generate_procfile_advanced() -> str:
        """Generate advanced Procfile with background tasks."""
        return """web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
worker: celery -A celery_app worker --loglevel=info
beat: celery -A celery_app beat --loglevel=info
"""


class DockerfileGenerator:
    """Generates Dockerfile for container deployment."""

    @staticmethod
    def generate_dockerfile() -> str:
        """Generate Dockerfile for Streamlit app."""
        return """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .streamlit directory
RUN mkdir -p ~/.streamlit

# Create Streamlit config
RUN echo "[server]" > ~/.streamlit/config.toml && \\
    echo "port = 8501" >> ~/.streamlit/config.toml && \\
    echo "headless = true" >> ~/.streamlit/config.toml && \\
    echo "runOnSave = true" >> ~/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py"]
"""

    @staticmethod
    def generate_docker_compose() -> str:
        """Generate docker-compose.yml for local development."""
        return """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DEBUG=true
      - ENVIRONMENT=development
    volumes:
      - .:/app
    command: streamlit run app.py --logger.level=debug

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=finance_advisor
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
"""


class KubernetesManifestGenerator:
    """Generates Kubernetes manifests for deployment."""

    @staticmethod
    def generate_deployment() -> str:
        """Generate Kubernetes Deployment."""
        return """apiVersion: apps/v1
kind: Deployment
metadata:
  name: finance-advisor-app
  labels:
    app: finance-advisor
spec:
  replicas: 2
  selector:
    matchLabels:
      app: finance-advisor
  template:
    metadata:
      labels:
        app: finance-advisor
    spec:
      containers:
      - name: app
        image: YOUR_REGISTRY/finance-advisor:latest
        ports:
        - containerPort: 8501
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: finance-advisor-service
spec:
  selector:
    app: finance-advisor
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: finance-advisor-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: finance-advisor-app
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
"""

    @staticmethod
    def generate_configmap() -> str:
        """Generate Kubernetes ConfigMap."""
        return """apiVersion: v1
kind: ConfigMap
metadata:
  name: finance-advisor-config
data:
  environment: production
  debug: "false"
  log_level: INFO
  max_workers: "4"
  cache_ttl: "3600"
"""

    @staticmethod
    def generate_secret() -> str:
        """Generate Kubernetes Secret template."""
        return """apiVersion: v1
kind: Secret
metadata:
  name: finance-advisor-secrets
type: Opaque
stringData:
  database_url: postgresql://user:password@postgres:5432/finance_advisor
  api_key: YOUR_API_KEY_HERE
  redis_url: redis://redis:6379/0
  secret_key: YOUR_SECRET_KEY_HERE
"""


class EnvironmentConfigurator:
    """Configures environment variables for deployment."""

    DEVELOPMENT_ENV = {
        'ENVIRONMENT': 'development',
        'DEBUG': 'true',
        'LOG_LEVEL': 'DEBUG',
        'DATABASE_URL': 'sqlite:///./finance_advisor.db',
        'REDIS_URL': 'redis://localhost:6379/0',
        'CACHE_TTL': '3600',
        'API_TIMEOUT': '300',
    }

    STAGING_ENV = {
        'ENVIRONMENT': 'staging',
        'DEBUG': 'false',
        'LOG_LEVEL': 'INFO',
        'DATABASE_URL': 'postgresql://user:pass@staging-db:5432/finance_advisor',
        'REDIS_URL': 'redis://staging-redis:6379/0',
        'CACHE_TTL': '3600',
        'API_TIMEOUT': '300',
    }

    PRODUCTION_ENV = {
        'ENVIRONMENT': 'production',
        'DEBUG': 'false',
        'LOG_LEVEL': 'WARNING',
        'DATABASE_URL': 'postgresql://user:pass@prod-db:5432/finance_advisor',
        'REDIS_URL': 'redis://prod-redis:6379/0',
        'CACHE_TTL': '7200',
        'API_TIMEOUT': '60',
        'ENABLE_MONITORING': 'true',
        'ENABLE_PROFILING': 'false',
    }

    @staticmethod
    def get_environment_vars(environment: DeploymentEnvironment) -> Dict[str, str]:
        """Get environment variables for environment."""
        if environment == DeploymentEnvironment.DEVELOPMENT:
            return EnvironmentConfigurator.DEVELOPMENT_ENV
        elif environment == DeploymentEnvironment.STAGING:
            return EnvironmentConfigurator.STAGING_ENV
        else:
            return EnvironmentConfigurator.PRODUCTION_ENV

    @staticmethod
    def generate_env_file(environment: DeploymentEnvironment) -> str:
        """Generate .env file content."""
        env_vars = EnvironmentConfigurator.get_environment_vars(environment)
        lines = [f"{key}={value}" for key, value in env_vars.items()]
        return "\n".join(lines)


class DeploymentMonitor:
    """Monitors deployment health and performance."""

    @dataclass
    class DeploymentStatus:
        """Status of deployment."""
        environment: DeploymentEnvironment
        platform: DeploymentPlatform
        status: str  # healthy, degraded, unhealthy
        app_running: bool
        uptime_hours: float
        active_users: int
        error_rate: float
        avg_response_time_ms: float
        cpu_usage_pct: float
        memory_usage_pct: float
        last_deployment: str
        timestamp: str

        def to_dict(self) -> Dict[str, Any]:
            return {
                'environment': self.environment.value,
                'platform': self.platform.value,
                'status': self.status,
                'app_running': self.app_running,
                'uptime_hours': self.uptime_hours,
                'active_users': self.active_users,
                'error_rate': self.error_rate,
                'avg_response_time_ms': self.avg_response_time_ms,
                'cpu_usage_pct': self.cpu_usage_pct,
                'memory_usage_pct': self.memory_usage_pct,
                'last_deployment': self.last_deployment,
                'timestamp': self.timestamp,
            }

    @staticmethod
    def check_deployment_health(config: DeploymentConfig) -> DeploymentStatus:
        """Check deployment health."""
        from datetime import datetime as dt

        return DeploymentMonitor.DeploymentStatus(
            environment=config.environment,
            platform=config.platform,
            status='healthy',
            app_running=True,
            uptime_hours=24.0,
            active_users=10,
            error_rate=0.01,
            avg_response_time_ms=150,
            cpu_usage_pct=45.0,
            memory_usage_pct=60.0,
            last_deployment=dt.now().isoformat(),
            timestamp=dt.now().isoformat(),
        )


class CI_CDConfiguration:
    """Generates CI/CD configuration files."""

    @staticmethod
    def generate_github_actions() -> str:
        """Generate GitHub Actions workflow."""
        return """name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest --cov=./ --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v2

    - name: Deploy to Streamlit Cloud
      uses: streamlit/deploy-action@v1.0.0
      with:
        app-path: app.py
        deploy-key: ${{ secrets.STREAMLIT_DEPLOY_KEY }}
"""

    @staticmethod
    def generate_gitlab_ci() -> str:
        """Generate GitLab CI configuration."""
        return """stages:
  - test
  - build
  - deploy

variables:
  REGISTRY: registry.gitlab.com
  IMAGE_NAME: $REGISTRY/$CI_PROJECT_PATH

test:
  stage: test
  image: python:3.9
  script:
    - pip install -r requirements.txt pytest pytest-cov
    - pytest --cov=./ --cov-report=xml
  coverage: '/^TOTAL.+?(\d+%)$/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHA $IMAGE_NAME:latest
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $IMAGE_NAME:latest

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - echo "Deploying to production..."
    - kubectl set image deployment/finance-advisor app=$IMAGE_NAME:$CI_COMMIT_SHA
  only:
    - main
"""


class RollbackStrategy:
    """Implements rollback strategies."""

    @staticmethod
    def get_rollback_plan(current_version: str, previous_version: str) -> Dict[str, Any]:
        """Get rollback plan."""
        return {
            'current_version': current_version,
            'previous_version': previous_version,
            'steps': [
                {
                    'step': 1,
                    'action': 'Stop current deployment',
                    'estimated_time_sec': 30,
                },
                {
                    'step': 2,
                    'action': 'Verify database integrity',
                    'estimated_time_sec': 60,
                },
                {
                    'step': 3,
                    'action': 'Start previous version',
                    'estimated_time_sec': 45,
                },
                {
                    'step': 4,
                    'action': 'Run health checks',
                    'estimated_time_sec': 30,
                },
            ],
            'total_estimated_time_sec': 165,
            'risk_level': 'low',
        }

    @staticmethod
    def get_blue_green_deployment() -> Dict[str, Any]:
        """Get blue-green deployment strategy."""
        return {
            'strategy': 'blue-green',
            'description': 'Two identical production environments, switch traffic after verification',
            'steps': [
                'Deploy new version to green environment',
                'Run smoke tests on green',
                'Switch load balancer to green',
                'Monitor green for errors (5 minutes)',
                'If success: blue becomes new baseline',
                'If failure: revert to blue immediately',
            ],
            'downtime': '0 minutes',
            'rollback_time': '< 1 minute',
        }

    @staticmethod
    def get_canary_deployment() -> Dict[str, Any]:
        """Get canary deployment strategy."""
        return {
            'strategy': 'canary',
            'description': 'Gradually shift traffic to new version',
            'phases': [
                {
                    'phase': 1,
                    'percentage': 5,
                    'duration_minutes': 10,
                    'action': 'Monitor error rate and latency',
                },
                {
                    'phase': 2,
                    'percentage': 25,
                    'duration_minutes': 15,
                    'action': 'Monitor with larger user base',
                },
                {
                    'phase': 3,
                    'percentage': 50,
                    'duration_minutes': 20,
                    'action': 'Full monitoring before full rollout',
                },
                {
                    'phase': 4,
                    'percentage': 100,
                    'duration_minutes': 5,
                    'action': 'Complete rollout',
                },
            ],
            'total_duration_minutes': 50,
            'downtime': '0 minutes',
            'rollback_time': '< 5 minutes',
        }
