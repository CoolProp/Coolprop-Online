# Deploying py4web on PythonAnywhere

This guide explains how to deploy the CoolProp py4web application on PythonAnywhere.

## Prerequisites

- A PythonAnywhere account (free or paid)
- Python 3.10+ support (free tier supports Python 3.10)

## Step-by-Step Deployment

### 1. Clone the Repository

Open a Bash console on PythonAnywhere:

```bash
cd ~
git clone https://github.com/CoolProp/Coolprop-Online.git
cd Coolprop-Online
git checkout py4web
```

### 2. Create Virtual Environment

```bash
mkvirtualenv --python=python3.10 coolprop-env
```

### 3. Install Dependencies

```bash
cd ~/Coolprop-Online/apps/coolpropgit
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If CoolProp installation fails, try:
```bash
pip install CoolProp  # Use latest version instead of 7.2.0
```

### 4. Configure Web App

1. Go to the **Web** tab in PythonAnywhere
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.10** (or your preferred version)

### 5. Update WSGI Configuration

In the Web tab, click on the WSGI configuration file and replace its contents with **ONE** of these options:

#### Option 1: Direct import (Recommended)
```python
import sys

# Add your project to the path
project_home = '/home/YOUR_USERNAME/Coolprop-Online'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtual environment
activate_this = '/home/YOUR_USERNAME/.virtualenvs/coolprop-env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import the WSGI application
from apps.coolpropgit.wsgi import application
```

#### Option 2: Execute the wsgi.py file directly (if imports fail)
```python
import sys

# Add project to path
project_home = '/home/YOUR_USERNAME/Coolprop-Online'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtual environment
activate_this = '/home/YOUR_USERNAME/.virtualenvs/coolprop-env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Execute the wsgi.py file directly
wsgi_file = '/home/YOUR_USERNAME/Coolprop-Online/apps/coolpropgit/wsgi.py'
with open(wsgi_file) as f:
    exec(f.read())
```

**Replace `YOUR_USERNAME`** with your actual PythonAnywhere username!

If you get import errors, try Option 2 which executes the wsgi.py file directly.

### 6. Set Virtual Environment

In the Web tab, under **"Virtualenv"** section:
- Enter: `/home/YOUR_USERNAME/.virtualenvs/coolprop-env`

### 7. Configure Static Files (Optional)

In the **"Static files"** section:
- URL: `/static`
- Directory: `/home/YOUR_USERNAME/Coolprop-Online/apps/coolpropgit/static`

### 8. Update Session Secret

For security, update the session secret in `common.py`:

```bash
cd ~/Coolprop-Online/apps/coolpropgit
nano common.py
```

Change:
```python
session = Session(secret="your-very-long-random-secret-key-here")
```

Generate a secure key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 9. Reload Web App

Click the green **"Reload"** button at the top of the Web tab.

### 10. Access Your Application

Your app will be available at:
```
https://YOUR_USERNAME.pythonanywhere.com/coolpropgit/index
```

## Troubleshooting

### Error: "No module named 'py4web'"

Make sure py4web is installed in your virtual environment:
```bash
workon coolprop-env
pip install py4web
```

### Error: "No module named 'CoolProp'"

CoolProp may not have pre-built wheels. Try:
```bash
workon coolprop-env
pip install CoolProp --no-cache-dir
```

### View Error Logs

In the Web tab, check:
- **Error log**: Python errors and stack traces
- **Server log**: Server-related issues
- **Access log**: Incoming requests

### Database Permissions

Ensure the databases directory is writable:
```bash
chmod 755 ~/Coolprop-Online/apps/coolpropgit/databases
```

### Static Files Not Loading

Make sure static files path is correct in Web tab:
```
/home/YOUR_USERNAME/Coolprop-Online/apps/coolpropgit/static
```

## Updating the Application

To update after pushing changes:

```bash
cd ~/Coolprop-Online
git pull origin py4web
workon coolprop-env
pip install -r apps/coolpropgit/requirements.txt
```

Then reload the web app from the Web tab.

## Alternative: Using Other Hosting Platforms

The `apps/wsgi.py` file can be used with any WSGI-compatible hosting platform:

- **Heroku**: Use with Gunicorn
- **DigitalOcean**: Use with uWSGI or Gunicorn
- **AWS/Azure**: Use with appropriate WSGI server

Example with Gunicorn:
```bash
gunicorn apps.wsgi:application
```

## Support

For issues specific to:
- **py4web**: https://py4web.com
- **PythonAnywhere**: https://help.pythonanywhere.com
- **CoolProp**: https://github.com/CoolProp/CoolProp
