#  Helper functions for CareerBot
import PyPDF2
from docx import Document
import re
import os
from groq import Groq

def calculate_readiness_score(user_data):
    """
    Calculate Career Readiness Score based on user profile
    Returns a score out of 100 and breakdown by category
    
    Parameters:
    user_data (dict): Dictionary containing user information
        - has_resume: Boolean
        - resume_length: Integer (word count)
        - skills_count: Integer (number of skills listed)
        - experience_years: Float
        - has_projects: Boolean
        - projects_count: Integer
    """
    
    # Initialize scores for each category
    resume_score = 0
    skills_score = 0
    experience_score = 0
    projects_score = 0
    
    # Calculate Resume Quality Score (out of 25 points)
    if user_data.get('has_resume', False):
        resume_score += 10  # Has a resume
        
        # Check resume length (optimal: 400-600 words)
        resume_length = user_data.get('resume_length', 0)
        if resume_length >= 400 and resume_length <= 600:
            resume_score += 15  # Perfect length
        elif resume_length >= 300 and resume_length < 800:
            resume_score += 10  # Acceptable length
        elif resume_length > 0:
            resume_score += 5   # Has content but needs work
    
    # Calculate Skills Score (out of 25 points)
    skills_count = user_data.get('skills_count', 0)
    if skills_count >= 8:
        skills_score = 25  # Strong skill set
    elif skills_count >= 5:
        skills_score = 20  # Good skill set
    elif skills_count >= 3:
        skills_score = 15  # Moderate skills
    elif skills_count > 0:
        skills_score = 10  # Basic skills
    
    # Calculate Experience Score (out of 25 points)
    experience_years = user_data.get('experience_years', 0)
    if experience_years >= 3:
        experience_score = 25  # Experienced professional
    elif experience_years >= 1:
        experience_score = 20  # Some experience
    elif experience_years >= 0.5:
        experience_score = 15  # Internship/fresher with some exposure
    else:
        experience_score = 10  # Fresh graduate (still valuable!)
    
    # Calculate Projects Score (out of 25 points)
    if user_data.get('has_projects', False):
        projects_count = user_data.get('projects_count', 0)
        if projects_count >= 5:
            projects_score = 25  # Impressive portfolio
        elif projects_count >= 3:
            projects_score = 20  # Strong portfolio
        elif projects_count >= 1:
            projects_score = 15  # Good start
    else:
        projects_score = 5  # Needs projects
    
    # Calculate total score
    total_score = resume_score + skills_score + experience_score + projects_score
    
    # Create breakdown dictionary
    breakdown = {
        'resume_quality': resume_score,
        'skills_match': skills_score,
        'experience_level': experience_score,
        'project_portfolio': projects_score,
        'total_score': total_score
    }
    
    # Generate personalized feedback based on score
    feedback = generate_feedback(breakdown)
    
    return {
        'score': total_score,
        'breakdown': breakdown,
        'feedback': feedback
    }


def generate_feedback(breakdown):
    """
    Generate personalized feedback based on score breakdown
    """
    feedback = []
    
    # Resume feedback
    if breakdown['resume_quality'] < 15:
        feedback.append("Your resume needs improvement. Focus on making it ATS-friendly and concise.")
    elif breakdown['resume_quality'] < 20:
        feedback.append("Your resume is good but could be optimized further.")
    else:
        feedback.append("Great resume quality! Keep it updated with recent achievements.")
    
    # Skills feedback
    if breakdown['skills_match'] < 15:
        feedback.append("Add more relevant skills to your profile. Aim for at least 5-8 key skills.")
    elif breakdown['skills_match'] < 20:
        feedback.append("Good skill set. Consider learning trending technologies in your field.")
    else:
        feedback.append("Excellent skill portfolio! Keep learning to stay ahead.")
    
    # Experience feedback
    if breakdown['experience_level'] < 15:
        feedback.append("Gain experience through internships, freelancing, or personal projects.")
    elif breakdown['experience_level'] < 20:
        feedback.append("Your experience is building up. Document your achievements clearly.")
    else:
        feedback.append("Strong professional experience! Highlight your impact in each role.")
    
    # Projects feedback
    if breakdown['project_portfolio'] < 15:
        feedback.append("Build more projects! They demonstrate your practical skills to employers.")
    elif breakdown['project_portfolio'] < 20:
        feedback.append("Good project portfolio. Add detailed descriptions and live demos.")
    else:
        feedback.append("Impressive project portfolio! Make sure they're accessible on GitHub.")
    
    return feedback


