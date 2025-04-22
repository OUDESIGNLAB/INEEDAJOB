# Smart Job Application Assistant

A streamlined AI-powered application to help job seekers analyze job postings, match them to their skills, and generate tailored application documents.

# Website

If you want to see it in action, take a look here!

https://ineedajob.streamlit.app/

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Intelligent Profile Management**: Create, import, or build your professional profile
- **Advanced Job Analysis**: Automatically extract key requirements from job listings and check how well your profile matches
- **Skill Gap Detection**: Identify missing skills and add them to your profile with proficiency ratings
- **Personalized Documents**: Generate tailored cover letters and resume content highlighting your relevant experience
- **Application Tracking**: Keep track of all your job applications
- **AI Integration**: Choose from 300+ AI models through OpenRouter for different tasks

## Requirements

- Python 3.7+
- Streamlit
- OpenRouter API key
- Internet connection

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/OUDESIGNLAB/INEEDAJOB.git
   ```
   ```
   cd INEEDAJOB
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```
   Try:
   ```
   python3 -m venu venu
   ```
   If the previous command didn't work.
   
   ### On Mac:
   ```
   source venv/bin/activate
   ```
   ### On Windows:
   ```
   venv\Scripts\activate
   ```

4. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

5. Run the application:
   ```
   streamlit run app.py
   ```

## API Key Setup

To use this application, you'll need an OpenRouter API key:

1. Visit [OpenRouter](https://openrouter.ai) and create an account
2. Go to https://openrouter.ai/keys to create an API key
3. Enter your key in the app's sidebar when prompted

## Using the Application

### 1. Profile Management

Create your professional profile using one of these methods:

- **Upload Document**: Upload a resume, CV, or profile in PDF, DOCX, JSON, or TXT format
- **Interactive Builder**: Build your profile step-by-step through a guided interface
- **Load Example**: Use one of our example profiles to see how the app works
- **Use Existing**: Continue with a previously created profile

### 2. Job Analysis

1. Paste a complete job posting into the text area
2. Click "Analyze Job" to process the listing
3. Review the match score, matching skills, and missing skills
4. Add missing skills to your profile with the "Add Missing Skills" feature
5. Export your updated profile as a JSON file

### 3. Document Generation

1. After analyzing a job, generate tailored application documents
2. Get a personalized cover letter highlighting your relevant experience
3. Receive customized resume bullet points focused on the target position
4. Save or export the generated content

### 4. Application Tracking

- Save all analyzed jobs and generated documents
- Track application status (Ready to Apply, Applied, Interview, etc.)
- Update status as you progress through your job search

## Privacy Considerations

- Your profile data is stored only in the browser session (not permanently)
- API keys are never saved to disk - you'll need to re-enter on each session
- Export your profile to save it between sessions

## AI Models

The application uses OpenRouter to access a variety of AI models:

- Default: Claude 3.5 Sonnet (balanced quality and speed)
- Fast: GPT-3.5 Turbo (quick, cost-effective)
- Powerful: Claude 3.5 Sonnet (high-quality outputs)
- Creative: Claude 3 Opus (best for creative writing)
- Analysis: Claude 3.5 Sonnet with Thinking (deep analysis)

You can also select any other model available through OpenRouter.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenRouter for providing access to multiple AI models
- Streamlit for the web application framework
- All contributors and testers who helped improve this tool
