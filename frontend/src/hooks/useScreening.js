import { useState, useCallback } from 'react'
import { screenResume, bulkScreenResumes } from '../services/api'

/**
 * Custom hook that manages the full screening flow:
 * file selection → submission → loading → result/error state
 */
export function useScreening() {
    const [files, setFiles] = useState([])
    const [jdData, setJdData] = useState({
        id: null,
        title: '',
        skills: '',
        softSkills: '',
        languages: '',
        projectsKeywords: '',
        about: '',
        experience: 0,
        domain: '',
        description: ''
    })
    const [biasFree, setBiasFree] = useState(false)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [bulkResult, setBulkResult] = useState(null)
    const [error, setError] = useState(null)

    const reset = useCallback(() => {
        setFiles([])
        setJdData({
            id: null,
            title: '',
            skills: '',
            softSkills: '',
            languages: '',
            projectsKeywords: '',
            about: '',
            experience: 0,
            domain: '',
            description: ''
        })
        setBiasFree(false)
        setResult(null)
        setBulkResult(null)
        setError(null)
        setLoading(false)
    }, [])

    const updateJdData = (fields) => {
        setJdData(prev => ({ ...prev, ...fields }))
    }

    const submit = useCallback(async () => {
        setError(null)

        if (files.length === 0) {
            setError('Please upload at least one PDF resume.')
            return
        }

        // Validation: either structured skills or description must exist
        if (!jdData.skills.trim() && !jdData.description.trim()) {
            setError('Please enter either required skills or a job description.')
            return
        }

        setLoading(true)
        try {
            if (files.length > 1) {
                const data = await bulkScreenResumes(files, jdData, biasFree)
                setBulkResult(data)
            } else {
                const data = await screenResume(files[0], jdData, biasFree)
                setResult(data)
            }
        } catch (err) {
            const detail =
                err?.response?.data?.detail ||
                err?.message ||
                'An unexpected error occurred. Please check the backend is running.'
            setError(detail)
        } finally {
            setLoading(false)
        }
    }, [files, jdData, biasFree])

    return {
        files, setFiles,
        jdData, setJdData, updateJdData,
        biasFree, setBiasFree,
        loading,
        result, setResult,
        bulkResult, setBulkResult,
        error, setError,
        submit,
        reset,
    }
}
