// CareerBot - Complete JavaScript with Fixes

// Initialize global variables at the very top
let requiredSkills = [];
let currentSessionId = null;
let currentFeedback = null;
let selectedResumeFile = null;

// ============================================
// CAREER READINESS SCORE FUNCTIONS
// ============================================

// Wait for DOM to load before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    
    // Career Readiness Form listeners
    const readinessForm = document.getElementById('readinessForm');
    if (readinessForm) {
        // Show/hide resume length field
        document.querySelectorAll('input[name="has_resume"]').forEach(radio => {
            radio.addEventListener('change', function() {
                const resumeLengthGroup = document.getElementById('resumeLengthGroup');
                if (resumeLengthGroup) {
                    resumeLengthGroup.style.display = this.value === 'true' ? 'block' : 'none';
                }
            });
        });

        // Show/hide projects count field
        document.querySelectorAll('input[name="has_projects"]').forEach(radio => {
            radio.addEventListener('change', function() {
                const projectsCountGroup = document.getElementById('projectsCountGroup');
                if (projectsCountGroup) {
                    projectsCountGroup.style.display = this.value === 'true' ? 'block' : 'none';
                }
            });
        });

        // Handle form submission
        readinessForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                has_resume: document.querySelector('input[name="has_resume"]:checked').value === 'true',
                resume_length: parseInt(document.getElementById('resume_length').value) || 0,
                skills_count: parseInt(document.getElementById('skills_count').value) || 0,
                experience_years: parseFloat(document.getElementById('experience_years').value) || 0,
                has_projects: document.querySelector('input[name="has_projects"]:checked').value === 'true',
                projects_count: parseInt(document.getElementById('projects_count').value) || 0
            };
            
            try {
                const submitButton = document.querySelector('.btn-primary');
                submitButton.textContent = 'Calculating...';
                submitButton.disabled = true;
                
                const response = await fetch('/api/calculate-score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to calculate score');
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                alert('Error calculating score: ' + error.message);
            } finally {
                const submitButton = document.querySelector('.btn-primary');
                submitButton.textContent = 'Calculate My Score';
                submitButton.disabled = false;
            }
        });
    }
    
    // Resume Upload listeners
    const resumeFile = document.getElementById('resumeFile');
    if (resumeFile) {
        resumeFile.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) handleResumeFile(file);
        });
    }
    
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.addEventListener('click', function() {
            document.getElementById('resumeFile').click();
        });
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file) handleResumeFile(file);
        });
    }
    
    // Job Tracker initialization
    if (document.getElementById('applicationsContainer')) {
        loadApplications();
        loadStatistics();
        checkReminders();
        
        const dateApplied = document.getElementById('date_applied');
        if (dateApplied) {
            dateApplied.valueAsDate = new Date();
        }
    }
});

function displayResults(result) {
    document.getElementById('readinessForm').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    
    document.getElementById('totalScore').textContent = result.score;
    document.getElementById('readinessLevel').textContent = result.readiness_level;
    
    const breakdown = result.breakdown;
    document.getElementById('resumeScore').textContent = breakdown.resume_quality + '/25';
    document.getElementById('resumeProgress').style.width = (breakdown.resume_quality / 25 * 100) + '%';
    document.getElementById('skillsScore').textContent = breakdown.skills_match + '/25';
    document.getElementById('skillsProgress').style.width = (breakdown.skills_match / 25 * 100) + '%';
    document.getElementById('experienceScore').textContent = breakdown.experience_level + '/25';
    document.getElementById('experienceProgress').style.width = (breakdown.experience_level / 25 * 100) + '%';
    document.getElementById('projectsScore').textContent = breakdown.project_portfolio + '/25';
    document.getElementById('projectsProgress').style.width = (breakdown.project_portfolio / 25 * 100) + '%';
    
    const feedbackList = document.getElementById('feedbackList');
    feedbackList.innerHTML = '';
    result.feedback.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        feedbackList.appendChild(li);
    });
    
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    document.getElementById('readinessForm').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('readinessForm').reset();
    document.getElementById('resumeLengthGroup').style.display = 'none';
    document.getElementById('projectsCountGroup').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// SKILLS GAP ANALYZER FUNCTIONS
