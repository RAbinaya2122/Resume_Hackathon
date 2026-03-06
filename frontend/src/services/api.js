import axios from 'axios'

const BASE_URL = 'http://localhost:8000'

const api = axios.create({
    baseURL: BASE_URL,
    timeout: 300000,
})

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

/**
 * Register a new user.
 */
export async function register(email, password, fullName, role = 'candidate') {
    const { data } = await api.post('/api/auth/register', { email, password, full_name: fullName, role })
    return data
}

/**
 * Login a user.
 */
export async function login(email, password) {
    const { data } = await api.post('/api/auth/login', { email, password })
    if (data.access_token) {
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('role', data.role)
    }
    return data
}

/**
 * Logout user.
 */
export function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
}

/**
 * Candidate upload resume.
 */
export async function uploadResumeCandidate(file) {
    const form = new FormData()
    form.append('file', file)
    const { data } = await api.post('/api/candidate/upload-resume', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
}

/**
 * Send bulk mail via n8n webhook.
 */
export async function sendBulkMail(candidates, subject, message) {
    // Construct the payload with the "people" field as required by n8n
    const payload = {
        people: candidates,
        subject,
        message
    }
    const { data } = await api.post('https://abinaya2122.app.n8n.cloud/webhook/bulkmail', payload)
    return data
}

/**
 * Parse a resume PDF (without job description matching).
 * @param {File} file - PDF file object
 * @param {boolean} biassFree - enable bias-free parsing
 * @returns {Promise<ParsedResume>}
 */
export async function parseResume(file, biasFree = false) {
    const form = new FormData()
    form.append('file', file)
    form.append('bias_free', biasFree)

    const { data } = await api.post('/api/resume/parse', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
}

/**
 * Screen a resume against a job description.
 * @param {File} file - PDF resume
 * @param {string|object} jobDescription - raw JD text or structured object
 * @param {boolean} biasFree - enable bias-free evaluation
 * @returns {Promise<MatchResult>}
 */
export async function screenResume(file, jobDescription, biasFree = false) {
    const form = new FormData()
    form.append('file', file)
    form.append('bias_free', biasFree)

    if (typeof jobDescription === 'string') {
        form.append('job_description', jobDescription)
    } else {
        form.append('job_title', jobDescription.title || '')
        form.append('about', jobDescription.about || '')
        form.append('required_skills', jobDescription.skills || '')
        form.append('soft_skills', jobDescription.softSkills || '')
        form.append('languages', jobDescription.languages || '')
        form.append('projects_keywords', jobDescription.projectsKeywords || '')
        form.append('required_experience', jobDescription.experience || 0)
        form.append('preferred_domain', jobDescription.domain || '')
        form.append('job_description', jobDescription.description || '')
    }

    const { data } = await api.post('/api/resume/screen', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
}

/**
 * Screen multiple resumes against a job description.
 * @param {File[]} files - array of PDF resumes
 * @param {string|object} jobDescription - raw JD text or structured object
 * @param {boolean} biasFree - enable bias-free evaluation
 * @returns {Promise<BulkScreenResponse>}
 */
export async function bulkScreenResumes(files, jobDescription, biasFree = false) {
    const form = new FormData()
    files.forEach(file => {
        form.append('files', file)
    })
    form.append('bias_free', biasFree)

    if (typeof jobDescription === 'string') {
        form.append('job_description', jobDescription)
    } else {
        if (jobDescription.id) {
            form.append('template_id', jobDescription.id)
        }
        form.append('job_title', jobDescription.title || '')
        form.append('about', jobDescription.about || '')
        form.append('required_skills', jobDescription.skills || '')
        form.append('soft_skills', jobDescription.softSkills || '')
        form.append('languages', jobDescription.languages || '')
        form.append('projects_keywords', jobDescription.projectsKeywords || '')
        form.append('required_experience', jobDescription.experience || 0)
        form.append('preferred_domain', jobDescription.domain || '')
        form.append('job_description', jobDescription.description || '')
    }

    const { data } = await api.post('/api/resume/bulk-screen', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
}

/**
 * Fetch screening history records.
 * @returns {Promise<ScreeningRecord[]>}
 */
export async function fetchHistory() {
    const { data } = await api.get('/api/history/')
    return data
}

/**
 * Delete a specific screening record.
 * @param {number} id
 */
export async function deleteRecord(id) {
    await api.delete(`/api/history/${id}`)
}

/**
 * Clear all screening records.
 */
export async function clearAllRecords() {
    await api.delete('/api/history/')
}

/**
 * Fetch a specific screening record's full details.
 * @param {number} id
 * @returns {Promise<MatchResult>}
 */
export async function fetchRecordDetail(id) {
    const { data } = await api.get(`/api/history/${id}`)
    return data
}

/**
 * Fetch all JD templates.
 * @returns {Promise<JDTemplate[]>}
 */
export async function fetchTemplates() {
    const { data } = await api.get('/api/templates/')
    return data
}

/**
 * Save a new JD template.
 * @param {string} title
 * @param {string} description
 * @returns {Promise<JDTemplate>}
 */
export async function createTemplate(title, jdData) {
    const payload = {
        title,
        description: jdData.description || '',
        about: jdData.about || '',
        required_skills: jdData.skills || '',
        soft_skills: jdData.softSkills || '',
        languages: jdData.languages || '',
        projects_keywords: jdData.projectsKeywords || '',
        required_experience: jdData.experience || 0,
        preferred_domain: jdData.domain || ''
    }
    const { data } = await api.post('/api/templates/', payload)
    return data
}

/**
 * Delete a JD template.
 * @param {number} id
 */
export async function deleteTemplate(id) {
    await api.delete(`/api/templates/${id}`)
}

/**
 * Predict ideal team formation.
 * @param {MatchResult[]} results 
 * @param {number} teamSize 
 * @returns {Promise<any>}
 */
export async function predictTeam(results, teamSize = 3) {
    const { data } = await api.post('/api/team/predict', results, {
        params: { team_size: teamSize }
    })
    return data
}

export default api