def get_readiness_level(score):
    """
    Convert numerical score to readiness level
    """
    if score >= 80:
        return "Highly Ready"
    elif score >= 60:
        return "Ready with Minor Improvements"
    elif score >= 40:
        return "Developing Readiness"
    else:
        return "Needs Significant Preparation"
def extract_skills_from_job(job_description):
    """
    Extract technical skills from a job description
    Returns a list of identified skills
    
    Parameters:
    job_description (str): The job description text
    """
    
    # Common technical skills database
    # In a real app, this would be much larger or use AI
    skills_database = {
        # Programming Languages
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift',
        'kotlin', 'go', 'rust', 'typescript', 'r', 'matlab', 'scala',
        
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
        'django', 'flask', 'fastapi', 'spring', 'asp.net', 'jquery',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
        'oracle', 'dynamodb', 'sqlite', 'nosql',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'tensorflow', 'pytorch',
        'scikit-learn', 'pandas', 'numpy', 'data analysis', 'statistics',
        'nlp', 'computer vision', 'keras', 'data science',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
        'git', 'github', 'gitlab', 'ci/cd', 'terraform', 'ansible',
        
        # Other Tools
        'excel', 'power bi', 'tableau', 'jira', 'agile', 'scrum',
        'linux', 'bash', 'api', 'rest', 'graphql', 'microservices'
    }
    
    # Convert job description to lowercase for matching
    job_text = job_description.lower()
    
    # Find matching skills
    found_skills = []
    for skill in skills_database:
        if skill in job_text:
            found_skills.append(skill.title())  # Capitalize for display
    
    # Remove duplicates and sort
    found_skills = sorted(list(set(found_skills)))
    
    return found_skills


def analyze_skill_gap(user_skills, required_skills):
    """
    Compare user skills with job requirements
    Returns analysis with matching and missing skills
    
    Parameters:
    user_skills (list): List of skills user has
    required_skills (list): List of skills required by job
    """
    
    # Convert to lowercase for comparison
    user_skills_lower = [skill.lower() for skill in user_skills]
    required_skills_lower = [skill.lower() for skill in required_skills]
    
    # Find matching skills
    matching_skills = []
    for skill in required_skills:
        if skill.lower() in user_skills_lower:
            matching_skills.append(skill)
    
    # Find missing skills
    missing_skills = []
    for skill in required_skills:
        if skill.lower() not in user_skills_lower:
            missing_skills.append(skill)
    
    # Calculate readiness percentage
    if len(required_skills) > 0:
        readiness_percentage = (len(matching_skills) / len(required_skills)) * 100
    else:
        readiness_percentage = 0
    
    # Determine readiness level
    if readiness_percentage >= 80:
        readiness_status = "Highly Ready"
        recommendation = "You have most required skills! Apply with confidence."
    elif readiness_percentage >= 60:
        readiness_status = "Ready with Minor Gaps"
        recommendation = "You're qualified! Learn the missing skills while applying."
    elif readiness_percentage >= 40:
        readiness_status = "Moderately Ready"
        recommendation = "Spend 2-3 weeks learning key missing skills before applying."
    else:
        readiness_status = "Needs Preparation"
        recommendation = "Focus on building foundational skills first."
    
    return {
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'readiness_percentage': round(readiness_percentage, 1),
        'readiness_status': readiness_status,
        'recommendation': recommendation,
        'total_required': len(required_skills),
        'total_matching': len(matching_skills),
        'total_missing': len(missing_skills)
    }


