"""
Job description parsers for different job sites.
This module contains specialized parsers for popular job listing sites.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def parse_seek_job(url):
    """
    Parser for seek.com.au job listings
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Job title
    try:
        job_title = soup.find('h1', class_='yvsb870 _14uh9944i').text.strip()
    except:
        try:
            job_title = soup.find('h1').text.strip()
        except:
            job_title = "Unknown Position"
    
    # Company name
    try:
        company = soup.find('span', class_='_y1frqlc').text.strip()
    except:
        try:
            company = soup.find('span', class_='_1tkhm9a8').text.strip()
        except:
            company = urlparse(url).netloc.replace('www.', '').split('.')[0].capitalize()
    
    # Job description
    try:
        description_div = soup.find('div', attrs={'data-automation': 'jobAdDetails'})
        description = description_div.text.strip() if description_div else ""
    except:
        description = ""
        
    if not description:
        try:
            description_div = soup.find('div', class_='yvsb870 _14uh9947m')
            description = description_div.text.strip() if description_div else ""
        except:
            description = ""
    
    # Location
    try:
        location = soup.find('div', attrs={'data-automation': 'job-location'}).text.strip()
    except:
        location = "Unknown Location"
        
    # Job type
    try:
        job_type = soup.find('div', attrs={'data-automation': 'job-work-type'}).text.strip()
    except:
        job_type = "Not specified"
        
    return {
        "title": job_title,
        "company": company,
        "description": description,
        "location": location,
        "job_type": job_type,
        "url": url
    }
    
def parse_indeed_job(url):
    """
    Parser for indeed.com job listings
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Job title
    try:
        job_title = soup.find('h1', class_='jobsearch-JobInfoHeader-title').text.strip()
    except:
        try:
            job_title = soup.find('h1').text.strip()
        except:
            job_title = "Unknown Position"
    
    # Company name
    try:
        company = soup.find('div', class_='jobsearch-InlineCompanyRating').find('a').text.strip()
    except:
        try:
            company = soup.find('div', class_='icl-u-lg-mr--sm').text.strip()
        except:
            company = urlparse(url).netloc.replace('www.', '').split('.')[0].capitalize()
    
    # Job description
    try:
        description_div = soup.find('div', id='jobDescriptionText')
        description = description_div.text.strip() if description_div else ""
    except:
        description = ""
    
    # Location
    try:
        location = soup.find('div', class_='jobsearch-JobInfoHeader-subtitle').find_all('div')[1].text.strip()
    except:
        location = "Unknown Location"
        
    # Job type
    try:
        job_type = soup.find('div', class_='jobsearch-JobDescriptionSection-sectionItem').find('div').text.strip()
    except:
        job_type = "Not specified"
        
    return {
        "title": job_title,
        "company": company,
        "description": description,
        "location": location,
        "job_type": job_type,
        "url": url
    }
    
def parse_linkedin_job(url):
    """
    Parser for LinkedIn job listings
    Note: LinkedIn may have protections against scraping that limit functionality
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Job title
    try:
        job_title = soup.find('h1', class_='top-card-layout__title').text.strip()
    except:
        try:
            job_title = soup.find('h1').text.strip()
        except:
            job_title = "Unknown Position"
    
    # Company name
    try:
        company = soup.find('a', class_='topcard__org-name-link').text.strip()
    except:
        try:
            company = soup.find('span', class_='topcard__flavor').text.strip()
        except:
            company = urlparse(url).netloc.replace('www.', '').split('.')[0].capitalize()
    
    # Job description
    try:
        description_div = soup.find('div', class_='show-more-less-html__markup')
        description = description_div.text.strip() if description_div else ""
    except:
        description = ""
    
    # Location
    try:
        location = soup.find('span', class_='topcard__flavor--bullet').text.strip()
    except:
        location = "Unknown Location"
        
    # Job type is typically within the description for LinkedIn
    job_type = "Not specified"
        
    return {
        "title": job_title,
        "company": company,
        "description": description,
        "location": location,
        "job_type": job_type,
        "url": url
    }

def parse_generic_job(url):
    """
    Generic parser that attempts to extract job information from any site
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Job title - typically in h1 or h2 tags
    job_title = "Unknown Position"
    for tag in ['h1', 'h2']:
        if soup.find(tag):
            job_title = soup.find(tag).text.strip()
            break
    
    # Company name - look for common patterns or extract from domain
    company = ""
    for company_class in ['company', 'organization', 'employer', 'company-name']:
        company_element = soup.find(['span', 'div', 'a'], class_=lambda x: x and company_class in x.lower())
        if company_element:
            company = company_element.text.strip()
            break
    
    if not company:
        company = urlparse(url).netloc.replace('www.', '').split('.')[0].capitalize()
    
    # Job description - look for content divs
    description = ""
    for desc_class in ['description', 'job-description', 'details', 'content', 'job_description', 'jobdescription']:
        desc_div = soup.find(['div', 'section'], class_=lambda x: x and desc_class in x.lower())
        if desc_div:
            description = desc_div.text.strip()
            break
    
    # If no specific div found, try to get main content
    if not description:
        main_content = soup.find('main') or soup.find('article') or soup.body
        if main_content:
            description = main_content.text.strip()
    
    # Location - look for location indicators
    location = "Unknown Location"
    for loc_class in ['location', 'job-location', 'city', 'address']:
        loc_elem = soup.find(['span', 'div'], class_=lambda x: x and loc_class in x.lower())
        if loc_elem:
            location = loc_elem.text.strip()
            break
    
    # Job type
    job_type = "Not specified"
    for type_class in ['job-type', 'employment-type', 'work-type']:
        type_elem = soup.find(['span', 'div'], class_=lambda x: x and type_class in x.lower())
        if type_elem:
            job_type = type_elem.text.strip()
            break
    
    return {
        "title": job_title,
        "company": company,
        "description": description,
        "location": location,
        "job_type": job_type,
        "url": url
    }

def get_appropriate_parser(url):
    """
    Determine which parser to use based on the URL
    """
    domain = urlparse(url).netloc.lower()
    
    if 'seek.com' in domain:
        return parse_seek_job
    elif 'indeed.com' in domain:
        return parse_indeed_job
    elif 'linkedin.com' in domain:
        return parse_linkedin_job
    else:
        return parse_generic_job