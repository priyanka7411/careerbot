# Main Flask application

from flask import Flask, render_template, request, jsonify
from utils import calculate_readiness_score, get_readiness_level
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for dashboard (home page)
@app.route('/')
def home():
    """Render the dashboard"""
    return render_template('dashboard.html')


# Route for Career Readiness Score page
@app.route('/readiness')
def readiness():
    """Render Career Readiness Score page"""
    return render_template('readiness.html')


# Route for Skills Gap Analyzer page
@app.route('/skills-gap')
def skills_gap():
    """Render Skills Gap Analyzer page"""
    return render_template('skills_gap.html')


# Route for Resume Roast Mode page
@app.route('/resume-roast')
def resume_roast():
    """Render Resume Roast Mode page"""
    return render_template('resume_roast.html')


# Route for Job Application Tracker page
@app.route('/job-tracker')
def job_tracker():
    """Render Job Application Tracker page"""
    return render_template('job_tracker.html')


# Route for Mock Interview page
@app.route('/mock-interview')
def mock_interview():
    """Render Mock Interview page"""
    return render_template('mock_interview.html')


# API endpoint to calculate readiness score
@app.route('/api/calculate-score', methods=['POST'])
def calculate_score():
    """
    API endpoint to calculate career readiness score
    Expects JSON data with user information
    """
    try:
        # Get data from request
        user_data = request.get_json()
        
        # Validate that we received data
        if not user_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Calculate the readiness score
        result = calculate_readiness_score(user_data)
        
        # Add readiness level to result
        result['readiness_level'] = get_readiness_level(result['score'])
        
        # Return the result as JSON
        return jsonify(result), 200
        
    except Exception as e:
        # Handle any errors
        return jsonify({'error': str(e)}), 500