def get_learning_resources(skill):
    """
    Provide free learning resources for a skill
    Returns a list of resources with links
    
    Parameters:
    skill (str): The skill to find resources for
    """
    
    # Basic resource database
    # In production, this would be more comprehensive
    resources = {
        'python': [
            {'name': 'Python.org Tutorial', 'url': 'https://docs.python.org/3/tutorial/', 'type': 'Documentation'},
            {'name': 'freeCodeCamp Python Course', 'url': 'https://www.freecodecamp.org/', 'type': 'Course'},
        ],
        'javascript': [
            {'name': 'MDN JavaScript Guide', 'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide', 'type': 'Documentation'},
            {'name': 'JavaScript.info', 'url': 'https://javascript.info/', 'type': 'Tutorial'},
        ],
        'react': [
            {'name': 'Official React Docs', 'url': 'https://react.dev/', 'type': 'Documentation'},
            {'name': 'freeCodeCamp React', 'url': 'https://www.freecodecamp.org/', 'type': 'Course'},
        ],
        'sql': [
            {'name': 'SQLBolt', 'url': 'https://sqlbolt.com/', 'type': 'Interactive Tutorial'},
            {'name': 'W3Schools SQL', 'url': 'https://www.w3schools.com/sql/', 'type': 'Tutorial'},
        ],
        'machine learning': [
            {'name': 'Google ML Crash Course', 'url': 'https://developers.google.com/machine-learning/crash-course', 'type': 'Course'},
            {'name': 'Kaggle Learn', 'url': 'https://www.kaggle.com/learn', 'type': 'Interactive'},
        ],
    }
    
    # Return resources for the skill or generic resources
    skill_lower = skill.lower()
    if skill_lower in resources:
        return resources[skill_lower]
    else:
        # Generic resources for any skill
        return [
            {'name': 'YouTube Tutorials', 'url': f'https://www.youtube.com/results?search_query={skill}+tutorial', 'type': 'Video'},
            {'name': 'freeCodeCamp', 'url': 'https://www.freecodecamp.org/', 'type': 'Course'},
            {'name': 'Coursera Free Courses', 'url': f'https://www.coursera.org/search?query={skill}', 'type': 'Course'},
        ]
import PyPDF2
from docx import Document
import re


