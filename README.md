<div align="center">

# 🛡️ MikroTik Auto Backup Tool

[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)](https://github.com/rezaworks/mikrotik-backup-tool)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/rezaworks/mikrotik-backup-tool)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-orange.svg)](https://github.com/rezaworks/mikrotik-backup-tool)

</div>

<p align="center">
  <strong>🚀 Professional MikroTik Router Backup Management System</strong>
</p>

<p align="center">
  A powerful, web-based backup management application designed for ISP and office environments. Built with modern web technologies to provide comprehensive router backup automation, scheduling, and monitoring capabilities.
</p>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📖 Usage Guide](#-usage-guide)
- [🎯 Supported Router Types](#-supported-router-types)
- [💻 Technology Stack](#-technology-stack)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [🚢 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📋 Changelog](#-changelog)
- [🐛 Troubleshooting](#-troubleshooting)
- [📞 Support](#-support)
- [📜 License](#-license)

---

## ✨ Features

### 🔧 **Core Functionality**
- **📁 Multiple Router Management**: Add, configure, and manage multiple MikroTik routers
- **⚡ One-Click Backup**: Trigger backups instantly and download files automatically
- **🔄 Connection Testing**: Test router connectivity before adding to system
- **📊 Real-time Monitoring**: Live status indicators for all managed routers
- **📱 Responsive Interface**: Optimized for desktop, tablet, and mobile devices

### 🔄 **Backup Management**
- **💾 Automated Backups**: Schedule automatic backups with flexible timing
- **📋 Backup Types**: Support for full system and configuration-only backups
- **🗂️ File Organization**: Automatic file naming and organized storage
- **📥 Download Management**: Easy access to all backup files
- **🧹 Cleanup Automation**: Automatic removal of old backup files

### 🎨 **User Experience**
- **💫 Modern UI/UX**: Clean, professional design with intuitive navigation
- **🌓 Dark/Light Theme**: Adaptive theming for comfortable viewing
- **📊 Interactive Dashboard**: Real-time statistics and system overview
- **🎯 Drag & Drop**: Seamless router configuration experience
- **⏳ Progress Indicators**: Real-time feedback during backup operations

### 🛡️ **Security & Performance**
- **🔒 Secure Connections**: SSL/TLS support for router communications
- **🛠️ Error Handling**: Comprehensive error reporting and recovery
- **⚡ Performance Optimized**: Efficient processing for multiple routers
- **🔐 Credential Management**: Secure storage of router credentials
- **🌐 Cross-Platform**: Compatible with Windows, macOS, and Linux

---

## 🚀 Quick Start

### 📋 Prerequisites
- **Python 3.8+** 🐍
- **Modern web browser** 🌐
- **MikroTik RouterOS 6.0+** 📡
- **100MB+ free disk space** 💾

### ⚡ Installation & Setup

#### 🚀 **Option 1: Quick Start (Recommended)**

```bash
# Clone the repository
git clone https://github.com/rezaworks/mikrotik-backup-tool.git
cd mikrotik-backup-tool

# Create virtual environment
python -m venv mikrotik_backup_venv
source mikrotik_backup_venv/bin/activate  # Windows: mikrotik_backup_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch application
python backend/app.py

# Open browser and navigate to:
# http://localhost:5000
```

#### 🐳 **Option 2: Docker (Alternative)**

```bash
# Build Docker image
docker build -t mikrotik-backup-tool .

# Run container
docker run -p 5000:5000 mikrotik-backup-tool

# Access at: http://localhost:5000
```

#### 📦 **Option 3: Production Deployment**

```bash
# Using Gunicorn (Recommended for production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# Access at: http://your-server:5000
```

---

## 📖 Usage Guide

### ➕ **Adding Routers**
1. **🔧 Access Router Management**: Click "Add Router" from the main dashboard
2. **📝 Enter Router Details**: Provide name, IP address, credentials
3. **🔌 Test Connection**: Verify router connectivity and API access
4. **💾 Save Configuration**: Store router for future backup operations

### 📦 **Creating Backups**
1. **🎯 Select Target Router**: Choose from configured routers list
2. **⚙️ Choose Backup Type**: Select full system or configuration backup
3. **▶️ Initiate Backup**: Click "Backup Now" to start the process
4. **📥 Download File**: Automatically download the backup file

### 📊 **Monitoring & Management**
1. **📈 View Dashboard**: Monitor all routers status in real-time
2. **🔍 Check Logs**: Review backup history and system events
3. **⚙️ Manage Schedules**: Configure automated backup schedules
4. **🧹 Cleanup**: Remove old backup files automatically

### 📤 **File Management**
- **📂 Automatic Organization**: Backups organized by router and date
- **📥 Easy Downloads**: Direct download links for all backup files
- **🗂️ Format Support**: Both full (.backup) and config (.rsc) formats
- **📋 Metadata Tracking**: File size, creation date, and router information

---

## 🎯 Supported Router Types

| Router Type | Description | Features |
|-------------|-------------|----------|
| **📡 MikroTik RouterOS** | All RouterBOARD devices | Full API integration |
| **🌐 CCR Series** | Cloud Core Routers | High-performance backups |
| **🏠 hAP Series** | Home Access Point | Wireless configuration backup |
| **🏢 RB Series** | General purpose routers | Complete system backup |
| **🔒 RB1100AHx4** | Enterprise routers | Advanced configuration management |

### 🔌 **Connection Methods**
- **🌐 API Connection**: Direct RouterOS API communication
- **🔒 SSL/TLS Support**: Secure encrypted connections
- **🔐 Authentication**: Username/password and key-based auth
- **📊 Status Monitoring**: Real-time connection health checks

---

## 💻 Technology Stack

### **Core Technologies**
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
</p>

### **Key Dependencies**
- **🔗 Flask**: Web framework for Python backend
- **🗄️ Flask-SQLAlchemy**: Database ORM for router management
- **🔌 librouteros**: MikroTik RouterOS API communication
- **🔒 paramiko**: SSH/SFTP for secure file transfers
- **⏰ schedule**: Background job scheduling
- **🌐 flask-cors**: Cross-origin resource sharing

### **Development Tools**
<p align="center">
  <img src="https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white" alt="VS Code">
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
  <img src="https://img.shields.io/badge/Virtual_Environment-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="Virtual Env">
</p>

---

## 📁 Project Structure

```
mikrotik-backup-tool/
├── 📄 backend/                  # 🔧 Backend Python application
│   ├── app.py                   # 🚀 Main Flask application
│   ├── models.py                # 💾 Database models and schemas
│   ├── utils/                   # 🔧 Utility modules
│   │   ├── mikrotik.py          # 📡 MikroTik communication utilities
│   │   └── scheduler.py         # ⏰ Backup scheduling logic
│   └── config.db               # 💾 SQLite database (auto-created)
├── 📄 public/                   # 🌐 Frontend assets
│   ├── index.html               # 🏠 Main web interface
│   ├── style.css                # 🎨 Application styling
│   ├── script.js                # ⚡ Frontend functionality
│   └── assets/                  # 🖼️ Static assets
│       ├── logo.svg             # 🏷️ Application logo
│       └── icons/               # 🔲 UI icons
├── 📄 backups/                  # 💾 Backup storage directory
├── 📄 requirements.txt          # 📦 Python dependencies
├── 📄 README.md                 # 📚 Project documentation
├── 📄 LICENSE                   # 📜 MIT license file
├── 📄 .gitignore               # 🚫 Git ignore patterns
├── 📄 setup.py                  # 📦 Package configuration
└── 📄 venv/                     # 🐍 Python virtual environment
```

---

## 🔧 Configuration

### **Application Settings**
```python
# Default Configuration (backend/app.py)
PORT = 5000
BACKUP_DIR = 'backups/'
DATABASE_URL = 'sqlite:///backend/config.db'
SECRET_KEY = 'your-secret-key-here'  # Change in production
```

### **Router Configuration**
Each router requires the following information:
- **Name**: Friendly identifier (e.g., "Office-Firewall")
- **Host**: IP address or hostname (e.g., "192.168.1.1")
- **Username**: RouterOS login username (default: "admin")
- **Password**: RouterOS login password
- **Port**: API port (default: 8728)
- **SSL**: Enable/disable SSL encryption

### **Environment Variables**
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret
export BACKUP_DIR=/path/to/backups
export DATABASE_URL=sqlite:///path/to/database.db
```

---

## 🚢 Deployment

### **🖥️ Development Deployment**
```bash
# Using Flask development server
python backend/app.py

# Access at: http://localhost:5000
```

### **🏭 Production Deployment**

#### **Option A: Gunicorn (Recommended)**
```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# Access at: http://your-server:5000
```

#### **Option B: Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "backend/app.py"]
```

```bash
# Build and run
docker build -t mikrotik-backup-tool .
docker run -p 5000:5000 mikrotik-backup-tool
```

#### **Option C: Nginx + Gunicorn**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🤝 Contributing

We welcome contributions from the community! 🌟

### **🚀 Getting Started**
1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/amazing-feature`
3. 💻 Make your changes
4. ✅ Test thoroughly
5. 📤 Submit a pull request

### **📋 Contribution Guidelines**
- 📝 Follow PEP 8 style guidelines for Python code
- 🧪 Write comprehensive tests for new features
- 📚 Update documentation for API changes
- 📱 Ensure responsive design for UI modifications
- 🔄 Maintain backward compatibility when possible

### **🎯 Areas for Contribution**
- 🔧 **New Router Support**: Additional RouterOS versions or device types
- 📊 **Enhanced Analytics**: New monitoring and reporting features
- ⚡ **Performance Improvements**: Backup speed and efficiency
- 💫 **UI/UX Enhancements**: Accessibility, mobile optimization
- 🧪 **Testing**: Unit tests, integration tests, performance benchmarks

---

## 📋 Changelog

### **🆕 Version 1.0.0 (Current)**
- ✨ Initial release with core backup functionality
- 🌐 Complete MikroTik RouterOS API integration
- 📱 Modern responsive web interface
- 📦 Support for full system and configuration backups
- 🔄 Real-time status monitoring and alerts

### **🔮 Planned Features**
- [ ] ⏰ Advanced scheduling with cron expressions
- [ ] 📧 Email notifications for backup completion/failure
- [ ] 📊 Advanced reporting and analytics dashboard
- [ ] 🔌 REST API for third-party integrations
- [ ] ☁️ Cloud storage integration (AWS S3, Google Cloud)

---

## 🐛 Troubleshooting

### **❌ Common Issues**

| Problem | Solution |
|---------|----------|
| **Router connection failed** | Verify IP address, credentials, and API access |
| **Backup process hangs** | Check router resources and network connectivity |
| **File download fails** | Verify disk space and file permissions |
| **Web interface not loading** | Confirm Flask is running on correct port |

### **🔧 Getting Help**
1. 📖 Check this README thoroughly
2. 🔍 Search existing GitHub issues
3. 💬 Create a new issue with detailed information
4. 📧 Contact: [work.rezaul@outlook.com](mailto:work.rezaul@outlook.com)

---

## 📞 Support & Contact

### **💬 Get Help**
- **📧 Email**: [work.rezaul@outlook.com](mailto:work.rezaul@outlook.com)
- **🐛 Issues**: [Create a GitHub issue](https://github.com/rezaworks/mikrotik-backup-tool/issues)
- **💭 Discussions**: [GitHub Discussions](https://github.com/rezaworks/mikrotik-backup-tool/discussions)

### **🌟 Show Your Support**
- ⭐ **Star this project** if you find it helpful
- 🐛 **Report bugs** to help improve the tool
- 💡 **Suggest features** for future releases
- 📖 **Share with others** who might benefit

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2023 REZ LAB

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👨‍💻 Author & Contact

<p align="center">
  <strong>Rezaul Karim</strong>
</p>

<p align="center">
  <a href="mailto:work.rezaul@outlook.com">
    <img src="https://img.shields.io/badge/Email-work.rezaul@outlook.com-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email">
  </a>
  <a href="https://www.linkedin.com/in/rezaul-bd/">
    <img src="https://img.shields.io/badge/LinkedIn-REZ%20LAB-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
  <a href="https://github.com/rezaworks">
    <img src="https://img.shields.io/badge/GitHub-rezaworks-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</p>

<p align="center">
  <strong>🏢 REZ LAB</strong>
</p>

---

<div align="center">

## 🎯 **About This Project**

<p align="center">
  <strong>Built with ❤️ for MikroTik administrators and ISP professionals</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg" alt="Production Ready">
  <img src="https://img.shields.io/badge/Maintenance-Active-green.svg" alt="Actively Maintained">
</p>

<p align="center">
  <strong>⭐ If you find this project helpful, please give it a star!</strong>
</p>

<p align="center">
  <a href="#-features">✨ Features</a> •
  <a href="#-quick-start">🚀 Quick Start</a> •
  <a href="#-usage-guide">📖 Usage</a> •
  <a href="#-contributing">🤝 Contribute</a>
</p>

</div>