// ============================================

async function extractSkills() {
    const jobDescription = document.getElementById('jobDescription').value.trim();
    
    if (!jobDescription || jobDescription.length < 50) {
        alert('Please paste a complete job description (at least 50 characters)');
        return;
    }
    
    try {
        const button = event.target;
        button.textContent = 'Analyzing...';
        button.disabled = true;
        
        const response = await fetch('/api/extract-skills', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_description: jobDescription })
        });
        
        if (!response.ok) throw new Error('Failed to extract skills');
        
        const result = await response.json();
        requiredSkills = result.required_skills;
        displayRequiredSkills(requiredSkills);
        
        document.getElementById('jobDescriptionStep').style.display = 'none';
        document.getElementById('userSkillsStep').style.display = 'block';
        
    } catch (error) {
        alert('Error extracting skills: ' + error.message);
    } finally {
        const button = event.target;
        button.textContent = 'Analyze Job Requirements';
        button.disabled = false;
    }
}

function displayRequiredSkills(skills) {
    const container = document.getElementById('requiredSkillsList');
    container.innerHTML = '';
    
    if (skills.length === 0) {
        container.innerHTML = '<p>No specific technical skills detected.</p>';
        return;
    }
    
    skills.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = 'skill-tag';
        tag.textContent = skill;
        container.appendChild(tag);
    });
}

async function analyzeGap() {
    const userSkillsInput = document.getElementById('userSkills').value.trim();
    
    if (!userSkillsInput) {
        alert('Please enter your skills');
        return;
    }
    
    const userSkills = userSkillsInput.split(',').map(skill => skill.trim()).filter(skill => skill);
    
    if (userSkills.length === 0) {
        alert('Please enter at least one skill');
        return;
    }
    
    try {
        const button = event.target;
        button.textContent = 'Analyzing...';
        button.disabled = true;
        
        const response = await fetch('/api/analyze-gap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_skills: userSkills, required_skills: requiredSkills })
        });
        
        if (!response.ok) throw new Error('Failed to analyze skill gap');
        
        const result = await response.json();
        displayGapAnalysis(result);
        
        document.getElementById('userSkillsStep').style.display = 'none';
        document.getElementById('skillsGapResults').style.display = 'block';
        document.getElementById('skillsGapResults').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error analyzing gap: ' + error.message);
    } finally {
        const button = event.target;
        button.textContent = 'Analyze My Skill Gap';
        button.disabled = false;
    }
}

function displayGapAnalysis(analysis) {
    document.getElementById('gapReadinessPercentage').textContent = analysis.readiness_percentage;
    document.getElementById('gapReadinessStatus').textContent = analysis.readiness_status;
    
    const matchingList = document.getElementById('matchingSkillsList');
    matchingList.innerHTML = '';
    if (analysis.matching_skills.length === 0) {
        matchingList.innerHTML = '<p style="color: #999;">No matching skills found</p>';
    } else {
        analysis.matching_skills.forEach(skill => {
            const div = document.createElement('div');
            div.className = 'skill-item';
            div.textContent = skill;
            matchingList.appendChild(div);
        });
    }
    
    const missingList = document.getElementById('missingSkillsList');
    missingList.innerHTML = '';
    if (analysis.missing_skills.length === 0) {
        missingList.innerHTML = '<p style="color: #999;">You have all required skills!</p>';
    } else {
        analysis.missing_skills.forEach(skill => {
            const div = document.createElement('div');
            div.className = 'skill-item';
            div.textContent = skill;
            missingList.appendChild(div);
        });
    }
    
    document.getElementById('gapRecommendation').textContent = analysis.recommendation;
    displayLearningResources(analysis.learning_resources);
}