def extract_text_from_pdf(file_path):
    """
    Extract text content from a PDF file
    
    Parameters:
    file_path (str): Path to the PDF file
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            # Extract text from all pages
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")


def extract_text_from_docx(file_path):
    """
    Extract text content from a Word document
    
    Parameters:
    file_path (str): Path to the DOCX file
    """
    try:
        doc = Document(file_path)
        # Extract text from all paragraphs
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")


def analyze_resume(resume_text):
    """
    Analyze resume and provide detailed feedback
    Returns scores and recommendations
    
    Parameters:
    resume_text (str): The extracted resume text
    """
    
    # Initialize scores (each category out of 20 points)
    scores = {
        'length_score': 0,
        'keywords_score': 0,
        'formatting_score': 0,
        'contact_info_score': 0,
        'action_verbs_score': 0
    }
    
    feedback = []
    
    # Calculate word count
    word_count = len(resume_text.split())
    
    # 1. Length Analysis (20 points)
    if word_count >= 400 and word_count <= 600:
        scores['length_score'] = 20
        feedback.append("✓ Perfect length! Your resume is concise and complete.")
    elif word_count >= 300 and word_count < 400:
        scores['length_score'] = 15
        feedback.append("⚠ Resume is a bit short. Add more details about your achievements.")
    elif word_count > 600 and word_count <= 800:
        scores['length_score'] = 15
        feedback.append("⚠ Resume is slightly long. Try to be more concise.")
    elif word_count > 800:
        scores['length_score'] = 10
        feedback.append("✗ Resume is too long! Recruiters spend only 6 seconds. Cut it down.")
    else:
        scores['length_score'] = 5
        feedback.append("✗ Resume is too short. Add more relevant experience and skills.")
    
    # 2. Keywords Analysis (20 points)
    # Check for important resume keywords
    important_keywords = [
        'experience', 'education', 'skills', 'project', 'achievement',
        'developed', 'managed', 'led', 'created', 'implemented'
    ]
    
    keywords_found = 0
    resume_lower = resume_text.lower()
    
    for keyword in important_keywords:
        if keyword in resume_lower:
            keywords_found += 1
    
    keyword_percentage = (keywords_found / len(important_keywords)) * 100
    
    if keyword_percentage >= 70:
        scores['keywords_score'] = 20
        feedback.append("✓ Great use of important keywords! ATS systems will love this.")
    elif keyword_percentage >= 50:
        scores['keywords_score'] = 15
        feedback.append("⚠ Good keywords, but add more action verbs and achievements.")
    else:
        scores['keywords_score'] = 10
        feedback.append("✗ Missing important keywords. Add more action verbs and specific achievements.")
    
    # 3. Formatting Check (20 points)
    # Check for bullet points or organized structure
    has_bullets = '•' in resume_text or '-' in resume_text or '*' in resume_text
    has_sections = any(section in resume_lower for section in ['experience', 'education', 'skills', 'projects'])
    
    if has_bullets and has_sections:
        scores['formatting_score'] = 20
        feedback.append("✓ Well-structured with clear sections and bullet points.")
    elif has_sections:
        scores['formatting_score'] = 15
        feedback.append("⚠ Good sections, but use bullet points for better readability.")
    else:
        scores['formatting_score'] = 10
        feedback.append("✗ Poor structure. Add clear sections: Experience, Education, Skills, Projects.")
    
    # 4. Contact Information (20 points)
    # Check for email, phone, and LinkedIn
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
    has_phone = bool(re.search(r'\d{10}|\d{3}[-.\s]\d{3}[-.\s]\d{4}', resume_text))
    has_linkedin = 'linkedin' in resume_lower
    
    contact_count = sum([has_email, has_phone, has_linkedin])
    
    if contact_count >= 3:
        scores['contact_info_score'] = 20
        feedback.append("✓ Complete contact information provided.")
    elif contact_count >= 2:
        scores['contact_info_score'] = 15
        feedback.append("⚠ Add LinkedIn profile for better networking opportunities.")
    else:
        scores['contact_info_score'] = 10
        feedback.append("✗ Missing contact information! Add email, phone, and LinkedIn.")
    
    # 5. Action Verbs Analysis (20 points)
    strong_action_verbs = [
        'achieved', 'improved', 'increased', 'reduced', 'developed',
        'created', 'implemented', 'designed', 'led', 'managed',
        'optimized', 'built', 'launched', 'generated', 'delivered'
    ]
    
    action_verbs_found = 0
    for verb in strong_action_verbs:
        if verb in resume_lower:
            action_verbs_found += 1
    
    if action_verbs_found >= 5:
        scores['action_verbs_score'] = 20
        feedback.append("✓ Excellent use of strong action verbs showing impact!")
    elif action_verbs_found >= 3:
        scores['action_verbs_score'] = 15
        feedback.append("⚠ Good action verbs, but use more to show your impact.")
    else:
        scores['action_verbs_score'] = 10
        feedback.append("✗ Weak language! Replace passive descriptions with strong action verbs.")
    
    # Calculate total score
    total_score = sum(scores.values())
    
    # Add overall assessment
    if total_score >= 85:
        overall = "Excellent resume! You're ready to apply with confidence."
    elif total_score >= 70:
        overall = "Good resume with minor improvements needed."
    elif total_score >= 50:
        overall = "Decent resume, but needs significant improvements."
    else:
        overall = "Your resume needs major work before applying to jobs."
    
    # Return complete analysis
    return {
        'total_score': total_score,
        'scores': scores,
        'feedback': feedback,
        'overall_assessment': overall,
        'word_count': word_count,
        'has_email': has_email,
        'has_phone': has_phone,
        'has_linkedin': has_linkedin
    }


def generate_resume_improvements(analysis):
    """
    Generate specific improvement suggestions based on analysis
    
    Parameters:
    analysis (dict): The resume analysis results
    """
    improvements = []
    
    scores = analysis['scores']
    
    # Length improvements
    if scores['length_score'] < 15:
        if analysis['word_count'] < 400:
            improvements.append({
                'category': 'Length',
                'issue': 'Resume is too short',
                'fix': 'Add more details about your projects, quantify your achievements, and expand on your responsibilities.'
            })
        else:
            improvements.append({
                'category': 'Length',
                'issue': 'Resume is too long',
                'fix': 'Remove unnecessary details, focus on recent and relevant experience, use concise bullet points.'
            })
    
    # Keywords improvements
    if scores['keywords_score'] < 15:
        improvements.append({
            'category': 'Keywords',
            'issue': 'Missing important keywords',
            'fix': 'Add action verbs like "developed", "implemented", "managed". Include technical skills and achievements.'
        })
    
    # Formatting improvements
    if scores['formatting_score'] < 15:
        improvements.append({
            'category': 'Formatting',
            'issue': 'Poor structure and formatting',
            'fix': 'Use clear sections: Summary, Experience, Education, Skills, Projects. Use bullet points, not paragraphs.'
        })
    
    # Contact info improvements
    if scores['contact_info_score'] < 15:
        improvements.append({
            'category': 'Contact Info',
            'issue': 'Incomplete contact information',
            'fix': 'Add: Professional email, phone number, LinkedIn profile, GitHub (for tech roles), portfolio link.'
        })
    
    # Action verbs improvements
    if scores['action_verbs_score'] < 15:
        improvements.append({
            'category': 'Impact',
            'issue': 'Weak language and no quantified results',
            'fix': 'Use strong verbs: "Increased sales by 30%", "Reduced costs by $50K", "Led team of 5 developers".'
        })
    
    return improvements

from datetime import datetime, timedelta
import json


def create_job_application(job_data):
    """
    Create a new job application entry
    
    Parameters:
    job_data (dict): Contains job details
        - company: Company name
        - position: Job title
        - job_url: Link to job posting
        - date_applied: Date of application
        - status: Current status (default: 'Applied')
    """
    
    # Generate unique ID based on timestamp
    application_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create application object
    application = {
        'id': application_id,
        'company': job_data.get('company', ''),
        'position': job_data.get('position', ''),
        'job_url': job_data.get('job_url', ''),
        'date_applied': job_data.get('date_applied', datetime.now().strftime('%Y-%m-%d')),
        'status': job_data.get('status', 'Applied'),
        'notes': job_data.get('notes', ''),
        'follow_up_date': calculate_follow_up_date(datetime.now()),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return application


def calculate_follow_up_date(application_date):
    """
    Calculate when to follow up (1 week after application)
    
    Parameters:
    application_date (datetime): Date when application was submitted
    """
    
    # Follow up after 7 days
    follow_up = application_date + timedelta(days=7)
    return follow_up.strftime('%Y-%m-%d')


def get_follow_up_reminders(applications, today_date=None):
    """
    Get list of applications that need follow-up
    
    Parameters:
    applications (list): List of all job applications
    today_date (str): Today's date in YYYY-MM-DD format
    """
    
    if today_date is None:
        today_date = datetime.now().strftime('%Y-%m-%d')
    
    today = datetime.strptime(today_date, '%Y-%m-%d')
    
    reminders = []
    
    for app in applications:
        # Only check applications in 'Applied' or 'Viewed' status
        if app['status'] in ['Applied', 'Viewed']:
            follow_up_date = datetime.strptime(app['follow_up_date'], '%Y-%m-%d')
            
            # Check if follow-up is due
            if follow_up_date <= today:
                days_overdue = (today - follow_up_date).days
                
                reminders.append({
                    'application': app,
                    'days_overdue': days_overdue,
                    'priority': 'High' if days_overdue > 3 else 'Medium'
                })
    
    # Sort by days overdue (most urgent first)
    reminders.sort(key=lambda x: x['days_overdue'], reverse=True)
    
    return reminders


def update_application_status(application, new_status):
    """
    Update the status of a job application
    
    Parameters:
    application (dict): The job application object
    new_status (str): New status value
    """
    
    valid_statuses = ['Applied', 'Viewed', 'Interview Scheduled', 'Interviewed', 'Rejected', 'Offer']
    
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
    
    application['status'] = new_status
    application['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update follow-up date based on status
    if new_status == 'Viewed':
        # Follow up in 3 days if they viewed your application
        application['follow_up_date'] = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    elif new_status == 'Interview Scheduled':
        # No follow-up needed
        application['follow_up_date'] = None
    elif new_status in ['Rejected', 'Offer']:
        # No follow-up needed for final statuses
        application['follow_up_date'] = None
    
    return application


def generate_follow_up_email(application):
    """
    Generate a follow-up email template
    
    Parameters:
    application (dict): The job application object
    """
    
    company = application['company']
    position = application['position']
    
    email_template = f"""Subject: Following Up on {position} Application

