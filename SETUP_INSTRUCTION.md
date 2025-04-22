# Setup Instructions

This document contains detailed instructions to get your Smart Job Application Assistant up and running quickly.

## Prerequisites

Before starting, make sure you have:

1. Python 3.7 or above installed
2. An OpenRouter API key (needed for all AI features)
3. Git installed (optional, for cloning the repository)

## Installation Steps

### Step 1: Clone the Repository

If you have Git installed, clone the repository:

```bash
git clone https://github.com/yourusername/smart-job-assistant.git
cd smart-job-assistant
```

Alternatively, you can download the ZIP file from GitHub and extract it.

### Step 2: Create a Virtual Environment

Creating a virtual environment is recommended to avoid package conflicts:

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

On macOS and Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

### Step 5: Get an OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai) and create an account
2. Go to https://openrouter.ai/keys to create an API key
3. Add credits to your account - many models have free tiers or require minimal credits

### Step 6: Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application should open automatically in your default web browser. If not, you can access it at http://localhost:8501.

## Configuration Options

### Using a Different Port

If port 8501 is already in use, you can specify a different port:

```bash
streamlit run app.py --server.port 8502
```

### Running in Headless Mode

To run the app on a server without opening a browser:

```bash
streamlit run app.py --server.headless true
```

## API Integration

The app uses OpenRouter to access multiple AI models. When prompted:

1. Enter your OpenRouter API key in the sidebar
2. Select which models to use for analysis and document generation
3. Alternatively, choose custom models from the available list

## Data Storage

This application prioritizes privacy:

1. **Profile Data**: Stored only in the browser session (temporary)
   - Use the "Export Profile" feature to save your profile as a JSON file
   - Upload the JSON file in future sessions to restore your profile

2. **API Keys**: Never saved to disk
   - You'll need to re-enter your API key each time you start the app
   - This ensures your credentials remain secure

3. **Application Data**: Saved locally as a CSV file
   - The job_applications.csv file is created in the application directory
   - Contains basic tracking information for your job applications

## Troubleshooting

### "No module named 'streamlit'"

Run `pip install streamlit` or check that your virtual environment is activated.

### "Invalid API key provided"

Make sure you've entered a valid OpenRouter API key in the sidebar.

### "Error processing job posting"

Some job descriptions may be too complex. Try simplifying the job description or use a more powerful model for analysis.

### "Session state has no attribute 'profile'"

Make sure you've created a profile before attempting job analysis or document generation.

## Next Steps

After setup, you can:

1. Create your professional profile
2. Find job listings that interest you
3. Analyze them for fit with your skills
4. Add missing skills to your profile
5. Generate tailored application documents
6. Track your application status