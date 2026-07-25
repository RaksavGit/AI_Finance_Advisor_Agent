# Deployment Guide - AI Finance Advisor Agent v2.0

**Version**: 2.0 Enterprise Edition  
**Last Updated**: July 25, 2026  
**Status**: Production Ready

---

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Recommended for MVP/Demo)

#### Prerequisites
- GitHub account with repository pushed
- Streamlit Cloud account (free at https://streamlit.io/cloud)

#### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy enhanced app with enterprise features"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your GitHub repository
   - Configure:
     - Repository: `RaksavGit/AI_Finance_Advisor_Agent`
     - Branch: `main`
     - Main file path: `app_enhanced.py`

3. **App Settings**
   - Client error details: `expanded`
   - Logger level: `info`
   - Client toolbars: `auto`

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for deployment

#### Access URL
```
https://share.streamlit.io/?repo=RaksavGit/AI_Finance_Advisor_Agent
```

After deployment, your unique URL will be:
```
https://[YOUR-USERNAME]-ai-finance-advisor-agent.streamlit.app/
```

---

### Option 2: Heroku (Production with Database)

#### Prerequisites
- Heroku account (https://www.heroku.com/)
- Heroku CLI installed
- GitHub repository

#### Procfile Setup
```
web: streamlit run app_enhanced.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

#### Deploy Steps

1. **Initialize Heroku App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set ENVIRONMENT=production
   heroku config:set DEBUG=false
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **View Logs**
   ```bash
   heroku logs --tail
   ```

#### Access URL
```
https://your-app-name.herokuapp.com/
```

---

### Option 3: Docker + AWS ECS (Enterprise)

#### Prerequisites
- Docker installed
- AWS account
- AWS CLI configured

#### Build Docker Image

1. **Create Dockerfile** (already provided in features/deployment.py)
   ```bash
   docker build -t finance-advisor:latest .
   ```

2. **Test Locally**
   ```bash
   docker run -p 8501:8501 finance-advisor:latest
   ```

3. **Push to ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login \
       --username AWS --password-stdin YOUR_REGISTRY_URL
   
   docker tag finance-advisor:latest YOUR_REGISTRY_URL/finance-advisor:latest
   docker push YOUR_REGISTRY_URL/finance-advisor:latest
   ```

4. **Deploy to ECS**
   - Use AWS Console or CloudFormation
   - Create ECS service with Docker image
   - Configure load balancer
   - Enable auto-scaling

#### Access URL
```
https://your-load-balancer.us-east-1.elb.amazonaws.com/
```

---

### Option 4: Kubernetes (Multi-region Enterprise)

#### Prerequisites
- Kubernetes cluster (AWS EKS, Google GKE, Azure AKS)
- kubectl configured
- Docker image in registry

#### Deploy

1. **Apply Kubernetes Manifests**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/hpa.yaml
   ```

2. **Verify Deployment**
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get hpa
   ```

3. **Port Forward (Local Testing)**
   ```bash
   kubectl port-forward svc/finance-advisor-service 8501:80
   ```

#### Access URL
```
https://finance-advisor.your-domain.com/
```

---

## 📋 All Access URLs

### Live Deployment

| Environment | Platform | URL | Status |
|-------------|----------|-----|--------|
| **Production** | Streamlit Cloud | [https://[USERNAME]-ai-finance-advisor-agent.streamlit.app/](https://share.streamlit.io) | Ready to Deploy |
| **Production** | Heroku | https://your-app-name.herokuapp.com/ | Ready to Deploy |
| **Enterprise** | AWS ECS | https://your-elb.us-east-1.elb.amazonaws.com/ | Ready to Deploy |
| **Enterprise** | Kubernetes | https://finance-advisor.your-domain.com/ | Ready to Deploy |

### Local Development

```
# Streamlit Local
streamlit run app_enhanced.py
→ http://localhost:8501

# Docker Local
docker run -p 8501:8501 finance-advisor:latest
→ http://localhost:8501

# Development with Features
python -m features.integration_example
→ Console output
```

---

## 🔧 Configuration Reference

### Environment Variables

| Variable | Development | Staging | Production |
|----------|-------------|---------|------------|
| `ENVIRONMENT` | development | staging | production |
| `DEBUG` | true | false | false |
| `LOG_LEVEL` | DEBUG | INFO | WARNING |
| `DATABASE_URL` | sqlite:/// | postgres://staging | postgres://prod |
| `CACHE_TTL` | 600 | 1800 | 3600 |
| `ENABLE_MONITORING` | false | true | true |

### Deployment Configuration

#### Development
```python
config = DeploymentConfig(
    environment=DeploymentEnvironment.DEVELOPMENT,
    platform=DeploymentPlatform.DOCKER_LOCAL,
    app_name="Finance Advisor",
    version="2.0",
    memory_mb=512,
    cpu_cores=0.5
)
```

#### Staging
```python
config = DeploymentConfig(
    environment=DeploymentEnvironment.STAGING,
    platform=DeploymentPlatform.HEROKU,
    app_name="Finance Advisor",
    version="2.0",
    memory_mb=1024,
    cpu_cores=1.0
)
```

#### Production
```python
config = DeploymentConfig(
    environment=DeploymentEnvironment.PRODUCTION,
    platform=DeploymentPlatform.AWS_ECS,
    app_name="Finance Advisor",
    version="2.0",
    region="us-east-1",
    replicas=3,
    max_replicas=10,
    memory_mb=2048,
    cpu_cores=2.0,
    enable_ssl=True,
    enable_logging=True,
    enable_monitoring=True
)
```

---

## 🔐 Security Checklist

- [ ] All API keys stored in environment variables
- [ ] HTTPS/SSL enabled on all environments
- [ ] Database credentials encrypted
- [ ] Access logs enabled
- [ ] WAF (Web Application Firewall) configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Secrets manager configured
- [ ] VPC/Network security groups configured
- [ ] Health checks configured
- [ ] Monitoring alerts configured
- [ ] Backup strategy implemented

---

## 📊 Monitoring & Health Checks

### Streamlit Cloud Health
```
https://[YOUR-APP].streamlit.app/healthz
```

### Heroku Health
```
heroku ps
heroku status
heroku logs --tail
```

### AWS ECS Health
```bash
aws ecs describe-services --cluster finance-advisor --services finance-advisor-service
aws ecs describe-task-definition --task-definition finance-advisor:1
```

### Logs & Metrics

**Access Observability Dashboard:**
Go to app → "📊 Observability" tab to view:
- Real-time metrics
- Event logs
- System health
- Performance metrics

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Automated)

Deploy automatically on push to main:

```yaml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy with Streamlit Action
        uses: streamlit/deploy-action@v1.0.0
        with:
          app-path: app_enhanced.py
          deploy-key: ${{ secrets.STREAMLIT_DEPLOY_KEY }}
```

---

## 📈 Scaling Guide

### For 100-500 Users
**Recommended**: Streamlit Cloud Pro or Heroku Dyno  
- Cost: $5-25/month
- No infrastructure management

### For 500-5000 Users
**Recommended**: AWS ECS or Heroku Standard
- Cost: $50-200/month
- Auto-scaling configured
- Load balancer enabled

### For 5000+ Users
**Recommended**: Kubernetes (EKS/GKE/AKS)
- Cost: $200-500+/month
- Full auto-scaling
- Multi-region support
- CDN integration

---

## 🚨 Troubleshooting

### App Won't Start
```bash
# Check logs
streamlit run app_enhanced.py --logger.level=debug

# Check dependencies
pip install -r requirements.txt

# Verify imports
python -c "from features.integration_example import FinanceAdvisorSystem"
```

### High Memory Usage
- Reduce cache TTL
- Disable plugins not in use
- Limit observability history size
- Implement database persistence

### Slow Performance
- Enable caching
- Profile with PerformanceMonitor
- Review logs via Observability dashboard
- Optimize skill execution

---

## 📞 Support & Resources

### Documentation
- **Features Guide**: FEATURES_GUIDE.md
- **Implementation Roadmap**: IMPLEMENTATION_ROADMAP.md
- **GitHub**: https://github.com/RaksavGit/AI_Finance_Advisor_Agent

### Quick Links
- Streamlit Docs: https://docs.streamlit.io
- Heroku Docs: https://devcenter.heroku.com
- AWS ECS Docs: https://docs.aws.amazon.com/ecs/
- Kubernetes Docs: https://kubernetes.io/docs/

### Community
- Streamlit Forum: https://discuss.streamlit.io
- GitHub Discussions: https://github.com/RaksavGit/AI_Finance_Advisor_Agent/discussions

---

## ✅ Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] requirements.txt updated
- [ ] app_enhanced.py tested locally
- [ ] Features module tested (python -m features.integration_example)
- [ ] Environment variables configured
- [ ] SSL/HTTPS enabled
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Security review completed
- [ ] Performance tested
- [ ] Documentation updated
- [ ] Team notified of deployment
- [ ] Rollback plan documented
- [ ] Post-deployment testing completed

---

**Status**: ✅ Ready for Deployment  
**Last Check**: July 25, 2026  
**Next Review**: August 2, 2026