Dear Hiring Manager,

I hope this email finds you well. I recently applied for the {position} position at {company} and wanted to follow up on my application.

I am very excited about the opportunity to contribute to your team and believe my skills and experience align well with the role's requirements.

I would appreciate any update on the status of my application and would be happy to provide any additional information you may need.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
[Your Name]
[Your Email]
[Your Phone]
"""
    
    return email_template


def get_application_statistics(applications):
    """
    Generate statistics about job applications
    
    Parameters:
    applications (list): List of all job applications
    """
    
    total = len(applications)
    
    if total == 0:
        return {
            'total_applications': 0,
            'status_breakdown': {},
            'response_rate': 0,
            'pending_follow_ups': 0
        }
    
    # Count by status
    status_counts = {}
    for app in applications:
        status = app['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Calculate response rate (Viewed + Interview + Offer / Total)
    responded = status_counts.get('Viewed', 0) + status_counts.get('Interview Scheduled', 0) + \
                status_counts.get('Interviewed', 0) + status_counts.get('Offer', 0)
    response_rate = round((responded / total) * 100, 1) if total > 0 else 0
    
    # Count pending follow-ups
    pending = len(get_follow_up_reminders(applications))
    
    return {
        'total_applications': total,
        'status_breakdown': status_counts,
        'response_rate': response_rate,
        'pending_follow_ups': pending,
        'interviews': status_counts.get('Interview Scheduled', 0) + status_counts.get('Interviewed', 0),
        'offers': status_counts.get('Offer', 0),
        'rejections': status_counts.get('Rejected', 0)
    }
    
    # Initialize Groq client
def get_groq_client():
    """Initialize and return Groq client"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise Exception("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)


