# Virtual Environment Setup Guide

This guide explains how to set up and use the virtual environment for the Flask Notes Application.

## 🎯 Why Use a Virtual Environment?

Virtual environments are essential for Python development because they:

- **Isolate dependencies**: Keep project dependencies separate from system-wide Python packages
- **Avoid conflicts**: Prevent version conflicts between different projects
- **Reproducible environments**: Ensure everyone working on the project uses the same dependency versions
- **Clean development**: Make it easy to start fresh or delete the environment

## 📦 What's Included

The project includes:

1. **Virtual environment**: Located in the `venv/` directory
2. **Dependencies**: Listed in `requirements.txt`
3. **Setup scripts**: Automated scripts for easy setup and execution

## 🚀 Setup Options

### Option 1: Automatic Setup (Recommended)

Use the `setup_and_run.sh` script to automatically:

```bash
./setup_and_run.sh
```

This script will:
- Create the virtual environment if it doesn't exist
- Activate it
- Install all dependencies
- Create necessary directories
- Run the application

### Option 2: Manual Setup

#### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

#### 2. Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the Application

```bash
python app.py
```

## 🧪 Running Tests

To run tests with the virtual environment:

```bash
./activate_and_test.sh
```

This will:
- Activate the virtual environment
- Run the test suite
- Show test results
- Deactivate the environment when done

## 🔧 Managing the Virtual Environment

### Check Installed Packages

```bash
source venv/bin/activate
pip list
```

### Add New Dependencies

```bash
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
```

### Update Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Delete and Recreate Environment

```bash
rm -rf venv
./setup_and_run.sh
```

## 💡 Tips

- **Always activate the virtual environment** before working on the project
- **Use `pip freeze`** to update `requirements.txt` when adding new packages
- **Don't commit the virtual environment** to version control (it's in `.gitignore`)
- **Use the same Python version** that was used to create the environment

## 🐛 Troubleshooting

### "Module not found" errors

If you get import errors, make sure you've:
1. Activated the virtual environment
2. Installed dependencies with `pip install -r requirements.txt`
3. Are running commands from the project directory

### Permission issues

If you get permission errors when activating the environment:

```bash
chmod +x venv/bin/activate
```

### Different Python versions

If you need to use a specific Python version:

```bash
python3.10 -m venv venv
```

## 📋 Virtual Environment Best Practices

1. **One environment per project**: Don't reuse environments across projects
2. **Document dependencies**: Always keep `requirements.txt` up to date
3. **Use `.gitignore`**: Never commit the virtual environment to version control
4. **Regular updates**: Periodically update dependencies to get security fixes
5. **Clean up**: Delete unused environments to save disk space

## 🔄 Environment Status

To check if you're in the virtual environment, look for `(venv)` at the beginning of your terminal prompt:

```bash
(venv) user@host:~/flask_notes_app$ 
```

If you see this, you're in the virtual environment. If not, activate it with `source venv/bin/activate`.

## 🎉 Ready to Go!

Your virtual environment is now set up and ready to use. The Flask Notes Application will run in an isolated environment with all the necessary dependencies!