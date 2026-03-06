import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Loader2,
    BrainCircuit,
    LayoutDashboard,
    Home,
    FileSearch as FileSearchIcon,
    Save as SaveIcon,
    Trash2 as TrashIcon,
    Plus as PlusIcon,
    Bookmark as BookmarkIcon,
    RotateCcw as RotateIcon,
    Mail,
    Phone,
    ExternalLink,
    Trophy,
    Filter,
    CheckSquare,
    Send,
    X
} from 'lucide-react'
import FileDropzone from '../components/FileDropzone'
import BiasFreeToggle from '../components/BiasFreeToggle'
import ErrorBanner from '../components/ErrorBanner'
import { useScreening } from '../hooks/useScreening'
import { fetchTemplates, createTemplate, deleteTemplate } from '../services/api'

export default function Dashboard() {
    const navigate = useNavigate()
    const {
        files, setFiles,
        jdData, setJdData, updateJdData,
        biasFree, setBiasFree,
        loading, result, bulkResult, error,
        submit, reset,
    } = useScreening()

    const [templates, setTemplates] = useState([])
    const [isSavingTemplate, setIsSavingTemplate] = useState(false)
    const [newTemplateTitle, setNewTemplateTitle] = useState('')

    const loadUserTemplates = async () => {
        try {
            const data = await fetchTemplates()
            setTemplates(data)
        } catch (err) {
            console.error('Failed to load templates')
        }
    }

    useEffect(() => {
        loadUserTemplates()
    }, [])

    const handleSubmit = async (e) => {
        e.preventDefault()
        await submit()
    }

    const handleSaveTemplate = async () => {
        if (!newTemplateTitle.trim() || (!jdData.skills.trim() && !jdData.description.trim())) {
            alert('Please provide a title and at least core skills or a description.')
            return
        }

        try {
            await createTemplate(newTemplateTitle, jdData)
            setNewTemplateTitle('')
            setIsSavingTemplate(false)
            loadUserTemplates()
        } catch (err) {
            alert('Failed to save template.')
        }
    }

    const handleDeleteTemplate = async (id) => {
        if (!window.confirm('Delete this template?')) return
        try {
            await deleteTemplate(id)
            loadUserTemplates()
        } catch (err) {
            alert('Failed to delete template.')
        }
    }

    useEffect(() => {
        if (result) {
            navigate('/results', { state: { result } })
        }
    }, [result, navigate])

    useEffect(() => {
        if (bulkResult) {
            navigate('/bulk-results', {
                state: {
                    results: bulkResult.results,
                    failedCount: bulkResult.failed_count,
                    totalProcessed: bulkResult.total_processed
                }
            })
        }
    }, [bulkResult, navigate])

    return (
        <div className="max-w-6xl mx-auto px-4 py-8 animate-slide-up">
            {/* Header */}
            <div className="mb-10 text-center lg:text-left">
                <h1 className="text-4xl font-black text-white leading-tight tracking-tight">
                    Smart <span className="text-gradient">Recruitment</span> Screen
                </h1>
                <p className="text-gray-400 mt-2 text-sm max-w-2xl">
                    Structured JD matching with AI-driven skill mapping and candidate ranking.
                    Upload resumes and define your ideal candidate's core features.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
                <div className="grid lg:grid-cols-12 gap-8">
                    {/* Left: Configuration & Resumes (4 cols) */}
                    <div className="lg:col-span-4 space-y-6">
                        {/* Resume Upload */}
                        <div className="card p-6 border-brand-500/10 hover:border-brand-500/30 transition-all">
                            <h2 className="section-title text-base mb-1">
                                <span className="text-brand-400 font-mono text-xs mr-2">01</span>
                                Upload Resumes
                            </h2>
                            <p className="section-sub mb-4">Bulk PDF upload supported (100+ files)</p>
                            <FileDropzone files={files} onFilesChange={setFiles} multiple={true} />
                        </div>

                        {/* Evaluation Mode */}
                        <div className="card p-6">
                            <h2 className="section-title text-base mb-3">
                                <span className="text-brand-400 font-mono text-xs mr-2">03</span>
                                Bias-Free Mode
                            </h2>
                            <BiasFreeToggle enabled={biasFree} onChange={setBiasFree} />
                        </div>

                        {/* Templates List */}
                        <div className="card p-6 bg-surface-900/50">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="section-title text-base mb-0">
                                    <span className="text-brand-400 font-mono text-xs mr-2">04</span>
                                    Templates
                                </h2>
                                <span className="text-[10px] text-gray-500 uppercase font-black tracking-widest">SAVED</span>
                            </div>

                            {templates.length === 0 ? (
                                <div className="text-center py-8 rounded-xl bg-surface-800/20 border border-surface-700/50">
                                    <BookmarkIcon className="w-6 h-6 text-surface-700 mx-auto mb-2" />
                                    <p className="text-[10px] text-gray-600 font-bold uppercase tracking-tight">No Templates</p>
                                </div>
                            ) : (
                                <div className="space-y-2 max-h-48 overflow-y-auto pr-1 scroll-thin">
                                    {templates.map((tpl) => (
                                        <div key={tpl.id} className="flex items-center justify-between p-3 rounded-xl bg-surface-800 border border-surface-700 group transition-all hover:bg-surface-700 hover:border-brand-500/50">
                                            <button
                                                type="button"
                                                onClick={() => updateJdData({
                                                    id: tpl.id,
                                                    title: tpl.title,
                                                    description: tpl.description || '',
                                                    about: tpl.about || '',
                                                    skills: tpl.required_skills || '',
                                                    softSkills: tpl.soft_skills || '',
                                                    languages: tpl.languages || '',
                                                    projectsKeywords: tpl.projects_keywords || '',
                                                    experience: tpl.required_experience || 0,
                                                    domain: tpl.preferred_domain || ''
                                                })}
                                                className="flex-1 text-left text-xs font-bold text-gray-300 group-hover:text-white transition-colors truncate"
                                            >
                                                {tpl.title}
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => handleDeleteTemplate(tpl.id)}
                                                className="p-1.5 text-gray-600 hover:text-danger-400 opacity-0 group-hover:opacity-100 transition-all"
                                            >
                                                <TrashIcon className="w-3.5 h-3.5" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: Structured Job Description (8 cols) */}
                    <div className="lg:col-span-8 space-y-6">
                        <div className="card p-8 border-brand-500/20 shadow-2xl">
                            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                                <div className="space-y-1">
                                    <h2 className="section-title text-xl mb-0">
                                        <span className="text-brand-400 font-mono text-xs mr-2">02</span>
                                        Structured Requirements
                                    </h2>
                                    <p className="section-sub">Define core key-value pairs for higher accuracy</p>
                                </div>
                                <div className="flex items-center gap-2">
                                    {!isSavingTemplate ? (
                                        <button
                                            type="button"
                                            onClick={() => setIsSavingTemplate(true)}
                                            className="btn-secondary py-1.5 px-3 text-[10px]"
                                        >
                                            <SaveIcon className="w-3 h-3" />
                                            Save Template
                                        </button>
                                    ) : (
                                        <div className="flex items-center gap-2 animate-scale-in">
                                            <input
                                                type="text"
                                                value={newTemplateTitle}
                                                onChange={(e) => setNewTemplateTitle(e.target.value)}
                                                placeholder="Title..."
                                                className="bg-surface-800 border-surface-600 text-[10px] px-3 py-1.5 rounded-lg outline-none focus:ring-1 focus:ring-brand-500 w-36 border text-white"
                                                autoFocus
                                            />
                                            <button type="button" onClick={handleSaveTemplate} className="text-success-400"><SaveIcon className="w-4 h-4" /></button>
                                            <button type="button" onClick={() => setIsSavingTemplate(false)} className="text-danger-400"><RotateIcon className="w-4 h-4" /></button>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="grid md:grid-cols-2 gap-6 mb-8">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Job Title / Role</label>
                                    <input
                                        type="text"
                                        value={jdData.title}
                                        onChange={(e) => updateJdData({ title: e.target.value })}
                                        placeholder="e.g. Senior Frontend Engineer"
                                        className="input-field py-3 text-sm focus:ring-accent-500/20"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Target Domain</label>
                                    <input
                                        type="text"
                                        value={jdData.domain}
                                        onChange={(e) => updateJdData({ domain: e.target.value })}
                                        placeholder="e.g. Healthcare, Fintech, AI"
                                        className="input-field py-3 text-sm"
                                    />
                                </div>
                                <div className="space-y-2 md:col-span-2">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">About the Role</label>
                                    <input
                                        type="text"
                                        value={jdData.about}
                                        onChange={(e) => updateJdData({ about: e.target.value })}
                                        placeholder="Brief summary of the position..."
                                        className="input-field py-3 text-sm"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Required Technical Skills</label>
                                    <input
                                        type="text"
                                        value={jdData.skills}
                                        onChange={(e) => updateJdData({ skills: e.target.value })}
                                        placeholder="React, Node.js, AWS..."
                                        className="input-field py-3 text-sm border-brand-500/30 focus:border-brand-500 bg-brand-500/5"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Soft Skills</label>
                                    <input
                                        type="text"
                                        value={jdData.softSkills}
                                        onChange={(e) => updateJdData({ softSkills: e.target.value })}
                                        placeholder="Leadership, Communication..."
                                        className="input-field py-3 text-sm"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Languages</label>
                                    <input
                                        type="text"
                                        value={jdData.languages}
                                        onChange={(e) => updateJdData({ languages: e.target.value })}
                                        placeholder="English, French, German..."
                                        className="input-field py-3 text-sm"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Project Keywords</label>
                                    <input
                                        type="text"
                                        value={jdData.projectsKeywords}
                                        onChange={(e) => updateJdData({ projectsKeywords: e.target.value })}
                                        placeholder="E-commerce, Blockchain, AI Chatbot..."
                                        className="input-field py-3 text-sm"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Min. Experience (Years)</label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            step="0.5"
                                            value={jdData.experience}
                                            onChange={(e) => updateJdData({ experience: parseFloat(e.target.value) || 0 })}
                                            className="input-field py-3 text-sm pr-12"
                                        />
                                        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-600">YRS</span>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between px-1">
                                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Full Job Description (Optional)</label>
                                    <span className="text-[10px] text-gray-700 font-mono">{jdData.description.length} chars</span>
                                </div>
                                <textarea
                                    value={jdData.description}
                                    onChange={(e) => updateJdData({ description: e.target.value })}
                                    placeholder="Paste the full JD text here for deeper AI analysis..."
                                    className="input-field min-h-[200px] resize-none text-[13px] leading-relaxed p-5 bg-surface-950/20"
                                />
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex flex-col sm:flex-row items-center gap-4 pt-4">
                            <button
                                type="submit"
                                disabled={loading}
                                className="btn-primary w-full sm:w-auto px-10 py-5 text-sm font-black uppercase tracking-wider shadow-glow-brand"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Analyzing Candidates...
                                    </>
                                ) : (
                                    <>
                                        <FileSearchIcon className="w-5 h-5" />
                                        Screen and Rank Resumes
                                    </>
                                )}
                            </button>

                            <button
                                type="button"
                                onClick={reset}
                                className="btn-secondary w-full sm:w-auto py-5 px-8"
                                disabled={loading}
                            >
                                <RotateIcon className="w-4 h-4" />
                                Reset
                            </button>

                            {loading && (
                                <div className="flex items-center gap-2 text-[10px] font-bold text-brand-400 animate-pulse ml-2 uppercase tracking-tighter">
                                    <span className="w-2 h-2 rounded-full bg-brand-400 animate-ping"></span>
                                    Processing massive datasets...
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                <ErrorBanner message={error} />
            </form>
        </div>
    )
}