# Company-specific interview questions database
COMPANY_QUESTIONS = {
    'google': [
        "Tell me about a time you solved a complex technical problem.",
        "How would you design a scalable system for millions of users?",
        "Explain a technical concept to a non-technical person.",
        "Describe your approach to debugging a production issue."
    ],
    'amazon': [
        "Tell me about a time you failed and what you learned.",
        "Describe a situation where you had to work with limited resources.",
        "How do you prioritize tasks when everything is urgent?",
        "Tell me about a time you went above and beyond for a customer."
    ],
    'microsoft': [
        "How would you improve one of our products?",
        "Describe a time you had to learn a new technology quickly.",
        "How do you handle disagreements with team members?",
        "Tell me about a project you're most proud of."
    ],
    'startup': [
        "Why do you want to work at a startup?",
        "Describe a time you wore multiple hats to get something done.",
        "How do you handle ambiguity and rapid change?",
        "What would you do in your first 90 days here?"
    ],
    'general': [
        "Tell me about yourself.",
        "What are your greatest strengths and weaknesses?",
        "Where do you see yourself in 5 years?",
        "Why should we hire you?",
        "Tell me about a challenging project you worked on."
    ]
}


def get_interview_questions(company, role, num_questions=5):
    """
    Get interview questions based on company and role
    
    Parameters:
    company (str): Company name or type
    role (str): Job role
    num_questions (int): Number of questions to return
    """
    
    # Normalize company name
    company_lower = company.lower()
    
    # Select question set
    if 'google' in company_lower:
        questions = COMPANY_QUESTIONS['google'].copy()
    elif 'amazon' in company_lower:
        questions = COMPANY_QUESTIONS['amazon'].copy()
    elif 'microsoft' in company_lower:
        questions = COMPANY_QUESTIONS['microsoft'].copy()
    elif 'startup' in company_lower or 'small' in company_lower:
        questions = COMPANY_QUESTIONS['startup'].copy()
    else:
        questions = COMPANY_QUESTIONS['general'].copy()
    
    # Add role-specific questions
    role_lower = role.lower()
    if 'data' in role_lower or 'analyst' in role_lower:
        questions.append("How do you approach analyzing a large dataset?")
        questions.append("Explain a time you used data to drive a decision.")
    elif 'developer' in role_lower or 'engineer' in role_lower:
        questions.append("Describe your development workflow.")
        questions.append("How do you ensure code quality?")
    
    # Return requested number of questions
    import random
    random.shuffle(questions)
    return questions[:num_questions]