function displayLearningResources(resources) {
    const container = document.getElementById('learningResourcesList');
    container.innerHTML = '';
    
    if (Object.keys(resources).length === 0) {
        container.innerHTML = '<p>No learning resources needed!</p>';
        return;
    }
    
    for (const [skill, resourceList] of Object.entries(resources)) {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'resource-group';
        
        const heading = document.createElement('h4');
        heading.textContent = skill;
        groupDiv.appendChild(heading);
        
        resourceList.forEach(resource => {
            const link = document.createElement('a');
            link.href = resource.url;
            link.target = '_blank';
            link.className = 'resource-link';
            link.innerHTML = resource.name + '<span class="resource-type">' + resource.type + '</span>';
            groupDiv.appendChild(link);
        });
        
        container.appendChild(groupDiv);
    }
}

function resetSkillsAnalyzer() {
    document.getElementById('jobDescriptionStep').style.display = 'block';
    document.getElementById('userSkillsStep').style.display = 'none';
    document.getElementById('skillsGapResults').style.display = 'none';
    document.getElementById('jobDescription').value = '';
    document.getElementById('userSkills').value = '';
    requiredSkills = [];
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// RESUME ROAST MODE FUNCTIONS
// ============================================

function handleResumeFile(file) {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (!allowedTypes.includes(file.type)) {
        alert('Please upload a PDF or DOCX file only');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    
    selectedResumeFile = file;
    
    const fileNameDiv = document.getElementById('fileName');
    if (fileNameDiv) {
        fileNameDiv.textContent = file.name;
        fileNameDiv.style.display = 'block';
    }
    
    const analyzeBtn = document.getElementById('analyzeResumeBtn');
    if (analyzeBtn) {
        analyzeBtn.style.display = 'block';
    }
}

async function uploadAndAnalyzeResume() {
    if (!selectedResumeFile) {
        alert('Please select a resume file first');
        return;
    }
    
    try {
        const button = document.getElementById('analyzeResumeBtn');
        button.innerHTML = '<span class="loading"></span> Analyzing...';
        button.disabled = true;
        
        const formData = new FormData();
        formData.append('resume', selectedResumeFile);
        
        const response = await fetch('/api/analyze-resume', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to analyze resume');
        }
        
        const result = await response.json();
        displayResumeAnalysis(result);
        
        document.getElementById('resumeUploadSection').style.display = 'none';
        document.getElementById('resumeAnalysisResults').style.display = 'block';
        document.getElementById('resumeAnalysisResults').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error analyzing resume: ' + error.message);
        console.error('Error:', error);
    } finally {
        const button = document.getElementById('analyzeResumeBtn');
        button.textContent = 'Analyze My Resume';
        button.disabled = false;
    }
}

function displayResumeAnalysis(analysis) {
    document.getElementById('resumeTotalScore').textContent = analysis.total_score;
    document.getElementById('resumeOverallAssessment').textContent = analysis.overall_assessment;
    document.getElementById('resumeWordCount').textContent = `Word Count: ${analysis.word_count} words`;
    
    const scores = analysis.scores;
    document.getElementById('lengthScore').textContent = scores.length_score + '/20';
    document.getElementById('lengthProgress').style.width = (scores.length_score / 20 * 100) + '%';
    document.getElementById('keywordsScore').textContent = scores.keywords_score + '/20';
    document.getElementById('keywordsProgress').style.width = (scores.keywords_score / 20 * 100) + '%';
    document.getElementById('formattingScore').textContent = scores.formatting_score + '/20';
    document.getElementById('formattingProgress').style.width = (scores.formatting_score / 20 * 100) + '%';
    document.getElementById('contactScore').textContent = scores.contact_info_score + '/20';
    document.getElementById('contactProgress').style.width = (scores.contact_info_score / 20 * 100) + '%';
    document.getElementById('actionScore').textContent = scores.action_verbs_score + '/20';
    document.getElementById('actionProgress').style.width = (scores.action_verbs_score / 20 * 100) + '%';
    
    const feedbackList = document.getElementById('bruthalFeedbackList');
    feedbackList.innerHTML = '';
    analysis.feedback.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        feedbackList.appendChild(li);
    });
    
    const improvementsList = document.getElementById('improvementsList');
    improvementsList.innerHTML = '';
    if (analysis.improvements && analysis.improvements.length > 0) {
        analysis.improvements.forEach(improvement => {
            const card = document.createElement('div');
            card.className = 'improvement-card';
            card.innerHTML = `
                <h4>${improvement.category}</h4>
                <div class="improvement-issue">Problem: ${improvement.issue}</div>
                <div class="improvement-fix">${improvement.fix}</div>
            `;
            improvementsList.appendChild(card);
        });
    } else {
        improvementsList.innerHTML = '<p style="color: #28a745; font-weight: 600;">Your resume looks great!</p>';
    }
}

