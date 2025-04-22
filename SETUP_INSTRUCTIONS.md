# Setup Instructions

This document contains step-by-step instructions to get your Smart Job Application Assistant up and running quickly.

## Prerequisites

Before starting, make sure you have:

1. Python 3.7 or above installed
2. An OpenAI API key (needed for all AI features)
3. Git installed (optional, for cloning the repository)

## Installation Steps

### Step 1: Set Up the Project Directory

Create a project folder and set it up with all the necessary files:

```bash
# Create a project directory
mkdir job-application-assistant
cd job-application-assistant

# Create virtual environment
python -m venv venv
```

### Step 2: Activate the Virtual Environment

On macOS and Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

### Step 3: Create Project Files

Create the following files in your project directory:

1. `app.py` - The main application file
2. `requirements.txt` - Package dependencies
3. `example_profile.json` - Example profile for reference

You can copy the content for each file from the provided artifacts.

### Step 4: Install Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application should open automatically in your default web browser. If not, you can access it at http://localhost:8501.

## Using Your Own OpenAI API Key

When the application starts, you'll need to:

1. Enter your OpenAI API key in the sidebar
2. The key will only be stored in memory during the current session
3. You'll need to enter it again if you restart the application

## Creating a Professional Profile

There are three ways to create your profile:

1. **Upload Resume**: If you have a PDF resume, upload it for AI extraction
2. **Interactive Builder**: Fill out the form fields to build your profile
3. **Upload JSON**: If you already have a structured JSON profile, upload it directly

## Customization Options

### Job Site Parsing

The job parser uses generic HTML extraction that works with many job sites. For better results with specific sites, you can customize the `parse_job_listing` function in `app.py`.

### Tracking Data Location

By default, the application saves tracking data to `job_applications.csv` in the project directory. You can modify this path in the `save_application` function.

### AI Models

The application uses GPT-4 by default. You can change this to a less expensive model like GPT-3.5-Turbo by modifying the model parameter in the OpenAI calls.

## Troubleshooting Common Issues

### "No module named 'streamlit'"

Run `pip install streamlit` or check that your virtual environment is activated.

### "Invalid API key provided"

Make sure you've entered a valid OpenAI API key in the sidebar.

### "Error parsing job"

Some job sites may have protection against web scraping. Try a different job site or manually copy the job description.

### "Session state has no attribute 'profile'"

Make sure you're running the app with `streamlit run app.py` and not directly with Python.

## Next Steps

After setup, you can:

1. Create your profile
2. Find job listings that interest you
3. Analyze them for fit with your skills
4. Generate tailored application documents
5. Track your application status