def analyze_interview_answer(question, answer):
    """
    Use AI to analyze the interview answer and provide feedback
    
    Parameters:
    question (str): The interview question
    answer (str): User's answer
    """
    
    try:
        client = get_groq_client()
        
        # Create prompt for AI analysis
        prompt = f"""You are an expert interview coach. Analyze this interview answer and provide constructive feedback.

Question: {question}

Candidate's Answer: {answer}

Provide feedback in the following format:
1. Content Score (1-10): Rate how well they answered the question
2. Communication Score (1-10): Rate clarity and structure
3. Strengths: List 2-3 things they did well
4. Areas for Improvement: List 2-3 specific suggestions
5. Better Answer Example: Provide a brief example of a stronger answer

Keep feedback honest but encouraging. Be specific and actionable."""

        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",  # Faster model
            temperature=0.7,
            max_tokens=300
        )
        
        # Extract response
        feedback = chat_completion.choices[0].message.content
        
        # Parse feedback (simple parsing)
        feedback_sections = {
            'raw_feedback': feedback,
            'content_score': extract_score(feedback, 'Content Score'),
            'communication_score': extract_score(feedback, 'Communication Score')
        }
        
        return feedback_sections
        
    except Exception as e:
        # Return fallback feedback if API fails
        return {
            'raw_feedback': f"Error: {str(e)}. Please check your API key.",
            'content_score': 5,
            'communication_score': 5
        }


def extract_score(text, score_name):
    """Helper function to extract score from feedback text"""
    import re
    pattern = f"{score_name}.*?(\d+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 5  # Default score


def detect_filler_words(answer):
    """
    Detect filler words in the answer
    
    Parameters:
    answer (str): User's answer text
    """
    
    filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'literally', 'kind of', 'sort of']
    
    answer_lower = answer.lower()
    found_fillers = {}
    
    for filler in filler_words:
        count = answer_lower.count(filler)
        if count > 0:
            found_fillers[filler] = count
    
    total_fillers = sum(found_fillers.values())
    
    # Calculate confidence score based on filler words
    word_count = len(answer.split())
    if word_count > 0:
        filler_percentage = (total_fillers / word_count) * 100
        confidence_score = max(0, 100 - (filler_percentage * 10))
    else:
        confidence_score = 0
    
    return {
        'filler_words': found_fillers,
        'total_fillers': total_fillers,
        'confidence_score': round(confidence_score, 1)
    }


def create_interview_session(company, role):
    """
    Create a new interview session
    
    Parameters:
    company (str): Company name
    role (str): Job role
    """
    
    from datetime import datetime
    
    session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    questions = get_interview_questions(company, role)
    
    session = {
        'session_id': session_id,
        'company': company,
        'role': role,
        'questions': questions,
        'current_question': 0,
        'answers': [],
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return session


def calculate_overall_score(session):
    """
    Calculate overall interview performance score
    
    Parameters:
    session (dict): Interview session with answers
    """
    
    if not session['answers']:
        return {
            'overall_score': 0,
            'content_avg': 0,
            'communication_avg': 0,
            'confidence_avg': 0
        }
    
    content_scores = []
    communication_scores = []
    confidence_scores = []
    
    for answer in session['answers']:
        content_scores.append(answer.get('content_score', 5))
        communication_scores.append(answer.get('communication_score', 5))
        confidence_scores.append(answer.get('confidence_score', 50))
    
    content_avg = sum(content_scores) / len(content_scores)
    communication_avg = sum(communication_scores) / len(communication_scores)
    confidence_avg = sum(confidence_scores) / len(confidence_scores)
    
    # Overall score (weighted average)
    overall = (content_avg * 10 * 0.4) + (communication_avg * 10 * 0.4) + (confidence_avg * 0.2)
    
    return {
        'overall_score': round(overall, 1),
        'content_avg': round(content_avg, 1),
        'communication_avg': round(communication_avg, 1),
        'confidence_avg': round(confidence_avg, 1)
    }