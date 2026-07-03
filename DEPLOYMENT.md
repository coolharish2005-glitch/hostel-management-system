# Hostel Management System - Production Deployment Guide

## 🚀 Deploying to Production

This guide covers deploying the Hostel Management System to a production environment.

### Prerequisites

- Production server (Linux recommended)
- Python 3.8+
- PostgreSQL database
- Nginx or Apache
- SSL certificate (Let's Encrypt)
- Domain name

### Step 1: Server Setup

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y nginx
```

### Step 2: Clone Repository

```bash
cd /var/www
sudo git clone https://github.com/coolharish2005-glitch/hostel-management-system.git
cd hostel-management-system
sudo chown -R www-data:www-data /var/www/hostel-management-system
```

### Step 3: Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Step 4: Configure PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE hostel_db;
CREATE USER hostel_user WITH PASSWORD 'strong_password_here';
ALTER ROLE hostel_user SET client_encoding TO 'utf8';
ALTER ROLE hostel_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE hostel_user SET default_transaction_deferrable TO on;
ALTER ROLE hostel_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hostel_db TO hostel_user;
\q
```

### Step 5: Update Environment Variables

```bash
cd /var/www/hostel-management-system
sudo nano .env
```

```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=generate-a-strong-secret-key
DATABASE_URL=postgresql://hostel_user:strong_password_here@localhost:5432/hostel_db
```

### Step 6: Initialize Database

```bash
cd /var/www/hostel-management-system
source venv/bin/activate
python
```

```python
from app import app, db
with app.app_context():
    db.create_all()
exit()
```

### Step 7: Configure Gunicorn

Create `/var/www/hostel-management-system/wsgi.py`:

```python
from app import app

if __name__ == "__main__":
    app.run()
```

### Step 8: Setup Systemd Service

Create `/etc/systemd/system/hostel.service`:

```ini
[Unit]
Description=Hostel Management System
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/hostel-management-system
ExecStart=/var/www/hostel-management-system/venv/bin/gunicorn --workers 4 --bind unix:/var/www/hostel-management-system/app.sock app:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start hostel
sudo systemctl enable hostel
```

### Step 9: Configure Nginx

Create `/etc/nginx/sites-available/hostel`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://unix:/var/www/hostel-management-system/app.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/hostel-management-system/static/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/hostel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 10: Setup SSL with Let's Encrypt

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## 🔒 Security Best Practices

1. **Update Secret Key** - Use a strong, random secret key
2. **Enable HTTPS** - Always use SSL/TLS
3. **Use Environment Variables** - Never hardcode secrets
4. **Regular Backups** - Backup database and files regularly
5. **Keep Dependencies Updated** - Run `pip install --upgrade -r requirements.txt`
6. **Monitor Logs** - Watch for suspicious activities
7. **Set Strong Passwords** - Enforce strong password policies

---

## 📊 Monitoring & Maintenance

```bash
# Check service status
sudo systemctl status hostel

# View logs
sudo journalctl -u hostel -f

# Restart service
sudo systemctl restart hostel

# Database backup
pg_dump hostel_db > backup.sql

# Database restore
psql hostel_db < backup.sql
```

---

## 🚀 Performance Optimization

1. **Use Gunicorn Workers** - Configure based on CPU cores
2. **Enable Caching** - Implement Redis caching
3. **Database Indexing** - Add indexes to frequently queried columns
4. **CDN Integration** - Use CDN for static files
5. **Database Optimization** - Regular maintenance and vacuuming

---

## 📞 Support & Issues

For deployment issues or questions, please create an issue on GitHub or contact support.
