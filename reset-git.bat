# Step 1: Create a backup of your important code files first
# Create a new folder for backup
mkdir ..\itinerary-backup
 
# Copy your Python files and other important files (adjust the extensions as needed)
xcopy *.py ..\itinerary-backup\ /s
xcopy *.json ..\itinerary-backup\ /s
xcopy *.txt ..\itinerary-backup\ /s
xcopy *.md ..\itinerary-backup\ /s
xcopy *.html ..\itinerary-backup\ /s
xcopy *.css ..\itinerary-backup\ /s
xcopy *.js ..\itinerary-backup\ /s
# Add any other file types you need

# Step 2: Remove Git tracking
# Delete the .git directory (this removes all Git history)
rmdir /s /q .git

# Step 3: Create a .gitignore file first
@echo off
(
echo # Python virtual environments
echo venv/
echo env/
echo ENV/
echo .env/
echo .venv/
echo pythonenv*/
echo 
echo # PyTorch specific files
echo *.dll
echo *.lib
echo *.so
echo *.dylib
echo 
echo # Python cache files
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo 
echo # Jupyter Notebook
echo .ipynb_checkpoints
echo 
echo # IDE settings
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo 
echo # Environment variables
echo .env
echo .env.local
echo .env.development.local
echo .env.test.local
echo .env.production.local
echo 
echo # Logs
echo logs/
echo *.log
echo npm-debug.log*
echo yarn-debug.log*
echo yarn-error.log*
echo 
echo # Local development settings
echo .DS_Store
echo Thumbs.db
) > .gitignore

# Step 4: Initialize a new Git repository
git init

# Step 5: Add and commit files (gitignore will be respected)
git add .
git commit -m "Initial clean commit"

# Step 6: Connect to GitHub repository
git remote add origin https://github.com/janat-zeezu/itinerary-planner.git

# Step 7: Push to GitHub
git push -f origin main

# If your default branch is named "master" instead of "main", use:
# git branch -M main
# git push -f origin main