# API endpoint to extract skills from job description
@app.route('/api/extract-skills', methods=['POST'])
def extract_skills():
    """
    Extract required skills from a job description
    Expects JSON with 'job_description' field
    """
    try:
        # Get job description from request
        data = request.get_json()
        job_description = data.get('job_description', '')
        
        # Validate input
        if not job_description or len(job_description.strip()) < 50:
            return jsonify({'error': 'Please provide a valid job description (at least 50 characters)'}), 400
        
        # Extract skills using our function
        from utils import extract_skills_from_job
        required_skills = extract_skills_from_job(job_description)
        
        # Return the extracted skills
        return jsonify({
            'required_skills': required_skills,
            'total_skills': len(required_skills)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to analyze skill gap
@app.route('/api/analyze-gap', methods=['POST'])
def analyze_gap():
    """
    Compare user skills with job requirements
    Expects JSON with 'user_skills' and 'required_skills' arrays
    """
    try:
        # Get data from request
        data = request.get_json()
        user_skills = data.get('user_skills', [])
        required_skills = data.get('required_skills', [])
        
        # Validate input
        if not user_skills:
            return jsonify({'error': 'Please provide your skills'}), 400
        if not required_skills:
            return jsonify({'error': 'Please provide required skills'}), 400
        
        # Analyze the gap
        from utils import analyze_skill_gap, get_learning_resources
        analysis = analyze_skill_gap(user_skills, required_skills)
        
        # Add learning resources for missing skills
        learning_paths = {}
        for skill in analysis['missing_skills'][:5]:  # Limit to first 5 skills
            learning_paths[skill] = get_learning_resources(skill)
        
        analysis['learning_resources'] = learning_paths
        
        # Return the analysis
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint to upload and analyze resume
@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume_endpoint():
    """
    Upload and analyze a resume file
    Accepts PDF or DOCX files
    """
    try:
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400
        
        # Save the file securely
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text based on file type
        from utils import extract_text_from_pdf, extract_text_from_docx, analyze_resume, generate_resume_improvements
        
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'pdf':
            resume_text = extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            resume_text = extract_text_from_docx(file_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        
        # Check if text was extracted
        if not resume_text or len(resume_text.strip()) < 50:
            return jsonify({'error': 'Could not extract text from resume or resume is too short'}), 400
        
        # Analyze the resume
        analysis = analyze_resume(resume_text)
        
        # Generate improvement suggestions
        improvements = generate_resume_improvements(analysis)
        analysis['improvements'] = improvements
        
        # Clean up - delete the uploaded file
        os.remove(file_path)
        
        # Return analysis results
        return jsonify(analysis), 200
        
    except Exception as e:
        # Clean up file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({'error': str(e)}), 500
    
# In-memory storage for job applications (in production, use a database)
job_applications = []


# API endpoint to add a new job application
@app.route('/api/add-application', methods=['POST'])
def add_application():
    """
    Add a new job application to track
    Expects JSON with job details
    """
    try:
        # Get job data from request
        job_data = request.get_json()
        
        # Validate required fields
        if not job_data.get('company'):
            return jsonify({'error': 'Company name is required'}), 400
        if not job_data.get('position'):
            return jsonify({'error': 'Position is required'}), 400
        
        # Create application
        from utils import create_job_application
        application = create_job_application(job_data)
        
        # Add to storage
        job_applications.append(application)
        
        return jsonify({
            'message': 'Application added successfully',
            'application': application
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to get all applications
@app.route('/api/get-applications', methods=['GET'])
def get_applications():
    """
    Get all job applications
    """
    try:
        # Sort by date (newest first)
        sorted_apps = sorted(job_applications, key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'applications': sorted_apps,
            'total': len(sorted_apps)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to update application status
@app.route('/api/update-status/<application_id>', methods=['PUT'])
def update_status(application_id):
    """
    Update the status of a job application
    """
    try:
        # Get new status from request
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        # Find the application
        application = None
        for app in job_applications:
            if app['id'] == application_id:
                application = app
                break
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Update status
        from utils import update_application_status
        updated_app = update_application_status(application, new_status)
        
        return jsonify({
            'message': 'Status updated successfully',
            'application': updated_app
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to delete an application
@app.route('/api/delete-application/<application_id>', methods=['DELETE'])
def delete_application(application_id):
    """
    Delete a job application
    """
    try:
        # Find and remove the application
        global job_applications
        original_length = len(job_applications)
        job_applications = [app for app in job_applications if app['id'] != application_id]
        
        if len(job_applications) == original_length:
            return jsonify({'error': 'Application not found'}), 404
        
        return jsonify({'message': 'Application deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to get follow-up reminders
@app.route('/api/get-reminders', methods=['GET'])
def get_reminders():
    """
    Get all pending follow-up reminders
    """
    try:
        from utils import get_follow_up_reminders
        reminders = get_follow_up_reminders(job_applications)
        
        return jsonify({
            'reminders': reminders,
            'count': len(reminders)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to get application statistics
@app.route('/api/get-statistics', methods=['GET'])
def get_statistics():
    """
    Get statistics about job applications
    """
    try:
        from utils import get_application_statistics
        stats = get_application_statistics(job_applications)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to generate follow-up email
@app.route('/api/generate-email/<application_id>', methods=['GET'])
def generate_email(application_id):
    """
    Generate a follow-up email template for an application
    """
    try:
        # Find the application
        application = None
        for app in job_applications:
            if app['id'] == application_id:
                application = app
                break
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Generate email
        from utils import generate_follow_up_email
        email_template = generate_follow_up_email(application)
        
        return jsonify({
            'email_template': email_template,
            'application': application
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# In-memory storage for interview sessions
interview_sessions = {}


# API endpoint to start a new interview
@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    """
    Start a new mock interview session
    Expects JSON with company and role
    """
    try:
        # Get company and role from request
        data = request.get_json()
        company = data.get('company', 'General')
        role = data.get('role', 'Software Engineer')
        
        # Validate input
        if not company or not role:
            return jsonify({'error': 'Company and role are required'}), 400
        
        # Create interview session
        from utils import create_interview_session
        session = create_interview_session(company, role)
        
        # Store session
        interview_sessions[session['session_id']] = session
        
        # Return first question
        return jsonify({
            'session_id': session['session_id'],
            'company': session['company'],
            'role': session['role'],
            'total_questions': len(session['questions']),
            'current_question': session['questions'][0],
            'question_number': 1
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to submit an answer
@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """
    Submit an answer and get AI feedback
    Expects JSON with session_id and answer
    """
    try:
        # Get data from request
        data = request.get_json()
        session_id = data.get('session_id')
        answer = data.get('answer', '').strip()
        
        # Validate input
        if not session_id or session_id not in interview_sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        if not answer or len(answer) < 10:
            return jsonify({'error': 'Please provide a meaningful answer (at least 10 characters)'}), 400
        
        # Get session
        session = interview_sessions[session_id]
        current_q_index = session['current_question']
        question = session['questions'][current_q_index]
        
        # Analyze answer with AI
        from utils import analyze_interview_answer, detect_filler_words
        ai_feedback = analyze_interview_answer(question, answer)
        filler_analysis = detect_filler_words(answer)
        
        # Combine feedback
        answer_data = {
            'question': question,
            'answer': answer,
            'content_score': ai_feedback['content_score'],
            'communication_score': ai_feedback['communication_score'],
            'confidence_score': filler_analysis['confidence_score'],
            'feedback': ai_feedback['raw_feedback'],
            'filler_words': filler_analysis['filler_words'],
            'total_fillers': filler_analysis['total_fillers']
        }
        
        # Store answer
        session['answers'].append(answer_data)
        
        # Move to next question
        session['current_question'] += 1
        
        # Check if interview is complete
        if session['current_question'] >= len(session['questions']):
            # Interview complete
            from utils import calculate_overall_score
            final_scores = calculate_overall_score(session)
            
            return jsonify({
                'status': 'complete',
                'feedback': answer_data,
                'final_scores': final_scores,
                'total_answered': len(session['answers'])
            }), 200
        else:
            # More questions remaining
            next_question = session['questions'][session['current_question']]
            
            return jsonify({
                'status': 'continue',
                'feedback': answer_data,
                'next_question': next_question,
                'question_number': session['current_question'] + 1,
                'total_questions': len(session['questions'])
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to get interview results
@app.route('/api/interview-results/<session_id>', methods=['GET'])
def get_interview_results(session_id):
    """
    Get complete interview results
    """
    try:
        # Validate session
        if session_id not in interview_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = interview_sessions[session_id]
        
        # Calculate scores
        from utils import calculate_overall_score
        scores = calculate_overall_score(session)
        
        # Return complete results
        return jsonify({
            'session': session,
            'scores': scores,
            'answers': session['answers']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500     
if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True, port=5000)