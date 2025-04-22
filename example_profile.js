# Add this function to load the example profile

def load_example_profile():
    """Load the example profile provided with the application"""
    # Example profile based on the example_profile.js from the repository
    example_profile = {
      "personal_info": {
        "name": "Alex Johnson",
        "email": "alex.johnson@example.com",
        "phone": "555-123-4567",
        "location": "Melbourne, Australia",
        "linkedin": "linkedin.com/in/alexjohnson",
        "portfolio": "alexjohnson.portfolio.com"
      },
      "skills": {
        "technical": [
          "AutoCAD",
          "SolidWorks",
          "Fusion 360",
          "CATIA",
          "Python",
          "MATLAB",
          "FEA Analysis",
          "3D Printing"
        ],
        "soft_skills": [
          "Project Management",
          "Team Leadership",
          "Problem Solving",
          "Client Communication",
          "Technical Documentation",
          "Quality Assurance"
        ],
        "certifications": [
          "Certified SolidWorks Professional (CSWP)",
          "Six Sigma Green Belt",
          "Project Management Professional (PMP)"
        ]
      },
      "education": [
        {
          "institution": "University of Melbourne",
          "degree": "Bachelor of Engineering (Mechanical)",
          "graduation_date": "2021",
          "gpa": "3.8/4.0",
          "relevant_coursework": [
            "Machine Design",
            "Thermodynamics",
            "Fluid Mechanics",
            "Materials Science",
            "Robotics"
          ]
        },
        {
          "institution": "RMIT University",
          "degree": "Certificate in Industrial Design",
          "graduation_date": "2022",
          "relevant_coursework": [
            "Product Development",
            "Design Thinking",
            "Manufacturing Processes"
          ]
        }
      ],
      "experience": [
        {
          "company": "TechInnovate Solutions",
          "position": "Mechanical Design Engineer",
          "duration": "2021-Present",
          "location": "Melbourne, Australia",
          "responsibilities": [
            "Designed mechanical components for industrial automation systems using SolidWorks",
            "Collaborated with electrical engineers to develop integrated systems",
            "Conducted structural and thermal analyses using FEA software",
            "Created detailed manufacturing drawings and specifications",
            "Managed prototype development and testing phases"
          ],
          "achievements": [
            "Reduced production costs by 15% through design optimization",
            "Led team of 3 junior engineers for major client project",
            "Implemented new design review process that improved quality metrics by 20%"
          ]
        },
        {
          "company": "GlobalManufacturing Inc.",
          "position": "Mechanical Engineering Intern",
          "duration": "2020-2021",
          "location": "Sydney, Australia",
          "responsibilities": [
            "Assisted senior engineers with CAD modeling and drawing creation",
            "Conducted product testing and documented results",
            "Participated in design review meetings and provided input",
            "Researched materials and components for new product development"
          ],
          "achievements": [
            "Developed an automated testing fixture that reduced testing time by 30%",
            "Recognized for exceptional attention to detail in documentation"
          ]
        }
      ],
      "projects": [
        {
          "title": "Automated Sorting System",
          "description": "Designed and built a small-scale automated sorting system using Arduino, sensors, and custom 3D printed components",
          "technologies": ["Arduino", "CAD", "3D Printing", "Python"],
          "url": "github.com/alexj/sorting-system"
        },
        {
          "title": "Energy-Efficient HVAC Controller",
          "description": "Developed a smart HVAC control system that optimized energy usage based on occupancy and environmental factors",
          "technologies": ["IoT", "MATLAB", "Thermodynamic Modeling"],
          "url": "alexjohnson.portfolio.com/hvac-project"
        }
      ],
      "languages": [
        {"language": "English", "proficiency": "Native"},
        {"language": "Mandarin", "proficiency": "Conversational"}
      ],
      "interests": [
        "Sustainable product design",
        "Additive manufacturing",
        "Renewable energy systems",
        "Robotics competitions",
        "Open-source hardware"
      ]
    }
    
    return example_profile

# Then update the Profile tab to include the "Load Example" option
# Add this inside the Tab 1 section, after the "Use Existing" option

elif profile_method == "Load Example":
    if st.button("Load Example Profile"):
        st.session_state['profile'] = load_example_profile()
        st.success("Example profile loaded!")
        st.json(st.session_state['profile'])