function resetResumeAnalyzer() {
    selectedResumeFile = null;
    const fileInput = document.getElementById('resumeFile');
    if (fileInput) fileInput.value = '';
    const fileNameDiv = document.getElementById('fileName');
    if (fileNameDiv) fileNameDiv.style.display = 'none';
    const analyzeBtn = document.getElementById('analyzeResumeBtn');
    if (analyzeBtn) analyzeBtn.style.display = 'none';
    
    document.getElementById('resumeUploadSection').style.display = 'block';
    document.getElementById('resumeAnalysisResults').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// JOB APPLICATION TRACKER FUNCTIONS
// ============================================

function toggleAddForm() {
    const form = document.getElementById('addApplicationForm');
    if (form.style.display === 'none' || !form.style.display) {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
        document.getElementById('jobApplicationForm').reset();
        const dateApplied = document.getElementById('date_applied');
        if (dateApplied) dateApplied.valueAsDate = new Date();
    }
}

async function addJobApplication() {
    const jobData = {
        company: document.getElementById('company').value.trim(),
        position: document.getElementById('position').value.trim(),
        job_url: document.getElementById('job_url').value.trim(),
        date_applied: document.getElementById('date_applied').value,
        notes: document.getElementById('notes').value.trim()
    };
    
    if (!jobData.company || !jobData.position) {
        alert('Please fill in company name and position');
        return;
    }
    
    try {
        const response = await fetch('/api/add-application', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jobData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add application');
        }
        
        alert('Application added successfully!');
        toggleAddForm();
        loadApplications();
        loadStatistics();
        checkReminders();
        
    } catch (error) {
        alert('Error adding application: ' + error.message);
    }
}

async function loadApplications() {
    try {
        const response = await fetch('/api/get-applications');
        if (!response.ok) throw new Error('Failed to load applications');
        const result = await response.json();
        displayApplications(result.applications);
    } catch (error) {
        console.error('Error loading applications:', error);
    }
}

function displayApplications(applications) {
    const container = document.getElementById('applicationsContainer');
    if (!container) return;
    
    if (applications.length === 0) {
        container.innerHTML = '<p class="empty-state">No applications yet. Add your first application to start tracking!</p>';
        return;
    }
    
    container.innerHTML = '';
    applications.forEach(app => {
        const card = createApplicationCard(app);
        container.appendChild(card);
    });
}

function createApplicationCard(app) {
    const card = document.createElement('div');
    card.className = 'application-card';
    
    const today = new Date();
    const followUpDate = app.follow_up_date ? new Date(app.follow_up_date) : null;
    const needsFollowUp = followUpDate && followUpDate <= today && ['Applied', 'Viewed'].includes(app.status);
    const appliedDate = new Date(app.date_applied);
    const daysSince = Math.floor((today - appliedDate) / (1000 * 60 * 60 * 24));
    
    card.innerHTML = `
        <div class="application-header">
            <div class="application-info">
                <h4>${app.company}</h4>
                <p>${app.position}</p>
            </div>
            <span class="status-badge status-${app.status.replace(' ', '')}">${app.status}</span>
        </div>
        ${needsFollowUp ? '<div class="follow-up-alert">⏰ Follow-up needed!</div>' : ''}
        <div class="application-details">
            <div class="detail-item">
                <span class="detail-label">Applied</span>
                <span class="detail-value">${app.date_applied} (${daysSince} days ago)</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Follow-up Date</span>
                <span class="detail-value">${app.follow_up_date || 'N/A'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Job Link</span>
                <span class="detail-value">${app.job_url ? `<a href="${app.job_url}" target="_blank">View Posting</a>` : 'N/A'}</span>
            </div>
        </div>
        ${app.notes ? `<div style="margin-bottom: 15px;"><strong>Notes:</strong> ${app.notes}</div>` : ''}
        <div class="application-actions">
            <select class="status-selector" onchange="updateApplicationStatus('${app.id}', this.value)">
                <option value="">Change Status</option>
                <option value="Applied" ${app.status === 'Applied' ? 'selected' : ''}>Applied</option>
                <option value="Viewed" ${app.status === 'Viewed' ? 'selected' : ''}>Viewed</option>
                <option value="Interview Scheduled" ${app.status === 'Interview Scheduled' ? 'selected' : ''}>Interview Scheduled</option>
                <option value="Interviewed" ${app.status === 'Interviewed' ? 'selected' : ''}>Interviewed</option>
                <option value="Rejected" ${app.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                <option value="Offer" ${app.status === 'Offer' ? 'selected' : ''}>Offer</option>
            </select>
            <button class="action-btn action-btn-primary" onclick="generateEmail('${app.id}')">Generate Follow-up Email</button>
            <button class="action-btn action-btn-danger" onclick="deleteApplication('${app.id}')">Delete</button>
        </div>
    `;
    
    return card;
}

async function updateApplicationStatus(applicationId, newStatus) {
    if (!newStatus) return;
    
    try {
        const response = await fetch(`/api/update-status/${applicationId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!response.ok) throw new Error('Failed to update status');
        loadApplications();
        loadStatistics();
        checkReminders();
    } catch (error) {
        alert('Error updating status: ' + error.message);
    }
}

async function deleteApplication(applicationId) {
    if (!confirm('Are you sure you want to delete this application?')) return;
    
    try {
        const response = await fetch(`/api/delete-application/${applicationId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete application');
        loadApplications();
        loadStatistics();
        checkReminders();
    } catch (error) {
        alert('Error deleting application: ' + error.message);
    }
}

async function loadStatistics() {
    try {
        const response = await fetch('/api/get-statistics');
        if (!response.ok) throw new Error('Failed to load statistics');
        const stats = await response.json();
        
        const totalApps = document.getElementById('totalApps');
        const responseRate = document.getElementById('responseRate');
        const interviewCount = document.getElementById('interviewCount');
        const offerCount = document.getElementById('offerCount');
        
        if (totalApps) totalApps.textContent = stats.total_applications;
        if (responseRate) responseRate.textContent = stats.response_rate + '%';
        if (interviewCount) interviewCount.textContent = stats.interviews;
        if (offerCount) offerCount.textContent = stats.offers;
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

async function checkReminders() {
    try {
        const response = await fetch('/api/get-reminders');
        if (!response.ok) throw new Error('Failed to load reminders');
        const result = await response.json();
        
        const notificationsBar = document.getElementById('notificationsBar');
        const notificationCount = document.getElementById('notificationCount');
        
        if (notificationsBar && notificationCount) {
            if (result.count > 0) {
                notificationsBar.style.display = 'block';
                notificationCount.textContent = result.count;
            } else {
                notificationsBar.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error checking reminders:', error);
    }
}

async function showReminders() {
    try {
        const response = await fetch('/api/get-reminders');
        if (!response.ok) throw new Error('Failed to load reminders');
        const result = await response.json();
        
        const remindersList = document.getElementById('remindersList');
        remindersList.innerHTML = '';
        
        if (result.reminders.length === 0) {
            remindersList.innerHTML = '<p style="text-align: center; color: #28a745;">No pending follow-ups!</p>';
        } else {
            result.reminders.forEach(reminder => {
                const app = reminder.application;
                const card = document.createElement('div');
                card.className = `reminder-card priority-${reminder.priority.toLowerCase()}`;
                card.innerHTML = `
                    <h4>${app.company} - ${app.position}</h4>
                    <p><strong>Applied:</strong> ${app.date_applied}</p>
                    <p><strong>Follow-up Due:</strong> ${app.follow_up_date}</p>
                    <p><strong>Days Overdue:</strong> ${reminder.days_overdue}</p>
                    <p><strong>Priority:</strong> ${reminder.priority}</p>
                    <button class="action-btn action-btn-primary" style="margin-top: 10px;" onclick="generateEmail('${app.id}'); closeRemindersModal();">Generate Email</button>
                `;
                remindersList.appendChild(card);
            });
        }
        
        document.getElementById('remindersModal').style.display = 'flex';
    } catch (error) {
        alert('Error loading reminders: ' + error.message);
    }
}

function closeRemindersModal() {
    document.getElementById('remindersModal').style.display = 'none';
}

async function generateEmail(applicationId) {
    try {
        const response = await fetch(`/api/generate-email/${applicationId}`);
        if (!response.ok) throw new Error('Failed to generate email');
        const result = await response.json();
        
        document.getElementById('emailTemplate').value = result.email_template;
        document.getElementById('emailModal').style.display = 'flex';
    } catch (error) {
        alert('Error generating email: ' + error.message);
    }
}

function closeEmailModal() {
    document.getElementById('emailModal').style.display = 'none';
}

function copyEmailTemplate() {
    const emailText = document.getElementById('emailTemplate');
    emailText.select();
    document.execCommand('copy');
    alert('Email template copied to clipboard!');
}

window.onclick = function(event) {
    const remindersModal = document.getElementById('remindersModal');
    const emailModal = document.getElementById('emailModal');
    
    if (event.target === remindersModal) closeRemindersModal();
    if (event.target === emailModal) closeEmailModal();
}

// ============================================
// MOCK INTERVIEW FUNCTIONS
// ============================================

async function startInterview() {
    const company = document.getElementById('interview_company').value;
    const role = document.getElementById('interview_role').value.trim();
    
    if (!role) {
        alert('Please enter a role');
        return;
    }
    
    const button = event.target;
    
    try {
        button.textContent = 'Starting...';
        button.disabled = true;
        
        const response = await fetch('/api/start-interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company, role })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to start interview');
        }
        
        const result = await response.json();
        currentSessionId = result.session_id;
        
        document.getElementById('interviewCompanyName').textContent = result.company;
        document.getElementById('interviewRoleName').textContent = result.role;
        document.getElementById('currentQuestionNum').textContent = result.question_number;
        document.getElementById('totalQuestions').textContent = result.total_questions;
        document.getElementById('currentQuestion').textContent = result.current_question;
        
        document.getElementById('interviewStartSection').style.display = 'none';
        document.getElementById('interviewInProgress').style.display = 'block';
        document.getElementById('interviewInProgress').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error starting interview: ' + error.message);
    } finally {
        button.textContent = 'Start Mock Interview';
        button.disabled = false;
    }
}

async function submitAnswer() {
    const answer = document.getElementById('userAnswer').value.trim();
    
    if (!answer || answer.length < 10) {
        alert('Please provide a meaningful answer (at least 10 characters)');
        return;
    }
    
    const button = event.target;
    
    try {
        button.innerHTML = '<span class="loading"></span> Analyzing...';
        button.disabled = true;
        
        const response = await fetch('/api/submit-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId, answer: answer })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to submit answer');
        }
        
        const result = await response.json();
        currentFeedback = result;
        displayFeedback(result.feedback);
        
        document.getElementById('interviewInProgress').style.display = 'none';
        document.getElementById('feedbackSection').style.display = 'block';
        
        if (result.status === 'complete') {
            document.getElementById('nextQuestionBtn').textContent = 'View Final Results';
            document.getElementById('nextQuestionBtn').onclick = function() {
                showFinalResults(result.final_scores);
            };
        }
        
        document.getElementById('feedbackSection').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error submitting answer: ' + error.message);
    } finally {
        button.textContent = 'Submit Answer';
        button.disabled = false;
    }
}

function displayFeedback(feedback) {
    document.getElementById('contentScore').textContent = feedback.content_score + '/10';
    document.getElementById('communicationScore').textContent = feedback.communication_score + '/10';
    document.getElementById('confidenceScore').textContent = Math.round(feedback.confidence_score) + '%';
    document.getElementById('aiFeedbackText').textContent = feedback.feedback;
    
    if (feedback.total_fillers > 0) {
        document.getElementById('fillerWordsAlert').style.display = 'block';
        const fillersList = document.getElementById('fillerWordsList');
        fillersList.innerHTML = '';
        
        for (const [word, count] of Object.entries(feedback.filler_words)) {
            const tag = document.createElement('span');
            tag.className = 'filler-tag';
            tag.textContent = `"${word}" (${count}x)`;
            fillersList.appendChild(tag);
        }
    } else {
        document.getElementById('fillerWordsAlert').style.display = 'none';
    }
}

function nextQuestion() {
    if (currentFeedback.status === 'complete') {
        showFinalResults(currentFeedback.final_scores);
        return;
    }
    
    document.getElementById('currentQuestionNum').textContent = currentFeedback.question_number;
    document.getElementById('currentQuestion').textContent = currentFeedback.next_question;
    document.getElementById('userAnswer').value = '';
    
    document.getElementById('feedbackSection').style.display = 'none';
    document.getElementById('interviewInProgress').style.display = 'block';
    document.getElementById('interviewInProgress').scrollIntoView({ behavior: 'smooth' });
}

async function showFinalResults(scores) {
    try {
        const response = await fetch(`/api/interview-results/${currentSessionId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load results');
        }
        
        const result = await response.json();
        
        document.getElementById('overallScore').textContent = Math.round(result.scores.overall_score);
        document.getElementById('finalContentScore').textContent = result.scores.content_avg + '/10';
        document.getElementById('finalContentBar').style.width = (result.scores.content_avg * 10) + '%';
        document.getElementById('finalCommScore').textContent = result.scores.communication_avg + '/10';
        document.getElementById('finalCommBar').style.width = (result.scores.communication_avg * 10) + '%';
        document.getElementById('finalConfScore').textContent = Math.round(result.scores.confidence_avg) + '%';
        document.getElementById('finalConfBar').style.width = result.scores.confidence_avg + '%';
        
        const summaryContainer = document.getElementById('answersSummary');
        summaryContainer.innerHTML = '';
        
        result.answers.forEach((answer, index) => {
            const summaryItem = document.createElement('div');
            summaryItem.className = 'answer-summary-item';
            summaryItem.innerHTML = `
                <h4>Question ${index + 1}: ${answer.question}</h4>
                <div class="summary-scores">
                    <span class="summary-score-badge">Content: ${answer.content_score}/10</span>
                    <span class="summary-score-badge">Communication: ${answer.communication_score}/10</span>
                    <span class="summary-score-badge">Confidence: ${Math.round(answer.confidence_score)}%</span>
                </div>
            `;
            summaryContainer.appendChild(summaryItem);
        });
        
        document.getElementById('feedbackSection').style.display = 'none';
        document.getElementById('finalResultsSection').style.display = 'block';
        document.getElementById('finalResultsSection').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error loading results: ' + error.message);
    }
}

function resetInterview() {
    currentSessionId = null;
    currentFeedback = null;
    document.getElementById('interview_role').value = 'Software Engineer';
    document.getElementById('userAnswer').value = '';
    document.getElementById('interviewStartSection').style.display = 'block';
    document.getElementById('interviewInProgress').style.display = 'none';
    document.getElementById('feedbackSection').style.display = 'none';
    document.getElementById('finalResultsSection').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function endInterview() {
    if (confirm('Are you sure you want to end this interview? Your progress will be lost.')) {
        resetInterview();
    }
}