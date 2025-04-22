import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime
import PyPDF2
import io
from typing import Dict, Any, List, Optional
from openrouter_client import OpenRouterClient, get_recommended_models, format_model_info

# App title and configuration
st.set_page_config(page_title="Smart Job Application Assistant", layout="wide")

# Configure the OpenRouter API
def setup_api():
    with st.sidebar:
        st.title("Settings")
        api_key = st.text_input("Enter your OpenRouter API Key", type="password")
        
        if not api_key:
            st.warning("Please enter your OpenRouter API key to use AI features")
            st.markdown("""
            Don't have an OpenRouter API key? [Sign up here](https://openrouter.ai/keys)
            """)
            return None
        
        try:
            client = OpenRouterClient(api_key)
            # Test the API key by listing models
            client.list_models()
            
            # Store the client in session state
            st.session_state['openrouter_client'] = client
            
            # Model selection
            st.subheader("Model Settings")
            
            # Define model categories
            model_categories = {
                "default": "Claude 3.5 Sonnet (Default)",
                "fast": "GPT-3.5 Turbo (Fast)",
                "powerful": "Claude 3.5 Sonnet (Powerful)",
                "balanced": "GPT-4o Mini (Balanced)",
                "creative": "Claude 3 Opus (Creative)",
                "analysis": "Claude 3.5 Sonnet with Thinking (Analysis)"
            }
            
            # Set default models if not in session state
            if 'model_analysis' not in st.session_state:
                st.session_state['model_analysis'] = "default"
            if 'model_generation' not in st.session_state:
                st.session_state['model_generation'] = "default"
            
            # Let user select the model for different tasks
            st.session_state['model_analysis'] = st.selectbox(
                "Model for Job Analysis:",
                options=list(model_categories.keys()),
                index=list(model_categories.keys()).index(st.session_state['model_analysis']),
                format_func=lambda x: model_categories[x]
            )
            
            st.session_state['model_generation'] = st.selectbox(
                "Model for Document Generation:",
                options=list(model_categories.keys()),
                index=list(model_categories.keys()).index(st.session_state['model_generation']),
                format_func=lambda x: model_categories[x]
            )
            
            # Custom model option
            use_custom_model = st.checkbox("Use custom model")
            
            if use_custom_model:
                # Get available models from OpenRouter
                try:
                    with st.spinner("Loading available models..."):
                        all_models = client.list_models()
                        # Create a list of model options
                        model_options = []
                        for model in all_models:
                            model_id = model.get("id", "")
                            if model_id:
                                model_options.append({
                                    "id": model_id,
                                    "name": model.get("name", model_id)
                                })
                        
                        # Sort alphabetically by name
                        model_options.sort(key=lambda x: x["name"])
                        
                        # Create selection boxes for custom models
                        if model_options:
                            # For analysis
                            custom_analysis_index = 0
                            custom_analysis_model = st.selectbox(
                                "Custom Model for Analysis:",
                                options=range(len(model_options)),
                                format_func=lambda i: f"{model_options[i]['name']} ({model_options[i]['id']})"
                            )
                            st.session_state['custom_analysis_model'] = model_options[custom_analysis_model]['id']
                            
                            # For generation
                            custom_generation_index = 0
                            custom_generation_model = st.selectbox(
                                "Custom Model for Generation:",
                                options=range(len(model_options)),
                                format_func=lambda i: f"{model_options[i]['name']} ({model_options[i]['id']})"
                            )
                            st.session_state['custom_generation_model'] = model_options[custom_generation_model]['id']
                except Exception as e:
                    st.error(f"Error loading models: {str(e)}")
            
            # Show selected models
            st.markdown("---")
            st.subheader("Selected Models")
            
            # Function to get actual model ID
            def get_actual_model_id(task_type):
                if use_custom_model:
                    return st.session_state.get(f'custom_{task_type}_model', get_recommended_models()["default"])
                else:
                    return get_recommended_models()[st.session_state[f'model_{task_type}']]
            
            # Display selected models
            st.write(f"Analysis: `{get_actual_model_id('analysis')}`")
            st.write(f"Generation: `{get_actual_model_id('generation')}`")
            
            # Store the model selection function in session state
            st.session_state['get_model_id'] = get_actual_model_id
            
            return client
        except Exception as e:
            st.error(f"Error connecting to OpenRouter: {str(e)}")
            return None

# Extract professional info from uploaded resume
def extract_info_from_resume(client, uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Use OpenRouter to extract structured information
        try:
            response = client.chat_completion(
                model=get_recommended_models()[st.session_state['model_analysis']],
                messages=[
                    {"role": "system", "content": "Extract professional information from the resume into JSON format."},
                    {"role": "user", "content": f"Extract key professional details from this resume into a structured JSON with skills, education, experience, etc:\n\n{text[:7000]}"}  # Limit text size
                ]
            )
            
            content = response['choices'][0]['message']['content']
            
            # Extract JSON if it's wrapped in code blocks
            if "```" in content:
                match = re.search(r'```(?:json)?\s*(.*?)```', content, re.DOTALL)
                if match:
                    content = match.group(1)
                    
            try:
                return json.loads(content)
            except:
                return {"error": "Failed to parse resume"}
        except Exception as e:
            return {"error": f"API error: {str(e)}"}
    
    return {"error": "Unsupported file type"}

# Interactive career profile builder
def build_career_profile(client):
    st.subheader("Career Profile Builder")
    
    # Basic information
    with st.expander("Personal Information", expanded=True):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        location = st.text_input("Location")
    
    # Skills
    with st.expander("Skills", expanded=True):
        st.write("What are your top skills? (separated by commas)")
        skills_text = st.text_area("Skills")
        skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
    
    # Experience
    with st.expander("Work Experience", expanded=True):
        st.write("Let's talk about your work experience...")
        experience_prompt = st.text_area("Describe your work experience in a few paragraphs")
    
    # Education
    with st.expander("Education", expanded=True):
        st.write("What's your educational background?")
        education_prompt = st.text_area("Describe your education")
    
    # Use AI to structure the information
    if st.button("Generate Profile"):
        if 'openrouter_client' not in st.session_state:
            st.error("Please enter your OpenRouter API key in the sidebar")
            return None
            
        try:
            prompt = f"""
            Create a detailed professional profile JSON from this information:
            
            Name: {name}
            Email: {email}
            Phone: {phone}
            Location: {location}
            Skills: {', '.join(skills)}
            Experience: {experience_prompt}
            Education: {education_prompt}
            
            Structure it with nested objects for experience and education items, and include 
            arrays for skills divided by categories where appropriate.
            Return ONLY valid JSON - no explanations or markdown formatting.
            """
            
            response = client.chat_completion(
                model=get_recommended_models()[st.session_state['model_analysis']],
                messages=[
                    {"role": "system", "content": "Create a structured professional profile in JSON format based on user input. Return ONLY JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response['choices'][0]['message']['content']
            
            # Extract JSON if it's wrapped in code blocks
            if "```" in content:
                match = re.search(r'```(?:json)?\s*(.*?)```', content, re.DOTALL)
                if match:
                    content = match.group(1)
            
            try:
                profile_json = json.loads(content)
                st.json(profile_json)
                return profile_json
            except json.JSONDecodeError as e:
                st.error(f"Failed to generate profile. Invalid JSON: {str(e)}")
                st.code(content)
                return None
        except Exception as e:
            st.error(f"API error: {str(e)}")
            return None

# Process raw job posting
def process_job_posting(client, raw_posting):
    """Extract structured information from a raw job posting"""
    
    try:
        # Extract key information from the raw posting
        prompt = f"""
        Extract key information from this job posting. Return a JSON with these fields:
        - title: The job title
        - company: The company name
        - location: The job location
        - job_type: Type of employment (full-time, part-time, etc.)
        
        Return ONLY JSON with no explanations.
        
        JOB POSTING:
        {raw_posting[:4000]}  # Limit text to save tokens
        """
        
        response = client.chat_completion(
            model=get_recommended_models()[st.session_state['model_analysis']],
            messages=[
                {"role": "system", "content": "Extract structured job information from a posting. Return ONLY JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response['choices'][0]['message']['content']
        
        # Extract JSON if it's wrapped in code blocks
        if "```" in content:
            match = re.search(r'```(?:json)?\s*(.*?)```', content, re.DOTALL)
            if match:
                content = match.group(1)
                
        try:
            job_info = json.loads(content)
            
            # Add the description and other metadata
            job_info["description"] = raw_posting
            job_info["url"] = "manually-entered"
            job_info["date_found"] = datetime.now().strftime("%Y-%m-%d")
            
            return job_info
            
        except json.JSONDecodeError:
            # If parsing fails, create a basic structure
            return {
                "title": "Unknown Position",
                "company": "Unknown Company",
                "location": "Unknown",
                "job_type": "Unknown",
                "description": raw_posting,
                "url": "manually-entered",
                "date_found": datetime.now().strftime("%Y-%m-%d")
            }
    except Exception as e:
        return {"error": f"Error processing job posting: {str(e)}"}

# Replace the analyze_job_fit function with this debugged version

def analyze_job_fit(client, job_data, profile):
    """Analyze job fit with better profile data extraction and debugging"""
    if 'openrouter_client' not in st.session_state:
        return {"error": "Please enter your OpenRouter API key in the sidebar"}
        
    try:
        # First check if we have a valid job description
        if not job_data.get("description") or len(job_data.get("description", "").strip()) < 10:
            return {"error": "No valid job description provided"}
            
        # Debug profile data structure
        st.write("Debug - Profile data structure:", type(profile))
        
        # Standardize profile format if needed
        if isinstance(profile, dict) and "professional_metadata" in profile:
            st.write("Converting from professional-database.json format...")
            profile = convert_professional_database_to_profile(profile)
        
        # Check if profile exists and has content
        if not profile:
            return {
                "error": "No profile data found. Please create a profile first.",
                "overall_match": 0,
                "skills_match": "0%",
                "matching_skills": [],
                "missing_skills": ["No profile data available"],
                "explanation": "Cannot perform analysis without profile data."
            }
            
        # Extract all technical skills from profile with improved handling
        all_skills = []
        try:
            if isinstance(profile, dict):
                # Extract from standard format
                if "skills" in profile:
                    if isinstance(profile["skills"], dict):
                        # Handle categorized skills
                        for category, skills_list in profile["skills"].items():
                            if isinstance(skills_list, list):
                                all_skills.extend(skills_list)
                    elif isinstance(profile["skills"], list):
                        # Handle flat list of skills
                        all_skills = profile["skills"]
                
                # Try alternative locations
                if "professional_metadata" in profile and "key_skills" in profile["professional_metadata"]:
                    all_skills.extend(profile["professional_metadata"]["key_skills"])
                    
                if "certifications" in profile:
                    all_skills.extend(profile["certifications"])
                
                # Extract skills from entries if available
                if "entries" in profile:
                    for entry in profile["entries"]:
                        if "components" in entry:
                            all_skills.extend(entry["components"])
                        if "technologies" in entry.get("content", {}):
                            all_skills.extend(entry["content"]["technologies"])
                
                # Make sure skills are unique
                all_skills = list(set(all_skills))
            
            # Debug skills extraction
            st.write(f"Debug - Extracted skills: {all_skills}")
        except Exception as e:
            st.error(f"Error extracting skills: {str(e)}")
            
        # Extract experience with better error handling
        experience_highlights = []
        try:
            if isinstance(profile, dict):
                # Standard format
                if "experience" in profile and isinstance(profile["experience"], list):
                    for exp in profile["experience"]:
                        if isinstance(exp, dict):
                            # Add position and company if available
                            position = exp.get("position", "")
                            company = exp.get("company", "")
                            if position and company:
                                experience_highlights.append(f"{position} at {company}")
                            elif position:
                                experience_highlights.append(position)
                            
                            # Add key responsibilities
                            if "responsibilities" in exp and isinstance(exp["responsibilities"], list):
                                for resp in exp["responsibilities"][:3]:  # Limit to top 3
                                    experience_highlights.append(resp)
                            
                            # Add key achievements
                            if "achievements" in exp and isinstance(exp["achievements"], list):
                                for achievement in exp["achievements"][:2]:  # Limit to top 2
                                    experience_highlights.append(achievement)
                
                # Professional database format
                if "entries" in profile:
                    for entry in profile["entries"]:
                        if entry.get("type") == "employment":
                            # Extract job title
                            title = entry.get("title", "")
                            if " - " in title:
                                company, position = title.split(" - ", 1)
                                experience_highlights.append(f"{position} at {company}")
                            
                            # Extract responsibilities and achievements
                            if "content" in entry:
                                content = entry["content"]
                                if "responsibilities" in content and isinstance(content["responsibilities"], list):
                                    for resp in content["responsibilities"][:3]:
                                        experience_highlights.append(resp)
                                        
                                if "achievements" in content and isinstance(content["achievements"], list):
                                    for achv in content["achievements"][:2]:
                                        experience_highlights.append(achv)
            
            # Debug experience extraction
            st.write(f"Debug - Extracted experience highlights: {len(experience_highlights)} items")
        except Exception as e:
            st.error(f"Error extracting experience: {str(e)}")
        
        # Extract job requirements specifically for the Industrial Designer position
        try:
            # Get a cleaner summary of job requirements
            extraction_prompt = f"""
            Extract 10-15 key technical skills and qualifications required for this job.
            Return as a simple JSON array of strings.
            
            Example format: ["Skill 1", "Skill 2", "Skill 3"]
            
            JOB POSTING:
            {job_data["description"][:5000]}
            """
            
            req_response = client.chat_completion(
                model=get_recommended_models()[st.session_state.get('model_analysis', 'balanced')],
                messages=[
                    {"role": "system", "content": "Extract specific job skills and qualifications as a JSON array. Return ONLY a JSON array."},
                    {"role": "user", "content": extraction_prompt}
                ]
            )
            
            content = req_response['choices'][0]['message']['content']
            
            # Extract JSON array
            if "```" in content:
                match = re.search(r'```(?:json)?\s*(.*?)```', content, re.DOTALL)
                if match:
                    content = match.group(1)
                    
            # Parse JSON - handle different formats
            parsed_content = json.loads(content)
            
            # Handle case where it returns an object with a key
            if isinstance(parsed_content, dict):
                for key in parsed_content:
                    if isinstance(parsed_content[key], list):
                        job_requirements = parsed_content[key]
                        break
                else:
                    job_requirements = list(parsed_content.values())[0] if parsed_content else []
            # Handle case where it returns a list directly
            elif isinstance(parsed_content, list):
                job_requirements = parsed_content
            else:
                st.error(f"Unexpected requirements format: {type(parsed_content)}")
                job_requirements = ["Unable to properly extract requirements"]
            
            # Debug job requirements
            st.write(f"Debug - Extracted job requirements: {job_requirements}")
            
        except Exception as e:
            st.error(f"Error extracting job requirements: {str(e)}")
            # Create a basic set of job requirements based on common skills
            job_requirements = [
                "3D design skills",
                "CAD proficiency",
                "Technical documentation",
                "Design experience",
                "Manufacturing knowledge",
                "Problem-solving abilities",
                "Communication skills"
            ]
        
        # If no skills or experience found, return early with helpful message
        if not all_skills and not experience_highlights:
            missing_skills = job_requirements[:10] if isinstance(job_requirements, list) else []
            return {
                "overall_match": 0,
                "skills_match": "0%",
                "matching_skills": [],
                "missing_skills": missing_skills,
                "explanation": "The profile doesn't contain any skills or experience information. Please update your profile with relevant skills and experience to get a proper match analysis."
            }
        
        # Manually calculate a basic match score instead of using AI
        matching_skills = []
        missing_skills = []
        
        # Convert everything to lowercase for better matching
        all_skills_lower = [s.lower() for s in all_skills]
        experience_text = " ".join(experience_highlights).lower()
        
        # Check each job requirement
        for req in job_requirements:
            req_lower = req.lower()
            # Check if requirement is matched by a skill
            matched = False
            
            # Look for exact skill matches
            for skill in all_skills_lower:
                if skill.lower() in req_lower or req_lower in skill.lower():
                    matching_skills.append(req)
                    matched = True
                    break
                    
            # If not matched by skills, check experience text
            if not matched:
                # Extract key terms from requirement
                key_terms = [term.strip() for term in req_lower.split() if len(term.strip()) > 3]
                for term in key_terms:
                    if term in experience_text:
                        matching_skills.append(req)
                        matched = True
                        break
                        
            # If still not matched, it's missing
            if not matched:
                missing_skills.append(req)
        
        # Calculate match scores
        total_reqs = len(job_requirements)
        matches = len(matching_skills)
        
        if total_reqs > 0:
            match_percentage = int((matches / total_reqs) * 100)
            # Convert to a 0-10 scale for overall match
            overall_match = round((match_percentage / 100) * 10)
        else:
            match_percentage = 0
            overall_match = 0
            
        # Generate explanation
        explanation = f"Found {matches} matching skills/experiences out of {total_reqs} requirements. "
        explanation += f"The profile has {len(all_skills)} skills and {len(experience_highlights)} experience items. "
        
        if matches >= total_reqs * 0.7:
            explanation += "This is a strong match for the position."
        elif matches >= total_reqs * 0.5:
            explanation += "This is a good match with some areas for development."
        else:
            explanation += "There are several skill gaps for this position."
            
        # Prepare the result
        result = {
            "overall_match": overall_match,
            "skills_match": f"{match_percentage}%",
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "explanation": explanation
        }
        
        return result
            
    except Exception as e:
        import traceback
        st.error(f"Error analyzing job: {str(e)}")
        st.error(traceback.format_exc())
        return {
            "error": f"Error analyzing job: {str(e)}",
            "overall_match": 0,
            "skills_match": "0%", 
            "matching_skills": [],
            "missing_skills": ["Error during analysis"],
            "explanation": "An error occurred during analysis."
        }

# Generate tailored application documents
def generate_application_docs(client, job_analysis, profile):
    """Generate tailored application documents with ONLY facts from the profile"""
    if 'openrouter_client' not in st.session_state:
        return {"error": "Please enter your OpenRouter API key in the sidebar"}
        
    try:
        # Extract job details
        job_title = job_analysis['job_data']['title']
        company = job_analysis['job_data']['company']
        
        # Extract personal info for personalization
        personal_info = {}
        if "personal_info" in profile:
            personal_info = profile["personal_info"]
        
        # Get actual values or empty strings (not placeholders)
        name = personal_info.get("name", "").strip()
        email = personal_info.get("email", "").strip()
        phone = personal_info.get("phone", "").strip()
        location = personal_info.get("location", "").strip()
        
        # Extract REAL experience information to prevent fabrication
        experience_details = []
        if "experience" in profile and isinstance(profile["experience"], list):
            for exp in profile["experience"]:
                if isinstance(exp, dict):
                    exp_dict = {
                        "company": exp.get("company", ""),
                        "position": exp.get("position", ""),
                        "duration": exp.get("duration", ""),
                        "responsibilities": [],
                        "achievements": []
                    }
                    
                    # Only include real responsibilities
                    if "responsibilities" in exp and isinstance(exp["responsibilities"], list):
                        exp_dict["responsibilities"] = exp["responsibilities"]
                        
                    # Only include real achievements
                    if "achievements" in exp and isinstance(exp["achievements"], list):
                        exp_dict["achievements"] = exp["achievements"]
                        
                    experience_details.append(exp_dict)
        
        # Extract REAL skills to prevent fabrication
        all_skills = []
        if "skills" in profile:
            if isinstance(profile["skills"], dict):
                # If skills are categorized
                for category, skills_list in profile["skills"].items():
                    if isinstance(skills_list, list):
                        all_skills.extend(skills_list)
            elif isinstance(profile["skills"], list):
                all_skills = profile["skills"]
        
        # Generate cover letter with strict fact-checking instructions
        cover_letter_prompt = f"""
        Create a brief, enthusiastic cover letter for a {job_title} position at {company}.

        THE FOLLOWING INFORMATION IS THE ONLY FACTUAL INFORMATION YOU CAN USE:
        
        CANDIDATE DETAILS:
        Name: {name}
        Email: {email}
        Phone: {phone}
        Location: {location}
        
        VERIFIED SKILLS (use ONLY these exact skills, do not fabricate or expand):
        {json.dumps(all_skills)}
        
        VERIFIED WORK EXPERIENCE (use ONLY these exact companies and details, do not fabricate or expand):
        {json.dumps(experience_details)}
        
        JOB REQUIREMENTS:
        {job_analysis['job_data']['description'][:800]}
        
        IMPORTANT INSTRUCTIONS:
        1. Keep it SHORT (150-200 words maximum, about 3-4 short paragraphs)
        2. Be enthusiastic and friendly, but professional
        3. NEVER include ANY placeholders like "[Your Name]"
        4. NEVER fabricate work experience or skills - use ONLY what's provided above
        5. If a real company name isn't provided above, DO NOT make one up - refer to roles generically
        6. Only include details explicitly listed in the VERIFIED sections
        7. Do not expand on bullet points with specifics not provided above
        8. Keep it direct and engaging for busy hiring managers
        9. End with "Sincerely," followed by the name only if provided
        
        Use ONLY the facts provided above - no fabrication whatsoever.
        """
        
        # Use the selected model for document generation
        cover_letter_content = client.chat_completion(
            model=get_recommended_models()[st.session_state['model_generation']],
            messages=[
                {"role": "system", "content": "You are a strictly factual resume writer who uses ONLY the exact information provided. You NEVER fabricate experience, companies, or achievements. You do not elaborate beyond the given facts."},
                {"role": "user", "content": cover_letter_prompt}
            ]
        )['choices'][0]['message']['content']
        
        # Additional check to remove any remaining placeholders
        placeholder_patterns = [
            r'\[Your Name\]', r'\[your name\]', r'\[NAME\]', 
            r'\[Your Address\]', r'\[your address\]', r'\[ADDRESS\]',
            r'\[Your Email\]', r'\[your email\]', r'\[EMAIL\]',
            r'\[Your Phone\]', r'\[your phone\]', r'\[PHONE\]',
            r'\[Date\]', r'\[date\]', r'\[TODAY\'S DATE\]',
            r'\[Hiring Manager\'s Name\]', r'\[hiring manager\]', r'\[HIRING MANAGER\]',
            r'\[Company Address\]', r'\[company address\]', r'\[COMPANY ADDRESS\]',
            r'\[City, State, Zip\]', r'\[city, state, zip\]', r'\[CITY, STATE, ZIP\]'
        ]
        
        for pattern in placeholder_patterns:
            cover_letter_content = re.sub(pattern, '', cover_letter_content)
        
        # Generate resume bullets with strict facts
        resume_prompt = f"""
        Create tailored resume bullet points for a {job_title} position at {company}.
        
        USE ONLY THESE EXACT WORK EXPERIENCES (do not fabricate or expand):
        {json.dumps(experience_details)}
        
        JOB REQUIREMENTS:
        {job_analysis['job_data']['description'][:800]}
        
        INSTRUCTIONS:
        1. For each position, create 3 powerful bullet points
        2. Each bullet should be ONE LINE only (15 words maximum)
        3. Start with strong ACTION VERBS
        4. ONLY use responsibilities and achievements explicitly listed above
        5. DO NOT fabricate or add details not provided in the work experience
        6. If no achievements are provided for a role, focus on responsibilities only
        
        Return as JSON with position titles as keys and arrays of bullet points as values.
        Return ONLY valid JSON with no explanations or markdown formatting.
        """
        
        resume_content = client.chat_completion(
            model=get_recommended_models()[st.session_state['model_generation']],
            messages=[
                {"role": "system", "content": "You create powerful resume content using ONLY the exact information provided. You NEVER fabricate experience, roles, or achievements. Return ONLY JSON."},
                {"role": "user", "content": resume_prompt}
            ]
        )['choices'][0]['message']['content']
        
        # Extract JSON if it's wrapped in code blocks
        if "```" in resume_content:
            match = re.search(r'```(?:json)?\s*(.*?)```', resume_content, re.DOTALL)
            if match:
                resume_content = match.group(1).strip()
                
        try:
            resume_bullets = json.loads(resume_content)
            
            return {
                "cover_letter": cover_letter_content,
                "resume_bullets": resume_bullets
            }
        except json.JSONDecodeError:
            # Try to extract format manually with regex
            positions = re.findall(r'"([^"]+)":\s*\[(.*?)\]', resume_content, re.DOTALL)
            manual_bullets = {}
            
            if positions:
                for pos, bullets_text in positions:
                    bullets = re.findall(r'"([^"]+)"', bullets_text)
                    if bullets:
                        manual_bullets[pos] = bullets
            
            if manual_bullets:
                return {
                    "cover_letter": cover_letter_content,
                    "resume_bullets": manual_bullets
                }
            else:
                # Fallback to basic structure
                return {
                    "cover_letter": cover_letter_content,
                    "resume_bullets": {"Position": ["Managed key responsibilities in professional environment.",
                                                   "Contributed to team projects and initiatives.",
                                                   "Applied technical skills to solve challenges."]}
                }
    except Exception as e:
        return {"error": f"Error generating documents: {str(e)}"}

# Save application to tracking system
def save_application(job_analysis, docs, status="Ready to Apply"):
    # Create a record for tracking
    application = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "company": job_analysis['job_data']['company'],
        "position": job_analysis['job_data']['title'],
        "url": job_analysis['job_data']['url'],
        "match_score": job_analysis['match_analysis'].get('overall_match', 0),
        "status": status,
        "cover_letter": docs.get('cover_letter', ''),
        "resume_bullets": json.dumps(docs.get('resume_bullets', {}))
    }
    
    # Load existing applications
    try:
        applications_df = pd.read_csv("job_applications.csv")
    except:
        applications_df = pd.DataFrame(columns=[
            "date", "company", "position", "url", "match_score", 
            "status", "cover_letter", "resume_bullets"
        ])
    
    # Add new application
    applications_df = pd.concat([applications_df, pd.DataFrame([application])], ignore_index=True)
    applications_df.to_csv("job_applications.csv", index=False)
    
    return "Application saved successfully"

def convert_professional_database_to_profile(data):
    """
    Convert the professional-database.json format to the standard profile format used by the app.
    """
    try:
        if not isinstance(data, dict):
            return {"error": "Invalid data format"}
            
        # Check if it's already in the expected format
        if "personal_info" in data and "skills" in data:
            return data
            
        # Check if it's in the professional-database.json format
        if "professional_metadata" in data and "entries" in data:
            metadata = data["professional_metadata"]
            entries = data["entries"]
            
            # Create new profile structure
            profile = {
                "personal_info": {
                    "name": metadata.get("name", ""),
                    "email": metadata.get("contact", {}).get("email", ""),
                    "phone": metadata.get("contact", {}).get("phone", ""),
                    "location": metadata.get("location", ""),
                    "websites": metadata.get("contact", {}).get("websites", [])
                },
                "skills": {}
            }
            
            # Add key skills
            if "key_skills" in metadata:
                profile["skills"]["technical"] = metadata["key_skills"]
            
            # Add soft skills and certifications if available
            profile["skills"]["certifications"] = metadata.get("certifications", [])
            
            # Extract education
            profile["education"] = []
            if "education" in metadata:
                for edu_type, edu_info in metadata["education"].items():
                    parts = edu_info.split(" - ")
                    if len(parts) >= 2:
                        institution = parts[0]
                        degree = parts[1]
                        graduation_date = parts[2] if len(parts) > 2 else ""
                        
                        profile["education"].append({
                            "institution": institution,
                            "degree": degree,
                            "graduation_date": graduation_date
                        })
            
            # Extract experience from entries
            profile["experience"] = []
            for entry in entries:
                if entry.get("type") == "employment":
                    experience = {
                        "company": entry.get("title", "").split(" - ")[0].strip() if " - " in entry.get("title", "") else "",
                        "position": entry.get("title", "").split(" - ")[1].strip() if " - " in entry.get("title", "") else entry.get("title", ""),
                        "duration": entry.get("duration", ""),
                        "location": entry.get("location", ""),
                        "responsibilities": entry.get("content", {}).get("responsibilities", []),
                        "achievements": entry.get("content", {}).get("achievements", [])
                    }
                    profile["experience"].append(experience)
            
            # Extract projects
            profile["projects"] = []
            for entry in entries:
                if entry.get("type") in ["project", "personal_project"]:
                    project = {
                        "title": entry.get("title", ""),
                        "description": entry.get("content", {}).get("description", ""),
                        "technologies": entry.get("content", {}).get("technologies", []),
                        "duration": entry.get("duration", "")
                    }
                    profile["projects"].append(project)
            
            # Extract languages if available
            profile["languages"] = []
            
            # Extract interests if available
            for entry in entries:
                if entry.get("id") == "PROF-PREF-003":
                    profile["interests"] = entry.get("content", {}).get("self_identified_strengths", [])
                    break
            
            return profile
            
        # If not in any recognized format, try to map whatever we can
        new_profile = {"personal_info": {}, "skills": {}, "experience": []}
        
        # Map any fields we can find
        if "name" in data:
            new_profile["personal_info"]["name"] = data["name"]
        if "email" in data:
            new_profile["personal_info"]["email"] = data["email"]
        if "phone" in data:
            new_profile["personal_info"]["phone"] = data["phone"]
        if "location" in data:
            new_profile["personal_info"]["location"] = data["location"]
        
        # Check for skills
        if "skills" in data:
            if isinstance(data["skills"], list):
                new_profile["skills"]["technical"] = data["skills"]
            elif isinstance(data["skills"], dict):
                new_profile["skills"] = data["skills"]
        
        # Check for experience
        if "experience" in data and isinstance(data["experience"], list):
            new_profile["experience"] = data["experience"]
        
        # Check for education
        if "education" in data and isinstance(data["education"], list):
            new_profile["education"] = data["education"]
        
        return new_profile
        
    except Exception as e:
        return {"error": f"Error converting profile: {str(e)}"}

def extract_profile_from_text(text):
    """
    Extract profile information from unstructured text (e.g., resume text)
    """
    # This would be handled by the OpenRouter API in the real implementation
    # For now, we'll create a basic structure to demonstrate how it would work
    
    # Split by lines and look for key sections
    lines = text.strip().split('\n')
    profile = {
        "personal_info": {
            "name": "",
            "email": "",
            "phone": "",
            "location": ""
        },
        "skills": {
            "technical": []
        },
        "experience": [],
        "education": []
    }
    
    current_section = ""
    experience_item = None
    education_item = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a section header
        lower_line = line.lower()
        if "experience" in lower_line and line.isupper():
            current_section = "experience"
            continue
        elif "education" in lower_line and line.isupper():
            current_section = "education"
            continue
        elif "skills" in lower_line and line.isupper():
            current_section = "skills"
            continue
        elif "contact" in lower_line and line.isupper():
            current_section = "contact"
            continue
        
        # Process based on current section
        if current_section == "experience":
            # Check if this is a new role (usually starts with dates)
            if any(char.isdigit() for char in line) and ("-" in line or "–" in line):
                # Save previous experience item if exists
                if experience_item:
                    profile["experience"].append(experience_item)
                
                # Start new experience item
                experience_item = {
                    "company": "",
                    "position": "",
                    "duration": line,
                    "location": "",
                    "responsibilities": []
                }
            elif experience_item:
                # First non-date line is usually position
                if not experience_item["position"]:
                    parts = line.split(" at ")
                    if len(parts) > 1:
                        experience_item["position"] = parts[0].strip()
                        experience_item["company"] = parts[1].strip()
                    else:
                        experience_item["position"] = line
                else:
                    # Add as responsibility
                    experience_item["responsibilities"].append(line)
        
        elif current_section == "education":
            # Check if this is a new education entry
            if any(word in line.lower() for word in ["university", "college", "school", "institute"]):
                # Save previous education item if exists
                if education_item:
                    profile["education"].append(education_item)
                
                # Start new education item
                education_item = {
                    "institution": line,
                    "degree": "",
                    "graduation_date": ""
                }
            elif education_item:
                # First line after institution is usually degree
                if not education_item["degree"]:
                    # Check if line contains a year (likely graduation date)
                    if any(char.isdigit() for char in line):
                        parts = line.split(",")
                        if len(parts) > 1:
                            education_item["degree"] = parts[0].strip()
                            for part in parts[1:]:
                                if any(char.isdigit() for char in part):
                                    education_item["graduation_date"] = part.strip()
                    else:
                        education_item["degree"] = line
        
        elif current_section == "skills":
            # Add skills
            if "," in line:
                skills = [skill.strip() for skill in line.split(",")]
                profile["skills"]["technical"].extend(skills)
            else:
                profile["skills"]["technical"].append(line)
        
        elif current_section == "contact":
            # Try to identify contact info
            if "@" in line and "." in line:
                profile["personal_info"]["email"] = line
            elif any(char.isdigit() for char in line) and any(c in line for c in ["-", "+", "("]):
                profile["personal_info"]["phone"] = line
            elif line and not profile["personal_info"]["name"]:
                profile["personal_info"]["name"] = line
    
    # Add any remaining items
    if experience_item:
        profile["experience"].append(experience_item)
    if education_item:
        profile["education"].append(education_item)
    
    return profile

def suggest_missing_skills(job_analysis, profile):
    """
    Detect missing skills from the job analysis and suggest them to the user.
    Allows adding them to the profile with better feedback.
    """
    if not job_analysis or "match_analysis" not in job_analysis:
        st.warning("Please analyze a job first to get skill suggestions.")
        return
    
    # Extract missing skills
    missing_skills = job_analysis["match_analysis"].get("missing_skills", [])
    
    if not missing_skills:
        st.success("Your profile already covers all the key skills for this job!")
        return
    
    # Display missing skills
    st.write("Based on the job analysis, you might want to add these skills to your profile:")
    
    # Allow user to select which skills to add
    selected_skills = []
    for skill in missing_skills:
        if st.checkbox(f"Add '{skill}' to my profile", key=f"skill_{hash(skill)}"):
            selected_skills.append(skill)
    
    if selected_skills:
        st.subheader("Tell us about these skills")
        st.write("For each selected skill, please rate your proficiency level and provide details about your experience.")
        
        skill_details = {}
        for skill in selected_skills:
            st.write(f"### {skill}")
            proficiency = st.slider(
                f"Proficiency level for {skill}", 
                min_value=1, 
                max_value=5, 
                value=3, 
                help="1 = Beginner, 5 = Expert"
            )
            
            experience = st.text_area(
                f"Experience with {skill} (projects, work, education, etc.)",
                key=f"exp_{hash(skill)}"
            )
            
            skill_details[skill] = {
                "proficiency": proficiency,
                "experience": experience
            }
        
        # Add skills to profile
        if st.button("Add Selected Skills to Profile"):
            # Make sure profile has proper structure
            if not isinstance(profile, dict):
                profile = {}
            
            if "skills" not in profile:
                profile["skills"] = {}
            
            if "technical" not in profile["skills"]:
                profile["skills"]["technical"] = []
            
            # Keep track of skills for summary
            existing_skills = set(profile["skills"]["technical"])
            
            # Add new skills
            profile["skills"]["technical"].extend(selected_skills)
            
            # Make sure there are no duplicates
            profile["skills"]["technical"] = list(set(profile["skills"]["technical"]))
            
            # Count new skills added
            new_skills_added = len(set(profile["skills"]["technical"]) - existing_skills)
            
            # Update experience section with skill details if provided
            experiences_added = False
            skill_experience_details = []
            
            for skill, details in skill_details.items():
                if details["experience"]:
                    # Create or update a special section for skill experiences
                    if "skill_experiences" not in profile:
                        profile["skill_experiences"] = {}
                    
                    profile["skill_experiences"][skill] = details
                    experiences_added = True
                    
                    # Add to details for summary
                    skill_experience_details.append({
                        "skill": skill,
                        "proficiency": details["proficiency"],
                        "experience": details["experience"]
                    })
            
            # Update session state
            st.session_state['profile'] = profile
            
            # Success message with better feedback
            st.success(f"✅ Added {new_skills_added} new skills to your profile!")
            
            # Show a human-readable summary instead of JSON
            st.subheader("Skills Added:")
            for skill in selected_skills:
                st.markdown(f"- **{skill}** (Proficiency: {'⭐' * skill_details[skill]['proficiency']})")
                
                # Show truncated experience if provided
                if skill_details[skill]['experience']:
                    exp_text = skill_details[skill]['experience']
                    if len(exp_text) > 100:
                        exp_text = exp_text[:100] + "..."
                    st.markdown(f"  *Experience:* {exp_text}")
            
            # Show detailed profile only as an option
            with st.expander("View Updated Profile Details"):
                st.json(profile)
            
            # Recalculate match score with updated profile
            if st.button("Recalculate Job Match with Updated Profile"):
                # Get the model ID to use for analysis
                model_id = st.session_state['get_model_id']('analysis')
                
                with st.spinner(f"Reanalyzing job fit using {model_id}..."):
                    updated_match_analysis = analyze_job_fit(
                        st.session_state['openrouter_client'], 
                        st.session_state['job_analysis']['job_data'], 
                        profile
                    )
                    
                    if "error" not in updated_match_analysis:
                        # Update the analysis
                        st.session_state['job_analysis']['match_analysis'] = updated_match_analysis
                        
                        # Show improvement
                        old_score = job_analysis["match_analysis"].get("overall_match", 0)
                        new_score = updated_match_analysis.get("overall_match", 0)
                        
                        if new_score > old_score:
                            st.success(f"🎉 Your match score improved from {old_score}/10 to {new_score}/10!")
                        else:
                            st.info(f"Your updated match score is {new_score}/10")
                        
                        # Show new match percentage
                        st.write(f"Skills Match: {updated_match_analysis.get('skills_match', 'N/A')}")
    
    return profile

def export_profile(profile):
    """
    Allow the user to export their profile as a JSON file.
    """
    if not profile:
        st.warning("No profile available to export.")
        return
    
    # Create a JSON string
    try:
        profile_json = json.dumps(profile, indent=2)
        
        # Create download button
        st.download_button(
            label="Download Profile as JSON",
            data=profile_json,
            file_name="my_profile.json",
            mime="application/json"
        )
        
        # Also provide copy option
        with st.expander("Copy Profile JSON"):
            st.code(profile_json, language="json")
            
    except Exception as e:
        st.error(f"Error exporting profile: {str(e)}")

# Main app
def main():
    st.title("Smart Job Application Assistant")
    
    # Initialize session state
    if 'show_all_models' not in st.session_state:
        st.session_state['show_all_models'] = False
        
    if 'model_analysis' not in st.session_state:
        st.session_state['model_analysis'] = "balanced"
        
    if 'model_generation' not in st.session_state:
        st.session_state['model_generation'] = "creative"
    
    # Setup API client in sidebar
    client = setup_api()
    
    # Initialize session state for storing profile
    if 'profile' not in st.session_state:
        st.session_state['profile'] = None
    
    if 'job_data' not in st.session_state:
        st.session_state['job_data'] = None
        
    if 'job_analysis' not in st.session_state:
        st.session_state['job_analysis'] = None
        
    if 'application_docs' not in st.session_state:
        st.session_state['application_docs'] = None
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Job Analysis", "Generate Documents", "Application Tracker"])
    
    # Tab 1: Profile Management
    with tab1:
        st.header("Professional Profile")
        
        # Method selection
        profile_method = st.radio(
            "How would you like to create your profile?",
            ["Upload Document", "Interactive Builder", "Load Example", "Use Existing"]
        )
        
        if profile_method == "Upload Document":
            st.info("Upload a resume, CV, or profile in any format (PDF, DOCX, JSON, TXT), and we'll extract your professional information.")
            
            uploaded_file = st.file_uploader("Upload your document", 
                                            type=["pdf", "docx", "json", "txt"])
            
            if uploaded_file:
                file_type = uploaded_file.type
                
                # Get file extension from name if type is not specific enough
                file_extension = uploaded_file.name.split(".")[-1].lower() if "." in uploaded_file.name else ""
                
                if st.button("Process Document"):
                    with st.spinner("Processing your document..."):
                        # Handle different file types
                        if file_type == "application/pdf" or file_extension == "pdf":
                            # Process PDF
                            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
                            extracted_text = ""
                            for page in pdf_reader.pages:
                                extracted_text += page.extract_text()
                                
                            # Display raw text for debugging
                            with st.expander("Debug - Extracted Text"):
                                st.text(extracted_text)
                            
                            if client:
                                # Use AI to extract info
                                profile_data = extract_info_from_resume(client, uploaded_file)
                            else:
                                # Fallback to basic extraction
                                profile_data = extract_profile_from_text(extracted_text)
                        
                        elif file_type == "application/json" or file_extension == "json":
                            # Process JSON file
                            try:
                                json_content = uploaded_file.getvalue().decode('utf-8')
                                # Display raw JSON for debugging
                                with st.expander("Debug - Raw JSON content"):
                                    st.code(json_content, language="json")
                                
                                # Parse the JSON
                                raw_data = json.loads(json_content)
                                
                                # Convert to standard profile format
                                profile_data = convert_professional_database_to_profile(raw_data)
                                
                                if "error" in profile_data:
                                    st.error(f"Error processing JSON: {profile_data['error']}")
                                    profile_data = None
                                
                            except json.JSONDecodeError as e:
                                st.error(f"Failed to parse JSON file: {str(e)}")
                                profile_data = None
                            except Exception as e:
                                st.error(f"Error processing file: {str(e)}")
                                profile_data = None
                        
                        elif file_type == "text/plain" or file_extension == "txt":
                            # Process plain text
                            extracted_text = uploaded_file.getvalue().decode('utf-8')
                            
                            # Display raw text for debugging
                            with st.expander("Debug - Extracted Text"):
                                st.text(extracted_text)
                                
                            if client:
                                # Use AI to extract structure
                                profile_data = client.chat_completion(
                                    model=get_recommended_models()[st.session_state.get('model_analysis', 'balanced')],
                                    messages=[
                                        {"role": "system", "content": "Extract structured professional profile information from this text. Return as JSON."},
                                        {"role": "user", "content": f"Extract key professional details from this text into a structured JSON with personal_info, skills, education, experience, etc.:\n\n{extracted_text[:10000]}"}
                                    ]
                                )
                                
                                try:
                                    content = profile_data['choices'][0]['message']['content']
                                    # Extract JSON if it's wrapped in code blocks
                                    if "```" in content:
                                        match = re.search(r'```(?:json)?\s*(.*?)```', content, re.DOTALL)
                                        if match:
                                            content = match.group(1)
                                    profile_data = json.loads(content)
                                except:
                                    # Fallback to basic extraction
                                    profile_data = extract_profile_from_text(extracted_text)
                            else:
                                # Fallback to basic extraction
                                profile_data = extract_profile_from_text(extracted_text)
                        
                        else:
                            st.error(f"Unsupported file type: {file_type}")
                            profile_data = None
                        
                        # If profile was successfully extracted
                        if profile_data:
                            # Validate/enhance profile format
                            if not isinstance(profile_data, dict):
                                st.error("Invalid profile format extracted")
                            elif "personal_info" not in profile_data:
                                st.warning("Profile is missing personal information. Some features may not work correctly.")
                            elif "skills" not in profile_data:
                                st.warning("Profile is missing skills. This will affect job matching.")
                            
                            # Show the processed profile
                            st.success("Profile extracted successfully!")
                            st.json(profile_data)
                            
                            # Save to session state
                            st.session_state['profile'] = profile_data
                    
        elif profile_method == "Interactive Builder" and client:
            st.info("Let's build your profile step by step. Fill in as much information as you can for better job matching.")
            
            # Create tabs for different profile sections
            personal_tab, skills_tab, exp_tab, edu_tab = st.tabs(["Personal Info", "Skills", "Experience", "Education"])
            
            with personal_tab:
                st.subheader("Personal Information")
                
                # Initialize profile in session state if it doesn't exist
                if 'building_profile' not in st.session_state:
                    st.session_state['building_profile'] = {
                        "personal_info": {
                            "name": "",
                            "email": "",
                            "phone": "",
                            "location": ""
                        },
                        "skills": {
                            "technical": [],
                            "soft_skills": []
                        },
                        "experience": [],
                        "education": []
                    }
                
                # Personal info form
                st.session_state['building_profile']['personal_info']['name'] = st.text_input(
                    "Full Name", 
                    value=st.session_state['building_profile']['personal_info'].get('name', '')
                )
                
                st.session_state['building_profile']['personal_info']['email'] = st.text_input(
                    "Email", 
                    value=st.session_state['building_profile']['personal_info'].get('email', '')
                )
                
                st.session_state['building_profile']['personal_info']['phone'] = st.text_input(
                    "Phone", 
                    value=st.session_state['building_profile']['personal_info'].get('phone', '')
                )
                
                st.session_state['building_profile']['personal_info']['location'] = st.text_input(
                    "Location", 
                    value=st.session_state['building_profile']['personal_info'].get('location', '')
                )
            
            with skills_tab:
                st.subheader("Skills")
                
                # Technical skills
                st.write("What are your technical skills? (separated by commas)")
                skills_text = st.text_area(
                    "Technical Skills", 
                    value=', '.join(st.session_state['building_profile']['skills'].get('technical', []))
                )
                if skills_text:
                    st.session_state['building_profile']['skills']['technical'] = [
                        skill.strip() for skill in skills_text.split(',') if skill.strip()
                    ]
                
                # Soft skills
                st.write("What are your soft skills? (separated by commas)")
                soft_skills_text = st.text_area(
                    "Soft Skills", 
                    value=', '.join(st.session_state['building_profile']['skills'].get('soft_skills', []))
                )
                if soft_skills_text:
                    st.session_state['building_profile']['skills']['soft_skills'] = [
                        skill.strip() for skill in soft_skills_text.split(',') if skill.strip()
                    ]
                
                # Certifications
                st.write("Do you have any certifications? (separated by commas)")
                cert_text = st.text_area(
                    "Certifications", 
                    value=', '.join(st.session_state['building_profile']['skills'].get('certifications', []))
                )
                if cert_text:
                    st.session_state['building_profile']['skills']['certifications'] = [
                        cert.strip() for cert in cert_text.split(',') if cert.strip()
                    ]
            
            with exp_tab:
                st.subheader("Work Experience")
                
                # Display existing experience
                if st.session_state['building_profile']['experience']:
                    st.write("Current Experience Entries:")
                    for i, exp in enumerate(st.session_state['building_profile']['experience']):
                        st.markdown(f"**{exp.get('position', '')} at {exp.get('company', '')}** ({exp.get('duration', '')})")
                        if st.button(f"Remove Entry #{i+1}"):
                            st.session_state['building_profile']['experience'].pop(i)
                            st.experimental_rerun()
                
                # Form for adding new experience
                st.write("Add New Experience:")
                new_exp = {
                    "company": st.text_input("Company Name"),
                    "position": st.text_input("Position/Title"),
                    "duration": st.text_input("Duration (e.g., 2021-Present)"),
                    "location": st.text_input("Location"),
                    "responsibilities": []
                }
                
                # Responsibilities and achievements
                resp_text = st.text_area("Responsibilities (one per line)")
                if resp_text:
                    new_exp["responsibilities"] = [r.strip() for r in resp_text.split('\n') if r.strip()]
                
                achieve_text = st.text_area("Achievements (one per line)")
                if achieve_text:
                    new_exp["achievements"] = [a.strip() for a in achieve_text.split('\n') if a.strip()]
                
                if st.button("Add Experience Entry"):
                    if new_exp["company"] and new_exp["position"]:
                        st.session_state['building_profile']['experience'].append(new_exp)
                        st.success("Experience added!")
                        st.experimental_rerun()
                    else:
                        st.error("Please enter at least a company name and position")
            
            with edu_tab:
                st.subheader("Education")
                
                # Display existing education
                if st.session_state['building_profile']['education']:
                    st.write("Current Education Entries:")
                    for i, edu in enumerate(st.session_state['building_profile']['education']):
                        st.markdown(f"**{edu.get('degree', '')}** from {edu.get('institution', '')}")
                        if st.button(f"Remove Education #{i+1}"):
                            st.session_state['building_profile']['education'].pop(i)
                            st.experimental_rerun()
                
                # Form for adding new education
                st.write("Add New Education:")
                new_edu = {
                    "institution": st.text_input("Institution Name"),
                    "degree": st.text_input("Degree/Qualification"),
                    "graduation_date": st.text_input("Graduation Year"),
                    "relevant_coursework": []
                }
                
                # Coursework
                course_text = st.text_area("Relevant Courses (one per line)")
                if course_text:
                    new_edu["relevant_coursework"] = [c.strip() for c in course_text.split('\n') if c.strip()]
                
                if st.button("Add Education Entry"):
                    if new_edu["institution"] and new_edu["degree"]:
                        st.session_state['building_profile']['education'].append(new_edu)
                        st.success("Education added!")
                        st.experimental_rerun()
                    else:
                        st.error("Please enter at least an institution and degree")
            
            # Final save button
            st.markdown("---")
            if st.button("Finalize Profile"):
                if st.session_state['building_profile']['personal_info']['name']:
                    # Save to main profile in session state
                    st.session_state['profile'] = st.session_state['building_profile']
                    st.success("Profile created successfully!")
                    
                    # Display final profile
                    st.json(st.session_state['profile'])
                else:
                    st.error("Please enter at least your name in the Personal Info tab")
        
        elif profile_method == "Load Example":
            st.info("Load one of our example profiles to see how the job matching works.")
            example_choice = st.radio(
                "Choose an example profile:",
                ["Software Developer", "Marketing Specialist", "Graphic Designer", "Data Analyst"]
            )
            
            if st.button("Load Example Profile"):
                if example_choice == "Software Developer":
                    # Software Developer profile
                    example_profile = {
                        "personal_info": {
                            "name": "Alex Taylor",
                            "email": "example@email.com",
                            "phone": "555-123-4567",
                            "location": "San Francisco, California",
                            "linkedin": "linkedin.com/in/example",
                            "github": "github.com/example"
                        },
                        "skills": {
                            "technical": [
                                "Python",
                                "JavaScript",
                                "React",
                                "Node.js",
                                "TypeScript",
                                "Docker",
                                "AWS",
                                "Git",
                                "REST APIs",
                                "SQL",
                                "MongoDB",
                                "CI/CD",
                                "Test-driven Development",
                                "Microservices Architecture"
                            ],
                            "soft_skills": [
                                "Problem Solving",
                                "Teamwork",
                                "Communication",
                                "Time Management",
                                "Adaptability"
                            ],
                            "certifications": [
                                "AWS Certified Developer",
                                "Scrum Master Certification"
                            ]
                        },
                        "education": [
                            {
                                "institution": "University of California, Berkeley",
                                "degree": "Bachelor of Science in Computer Science",
                                "graduation_date": "2019",
                                "gpa": "3.8/4.0",
                                "relevant_coursework": [
                                    "Data Structures",
                                    "Algorithms",
                                    "Web Development",
                                    "Database Systems",
                                    "Machine Learning"
                                ]
                            }
                        ],
                        "experience": [
                            {
                                "company": "TechStartup Inc.",
                                "position": "Full Stack Developer",
                                "duration": "2020-Present",
                                "location": "San Francisco, CA",
                                "responsibilities": [
                                    "Develop and maintain web applications using React, Node.js, and MongoDB",
                                    "Implement CI/CD pipelines for automated testing and deployment",
                                    "Collaborate with product managers to define feature specifications",
                                    "Improve application performance and optimize database queries",
                                    "Mentor junior developers and conduct code reviews"
                                ],
                                "achievements": [
                                    "Reduced page load times by 40% through code optimization",
                                    "Led migration from monolith to microservices architecture",
                                    "Implemented automated testing that caught 95% of bugs before deployment"
                                ]
                            },
                            {
                                "company": "GlobalTech Solutions",
                                "position": "Software Engineering Intern",
                                "duration": "2019-2020",
                                "location": "San Jose, CA",
                                "responsibilities": [
                                    "Assisted in developing RESTful APIs using Python Flask",
                                    "Created unit tests for backend services",
                                    "Worked with front-end team to integrate APIs with React components",
                                    "Documented code and API endpoints"
                                ],
                                "achievements": [
                                    "Developed a dashboard feature that became part of the core product",
                                    "Received outstanding intern recognition award"
                                ]
                            }
                        ],
                        "projects": [
                            {
                                "title": "Personal Finance Tracker",
                                "description": "Built a web application that helps users track expenses, set budgets, and visualize spending patterns",
                                "technologies": ["React", "Firebase", "Chart.js", "Node.js"],
                                "url": "github.com/example/finance-tracker"
                            },
                            {
                                "title": "Community Event Finder",
                                "description": "Created a mobile-responsive app that aggregates local community events and allows filtering by category and location",
                                "technologies": ["React Native", "MongoDB", "Express", "Google Maps API"],
                                "url": "github.com/example/event-finder"
                            }
                        ],
                        "languages": [
                            {"language": "English", "proficiency": "Native"},
                            {"language": "Spanish", "proficiency": "Intermediate"}
                        ],
                        "interests": [
                            "Open source contribution",
                            "Mobile app development",
                            "Machine learning",
                            "Hackathons",
                            "Tech meetups"
                        ]
                    }
                    
                elif example_choice == "Marketing Specialist":
                    # Marketing Specialist profile
                    example_profile = {
                        "personal_info": {
                            "name": "Jordan Rivera",
                            "email": "example@email.com",
                            "phone": "555-987-6543",
                            "location": "Chicago, Illinois",
                            "linkedin": "linkedin.com/in/example",
                            "website": "example-portfolio.com"
                        },
                        "skills": {
                            "technical": [
                                "Social Media Marketing",
                                "Content Strategy",
                                "SEO/SEM",
                                "Email Marketing",
                                "Google Analytics",
                                "HubSpot",
                                "Mailchimp",
                                "Adobe Creative Suite",
                                "WordPress",
                                "A/B Testing",
                                "Data Analysis",
                                "Campaign Management",
                                "CRM Software",
                                "Marketing Automation"
                            ],
                            "soft_skills": [
                                "Creative Thinking",
                                "Project Management",
                                "Cross-functional Collaboration",
                                "Client Communication",
                                "Presentation Skills",
                                "Copywriting",
                                "Brand Storytelling"
                            ],
                            "certifications": [
                                "Google Analytics Certification",
                                "HubSpot Inbound Marketing",
                                "Facebook Blueprint Certification"
                            ]
                        },
                        "education": [
                            {
                                "institution": "Northwestern University",
                                "degree": "Bachelor of Science in Marketing",
                                "graduation_date": "2018",
                                "gpa": "3.7/4.0",
                                "relevant_coursework": [
                                    "Digital Marketing",
                                    "Consumer Behavior",
                                    "Brand Management",
                                    "Marketing Analytics",
                                    "Digital Content Creation"
                                ]
                            }
                        ],
                        "experience": [
                            {
                                "company": "Horizon Marketing Agency",
                                "position": "Digital Marketing Specialist",
                                "duration": "2020-Present",
                                "location": "Chicago, IL",
                                "responsibilities": [
                                    "Develop and implement digital marketing strategies for 12+ clients",
                                    "Create and manage social media content calendars across platforms",
                                    "Run Google Ads and social media advertising campaigns",
                                    "Generate monthly performance reports using analytics tools",
                                    "Optimize website content for SEO and conversion rates",
                                    "Collaborate with design team on content creation"
                                ],
                                "achievements": [
                                    "Increased client conversion rates by an average of 35%",
                                    "Reduced cost-per-acquisition by 28% across client accounts",
                                    "Grew social media engagement by 150% for key accounts"
                                ]
                            },
                            {
                                "company": "Global Retail Brands",
                                "position": "Marketing Coordinator",
                                "duration": "2018-2020",
                                "location": "Chicago, IL",
                                "responsibilities": [
                                    "Assisted in planning and executing email marketing campaigns",
                                    "Maintained website content using WordPress",
                                    "Helped coordinate promotional events and trade shows",
                                    "Collaborated with product teams on launch strategies",
                                    "Tracked campaign performance and prepared reports"
                                ],
                                "achievements": [
                                    "Helped achieve 22% growth in email subscriber base",
                                    "Redesigned newsletter template resulting in 15% higher open rates",
                                    "Supported successful launch of 5 product lines"
                                ]
                            }
                        ],
                        "projects": [
                            {
                                "title": "Nonprofit Rebrand Campaign",
                                "description": "Led pro-bono rebranding project for local environmental nonprofit including website redesign and social media strategy",
                                "results": "Increased volunteer sign-ups by 45% and online donations by 30%"
                            },
                            {
                                "title": "E-commerce Launch Strategy",
                                "description": "Developed comprehensive digital marketing strategy for new direct-to-consumer brand launch",
                                "results": "Achieved 200% of first-quarter sales targets and 15k+ Instagram followers within 3 months"
                            }
                        ],
                        "languages": [
                            {"language": "English", "proficiency": "Native"},
                            {"language": "French", "proficiency": "Conversational"}
                        ],
                        "interests": [
                            "Digital content creation",
                            "Consumer psychology",
                            "Brand storytelling",
                            "Marketing technology",
                            "Sustainable marketing practices"
                        ]
                    }
                    
                elif example_choice == "Graphic Designer":
                    # Graphic Designer profile
                    example_profile = {
                        "personal_info": {
                            "name": "Morgan Chen",
                            "email": "example@email.com",
                            "phone": "555-234-5678",
                            "location": "New York, NY",
                            "linkedin": "linkedin.com/in/example",
                            "portfolio": "example-design.com"
                        },
                        "skills": {
                            "technical": [
                                "Adobe Photoshop",
                                "Adobe Illustrator",
                                "Adobe InDesign",
                                "Adobe XD",
                                "Figma",
                                "Sketch",
                                "UI/UX Design",
                                "Typography",
                                "Color Theory",
                                "Brand Identity Design",
                                "Packaging Design",
                                "Digital Illustration",
                                "Motion Graphics",
                                "HTML/CSS Basics",
                                "Print Production"
                            ],
                            "soft_skills": [
                                "Creative Problem Solving",
                                "Client Communication",
                                "Visual Storytelling",
                                "Attention to Detail",
                                "Meeting Deadlines",
                                "Giving/Receiving Critique",
                                "Cross-functional Collaboration"
                            ],
                            "certifications": [
                                "Adobe Certified Professional",
                                "UI/UX Design Certificate - Design School NY"
                            ]
                        },
                        "education": [
                            {
                                "institution": "Rhode Island School of Design",
                                "degree": "Bachelor of Fine Arts in Graphic Design",
                                "graduation_date": "2019",
                                "gpa": "3.9/4.0",
                                "relevant_coursework": [
                                    "Typography",
                                    "Brand Identity",
                                    "Package Design",
                                    "Digital Media",
                                    "Information Design",
                                    "Interactive Design"
                                ]
                            }
                        ],
                        "experience": [
                            {
                                "company": "Creative Partners Agency",
                                "position": "Senior Graphic Designer",
                                "duration": "2021-Present",
                                "location": "New York, NY",
                                "responsibilities": [
                                    "Create visual concepts for client campaigns across digital and print media",
                                    "Design logos, brand identities, and style guides for diverse clients",
                                    "Develop UI designs for websites and mobile applications",
                                    "Collaborate with marketing team on campaign concepts and execution",
                                    "Present design concepts and iterations to clients",
                                    "Mentor junior designers and provide art direction"
                                ],
                                "achievements": [
                                    "Designed award-winning packaging system for consumer product line",
                                    "Led rebranding project that resulted in 40% increase in client engagement",
                                    "Created design system that improved team efficiency by 25%"
                                ]
                            },
                            {
                                "company": "Metro Digital Magazine",
                                "position": "Junior Graphic Designer",
                                "duration": "2019-2021",
                                "location": "Boston, MA",
                                "responsibilities": [
                                    "Designed layouts for print and digital magazine issues",
                                    "Created social media graphics and promotional materials",
                                    "Collaborated with editorial team on visual storytelling",
                                    "Prepared files for print production",
                                    "Assisted with photoshoots and image editing"
                                ],
                                "achievements": [
                                    "Redesigned magazine template increasing newsstand sales by 18%",
                                    "Created social media templates that boosted engagement by 35%",
                                    "Received Society of Publication Designers award for editorial spread"
                                ]
                            }
                        ],
                        "projects": [
                            {
                                "title": "Brand Identity for Sustainable Startup",
                                "description": "Developed complete brand identity including logo, color palette, typography, and applications for eco-friendly product line",
                                "url": "example-design.com/sustainable-brand"
                            },
                            {
                                "title": "Mobile App UI Design",
                                "description": "Created user interface design for fitness tracking application including wireframes, prototypes, and final UI components",
                                "url": "example-design.com/fitness-app"
                            }
                        ],
                        "languages": [
                            {"language": "English", "proficiency": "Native"},
                            {"language": "Mandarin", "proficiency": "Fluent"}
                        ],
                        "interests": [
                            "Typography",
                            "Sustainable design",
                            "Interactive experiences",
                            "Art exhibitions",
                            "Design history"
                        ]
                    }
                    
                elif example_choice == "Data Analyst":
                    # Data Analyst profile
                    example_profile = {
                        "personal_info": {
                            "name": "Sam Washington",
                            "email": "example@email.com",
                            "phone": "555-876-5432",
                            "location": "Austin, Texas",
                            "linkedin": "linkedin.com/in/example",
                            "github": "github.com/example"
                        },
                        "skills": {
                            "technical": [
                                "SQL",
                                "Python",
                                "R",
                                "Tableau",
                                "Power BI",
                                "Excel (Advanced)",
                                "Data Visualization",
                                "Statistical Analysis",
                                "A/B Testing",
                                "Data Cleaning",
                                "ETL Processes",
                                "Database Management",
                                "Machine Learning Basics",
                                "Google Analytics",
                                "Big Query",
                                "Pandas",
                                "NumPy",
                                "Scikit-learn"
                            ],
                            "soft_skills": [
                                "Analytical Thinking",
                                "Problem Solving",
                                "Data Storytelling",
                                "Business Acumen",
                                "Cross-functional Communication",
                                "Attention to Detail",
                                "Project Management"
                            ],
                            "certifications": [
                                "Google Data Analytics Professional Certificate",
                                "Microsoft Power BI Data Analyst",
                                "Tableau Desktop Specialist"
                            ]
                        },
                        "education": [
                            {
                                "institution": "University of Texas at Austin",
                                "degree": "Bachelor of Science in Statistics",
                                "graduation_date": "2020",
                                "gpa": "3.8/4.0",
                                "relevant_coursework": [
                                    "Data Analysis",
                                    "Probability and Statistics",
                                    "Database Systems",
                                    "Data Mining",
                                    "Business Intelligence",
                                    "Programming for Data Science"
                                ]
                            }
                        ],
                        "experience": [
                            {
                                "company": "TechData Solutions",
                                "position": "Data Analyst",
                                "duration": "2021-Present",
                                "location": "Austin, TX",
                                "responsibilities": [
                                    "Analyze large datasets to identify trends and business insights",
                                    "Create interactive dashboards and reports using Tableau and Power BI",
                                    "Develop and maintain SQL queries for data extraction and analysis",
                                    "Collaborate with product and marketing teams to define metrics",
                                    "Perform A/B testing and statistical analysis to optimize user experience",
                                    "Automate reporting processes using Python scripts"
                                ],
                                "achievements": [
                                    "Identified pricing optimization opportunity that increased revenue by 15%",
                                    "Reduced reporting time by 70% through process automation",
                                    "Created customer segmentation model that improved marketing ROI by 25%"
                                ]
                            },
                            {
                                "company": "Retail Analytics Inc.",
                                "position": "Junior Data Analyst",
                                "duration": "2020-2021",
                                "location": "Austin, TX",
                                "responsibilities": [
                                    "Assisted with data collection, cleaning, and preparation",
                                    "Generated regular sales and inventory reports",
                                    "Tracked KPIs and created visualizations in Excel and Tableau",
                                    "Supported market research initiatives with data analysis",
                                    "Helped identify data quality issues and implemented solutions"
                                ],
                                "achievements": [
                                    "Developed inventory forecasting model that reduced stockouts by 30%",
                                    "Created automated Excel dashboard used by entire sales team",
                                    "Identified data anomaly that saved company $50,000 in misbilled orders"
                                ]
                            }
                        ],
                        "projects": [
                            {
                                "title": "Customer Churn Prediction Model",
                                "description": "Developed machine learning model to predict customer churn using historical data",
                                "technologies": ["Python", "Scikit-learn", "Pandas", "Matplotlib"],
                                "url": "github.com/example/churn-prediction"
                            },
                            {
                                "title": "Sales Performance Dashboard",
                                "description": "Created interactive Tableau dashboard visualizing sales performance by region, product, and time period",
                                "technologies": ["Tableau", "SQL", "Excel"],
                                "url": "public.tableau.com/example/sales-dashboard"
                            }
                        ],
                        "languages": [
                            {"language": "English", "proficiency": "Native"},
                            {"language": "Spanish", "proficiency": "Intermediate"}
                        ],
                        "interests": [
                            "Data visualization",
                            "Predictive analytics",
                            "Business intelligence",
                            "Open data initiatives",
                            "Statistical modeling"
                        ]
                    }
                
                st.session_state['profile'] = example_profile
                st.success(f"{example_choice} example profile loaded!")
                
                # Show profile summary
                with st.expander("Profile Summary"):
                    st.write(f"### {example_profile['personal_info']['name']}")
                    st.write(f"**Location:** {example_profile['personal_info']['location']}")
                    
                    st.write("### Skills")
                    st.write(f"**Technical:** {', '.join(example_profile['skills']['technical'][:5])} ...")
                    st.write(f"**Soft Skills:** {', '.join(example_profile['skills']['soft_skills'][:3])} ...")
                    
                    st.write("### Experience")
                    for exp in example_profile['experience']:
                        st.write(f"**{exp['position']}** at {exp['company']} ({exp['duration']})")
                    
                    st.write("### Education")
                    for edu in example_profile['education']:
                        st.write(f"**{edu['degree']}** from {edu['institution']}")
        
        elif profile_method == "Use Existing":
            if st.session_state.get('profile'):
                st.json(st.session_state['profile'])
                if st.button("Clear Existing Profile"):
                    st.session_state['profile'] = None
                    st.experimental_rerun()
            else:
                st.warning("No existing profile found. Please create one first.")
                
        # Profile summary if available
        if st.session_state.get('profile'):
            with st.expander("Current Profile Summary"):
                profile = st.session_state['profile']
                
                st.write("### Personal Information")
                for key, value in profile.get('personal_info', {}).items():
                    if key != 'websites' and value:
                        st.write(f"**{key.title()}:** {value}")
                
                st.write("### Skills")
                for category, skills in profile.get('skills', {}).items():
                    if skills:
                        st.write(f"**{category.replace('_', ' ').title()}:** {', '.join(skills)}")
                
                st.write("### Experience")
                for exp in profile.get('experience', []):
                    st.write(f"**{exp.get('position')}** at {exp.get('company')} ({exp.get('duration')})")
                
                st.write("### Education")
                for edu in profile.get('education', []):
                    st.write(f"**{edu.get('degree')}** from {edu.get('institution')} ({edu.get('graduation_date')})")
    
    # Tab 2: Job Analysis
    with tab2:
        st.header("Job Analysis")
        
        if not st.session_state['profile']:
            st.warning("Please create your profile first in the Profile tab")
        elif not client:
            st.warning("Please enter your OpenRouter API key in the sidebar")
        else:
            # Create three columns
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Single text field for entire job posting
                st.write("Paste the full job posting below (title, company, description, etc.)")
                job_posting = st.text_area("Job Posting", height=300)
                
                if job_posting and st.button("Analyze Job"):
                    if len(job_posting.strip()) < 50:
                        st.error("Please paste a more complete job posting")
                    else:
                        # Process the job posting
                        with st.spinner("Processing job posting..."):
                            job_data = process_job_posting(client, job_posting)
                            
                        if "error" in job_data:
                            st.error(f"Error processing job: {job_data['error']}")
                        else:
                            st.success("Job posting processed successfully!")
                            
                            # Display basic job info
                            st.subheader(job_data["title"])
                            st.write(f"Company: {job_data['company']}")
                            
                            if "location" in job_data and job_data['location'] != "Unknown":
                                st.write(f"Location: {job_data['location']}")
                                
                            if "job_type" in job_data and job_data['job_type'] != "Unknown":
                                st.write(f"Job Type: {job_data['job_type']}")
                            
                            # Store in session state
                            st.session_state['job_data'] = job_data
                            
                            # Get the model ID to use for analysis
                            model_id = st.session_state['get_model_id']('analysis')
                            
                            # Analyze match
                            with st.spinner(f"Analyzing job fit using {model_id}..."):
                                match_analysis = analyze_job_fit(client, job_data, st.session_state['profile'])
                                
                            if "error" in match_analysis:
                                st.error(f"Error analyzing job: {match_analysis['error']}")
                            else:
                                # Display match analysis
                                st.subheader("Match Analysis")
                                st.write(f"Overall Match Score: {match_analysis.get('overall_match', 'N/A')}/10")
                                st.write(f"Skills Match: {match_analysis.get('skills_match', 'N/A')}")
                                
                                # Create columns for matching and missing skills
                                match_col, miss_col = st.columns(2)
                                
                                with match_col:
                                    st.write("🟢 Matching Skills:")
                                    for skill in match_analysis.get('matching_skills', []):
                                        st.write(f"✓ {skill}")
                                
                                with miss_col:
                                    st.write("🔴 Missing Skills:")
                                    for skill in match_analysis.get('missing_skills', []):
                                        st.write(f"✗ {skill}")
                                    
                                # Show explanation
                                if "explanation" in match_analysis:
                                    st.write("Analysis:")
                                    st.write(match_analysis["explanation"])
                                    
                                # Save complete analysis
                                st.session_state['job_analysis'] = {
                                    "job_data": job_data,
                                    "match_analysis": match_analysis
                                }
            
            with col2:
                # Show skill suggestions and profile export if job has been analyzed
                if 'job_analysis' in st.session_state and st.session_state['job_analysis']:
                    st.subheader("Improve Your Profile")
                    
                    # Skill suggestion tab
                    skill_tab, export_tab = st.tabs(["Add Missing Skills", "Export Profile"])
                    
                    with skill_tab:
                        # Use the suggest_missing_skills function
                        suggest_missing_skills(st.session_state['job_analysis'], st.session_state['profile'])
                    
                    with export_tab:
                        # Use the export_profile function
                        export_profile(st.session_state['profile'])
                else:
                    st.info("Analyze a job to see skill suggestions and export options")
    
    # Tab 3: Generate Documents
    with tab3:
        st.header("Application Documents")
        
        if 'job_analysis' not in st.session_state or not st.session_state['job_analysis']:
            st.warning("Please analyze a job first in the Job Analysis tab")
        elif not client:
            st.warning("Please enter your OpenRouter API key in the sidebar")
        else:
            # Get model ID for document generation
            model_id = st.session_state['get_model_id']('generation')
            
            if st.button("Generate Application Documents"):
                with st.spinner(f"Generating tailored documents using {model_id}..."):
                    try:
                        # Generate application documents with the selected model
                        # First, generate cover letter with explicit model ID
                        cover_letter_prompt = f"""
                        Create a brief, enthusiastic cover letter for a {st.session_state['job_analysis']['job_data']['title']} position at {st.session_state['job_analysis']['job_data']['company']}.

                        THE FOLLOWING INFORMATION IS THE ONLY FACTUAL INFORMATION YOU CAN USE:
                        
                        CANDIDATE DETAILS:
                        Name: {st.session_state['profile'].get('personal_info', {}).get('name', '')}
                        Email: {st.session_state['profile'].get('personal_info', {}).get('email', '')}
                        Phone: {st.session_state['profile'].get('personal_info', {}).get('phone', '')}
                        Location: {st.session_state['profile'].get('personal_info', {}).get('location', '')}
                        
                        VERIFIED SKILLS (use ONLY these exact skills, do not fabricate or expand):
                        {json.dumps(st.session_state['profile'].get('skills', {}).get('technical', []))}
                        
                        VERIFIED WORK EXPERIENCE (use ONLY these exact companies and details, do not fabricate or expand):
                        {json.dumps(st.session_state['profile'].get('experience', []))}
                        
                        JOB REQUIREMENTS:
                        {st.session_state['job_analysis']['job_data']['description'][:800]}
                        
                        IMPORTANT INSTRUCTIONS:
                        1. Keep it SHORT (150-200 words maximum, about 3-4 short paragraphs)
                        2. Be enthusiastic and friendly, but professional
                        3. NEVER include ANY placeholders like "[Your Name]"
                        4. NEVER fabricate work experience or skills - use ONLY what's provided above
                        5. If a real company name isn't provided above, DO NOT make one up - refer to roles generically
                        6. Only include details explicitly listed in the VERIFIED sections
                        7. Do not expand on bullet points with specifics not provided above
                        8. Keep it direct and engaging for busy hiring managers
                        9. End with "Sincerely," followed by the name only if provided
                        
                        Use ONLY the facts provided above - no fabrication whatsoever.
                        """
                        
                        cover_letter_response = client.chat_completion(
                            model=model_id,
                            messages=[
                                {"role": "system", "content": "You are a strictly factual resume writer who uses ONLY the exact information provided. You NEVER fabricate experience, companies, or achievements. You do not elaborate beyond the given facts."},
                                {"role": "user", "content": cover_letter_prompt}
                            ]
                        )
                        
                        cover_letter_content = cover_letter_response['choices'][0]['message']['content']
                        
                        # Generate resume bullets - fixed the JSON example format
                        resume_prompt = """
                        Create tailored resume bullet points for a {} position at {}.
                        
                        USE ONLY THESE EXACT WORK EXPERIENCES (do not fabricate or expand):
                        {}
                        
                        JOB REQUIREMENTS:
                        {}
                        
                        INSTRUCTIONS:
                        1. For each position, create 3 powerful bullet points
                        2. Each bullet should be ONE LINE only (15 words maximum)
                        3. Start with strong ACTION VERBS
                        4. ONLY use responsibilities and achievements explicitly listed above
                        5. DO NOT fabricate or add details not provided in the work experience
                        6. If no achievements are provided for a role, focus on responsibilities only
                        
                        Return as JSON with position titles as keys and arrays of bullet points as values.
                        Return ONLY valid JSON with no explanations or markdown formatting.
                        Example format: {{"Position Title": ["Bullet 1", "Bullet 2", "Bullet 3"]}}
                        """.format(
                            st.session_state['job_analysis']['job_data']['title'],
                            st.session_state['job_analysis']['job_data']['company'],
                            json.dumps(st.session_state['profile'].get('experience', [])),
                            st.session_state['job_analysis']['job_data']['description'][:800]
                        )
                        
                        resume_response = client.chat_completion(
                            model=model_id,
                            messages=[
                                {"role": "system", "content": "You create powerful resume content using ONLY the exact information provided. You NEVER fabricate experience, roles, or achievements. Return ONLY JSON."},
                                {"role": "user", "content": resume_prompt}
                            ]
                        )
                        
                        resume_content = resume_response['choices'][0]['message']['content']
                        
                        # Extract JSON if it's wrapped in code blocks
                        if "```" in resume_content:
                            match = re.search(r'```(?:json)?\s*(.*?)```', resume_content, re.DOTALL)
                            if match:
                                resume_content = match.group(1).strip()
                                
                        try:
                            resume_bullets = json.loads(resume_content)
                            
                            docs = {
                                "cover_letter": cover_letter_content,
                                "resume_bullets": resume_bullets
                            }
                            
                            # Store in session state
                            st.session_state['application_docs'] = docs
                            
                            # Display documents
                            st.subheader("Cover Letter")
                            st.text_area("Copy or edit as needed:", docs["cover_letter"], height=300)
                            
                            # Show resume bullets
                            st.subheader("Tailored Resume Bullets")
                            for exp, bullets in docs["resume_bullets"].items():
                                st.write(f"**{exp}**")
                                for bullet in bullets:
                                    st.write(f"• {bullet}")
                                    
                            # Save to tracker
                            save_button = st.button("Save Application")
                            if save_button:
                                result = save_application(
                                    st.session_state['job_analysis'],
                                    st.session_state['application_docs']
                                )
                                st.success(result)
                        except json.JSONDecodeError as e:
                            st.error(f"Error parsing resume bullets: {str(e)}")
                            st.code(resume_content, language="json")
                    except Exception as e:
                        st.error(f"Error generating documents: {str(e)}")
                        st.error("Please try a different model or check your OpenRouter API key.")
    
    # Tab 4: Application Tracker
    with tab4:
        st.header("Application Tracker")
        
        try:
            applications_df = pd.read_csv("job_applications.csv")
            st.dataframe(applications_df[["date", "company", "position", "match_score", "status"]])
            
            # Allow status updates
            if not applications_df.empty:
                selected_app = st.selectbox(
                    "Select application to update:",
                    applications_df["position"] + " at " + applications_df["company"]
                )
                
                if selected_app:
                    idx = applications_df.index[applications_df["position"] + " at " + applications_df["company"] == selected_app][0]
                    new_status = st.selectbox(
                        "Update status:",
                        ["Ready to Apply", "Applied", "Interview Scheduled", "Rejected", "Offer Received", "Accepted"]
                    )
                    
                    if st.button("Update Status"):
                        applications_df.at[idx, "status"] = new_status
                        applications_df.to_csv("job_applications.csv", index=False)
                        st.success("Status updated successfully!")
                        st.experimental_rerun()
            else:
                st.info("No applications found. Add some applications first.")
                    
        except FileNotFoundError:
            st.info("No applications tracked yet.")
        except Exception as e:
            st.error(f"Error loading applications: {str(e)}")

if __name__ == "__main__":
    main()