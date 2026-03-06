import { useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { ArrowLeft, Mail, Phone, ExternalLink, Trophy, Filter, CheckSquare, Send, X, Loader2, Users, Sparkles, AlertCircle } from 'lucide-react'
import { sendBulkMail, predictTeam } from '../services/api'

export default function BulkResults() {
    const { state } = useLocation()
    const navigate = useNavigate()
    const results = state?.results || []
    const failedCount = state?.failedCount || 0
    const totalProcessed = state?.totalProcessed || 0

    const [selectedIndices, setSelectedIndices] = useState([])
    const [isEmailModalOpen, setIsEmailModalOpen] = useState(false)
    const [emailSubject, setEmailSubject] = useState('')
    const [emailMessage, setEmailMessage] = useState('')
    const [isSending, setIsSending] = useState(false)

    // Team Prediction
    const [predictedTeam, setPredictedTeam] = useState(null)
    const [isPredicting, setIsPredicting] = useState(false)
    const [isTeamModalOpen, setIsTeamModalOpen] = useState(false)

    useEffect(() => {
        if (!state) {
            navigate('/dashboard')
        }
    }, [state, navigate])

    const handlePredictTeam = async () => {
        setIsPredicting(true)
        try {
            const data = await predictTeam(results, 3)
            setPredictedTeam(data.team)
            setIsTeamModalOpen(true)
        } catch (err) {
            alert('Failed to predict team.')
        } finally {
            setIsPredicting(false)
        }
    }

    const toggleSelection = (index) => {
        if (selectedIndices.includes(index)) {
            setSelectedIndices(selectedIndices.filter(i => i !== index))
        } else {
            setSelectedIndices([...selectedIndices, index])
        }
    }

    const selectTop = (n) => {
        const topIndices = results.slice(0, n).map((_, i) => i)
        setSelectedIndices(topIndices)
    }

    const handleSendBulkEmail = async () => {
        if (!emailSubject || !emailMessage) {
            alert('Please provide both subject and message.')
            return
        }

        const selectedCandidates = selectedIndices.map(i => ({
            name: results[i].candidate_name || 'Candidate',
            email: results[i].email || ''
        })).filter(c => c.email)

        if (selectedCandidates.length === 0) {
            alert('No candidates with valid email selected.')
            return
        }

        setIsSending(true)
        try {
            await sendBulkMail(selectedCandidates, emailSubject, emailMessage)
            alert('Bulk email request sent successfully!')
            setIsEmailModalOpen(false)
            setEmailSubject('')
            setEmailMessage('')
        } catch (err) {
            alert('Failed to send bulk email: ' + (err.response?.data?.detail || err.message))
        } finally {
            setIsSending(false)
        }
    }

    if (!results.length) return null

    return (
        <div className="max-w-6xl mx-auto px-4 py-10 animate-slide-up space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <button
                        id="back-btn"
                        onClick={() => navigate('/dashboard')}
                        className="btn-secondary w-10 h-10 rounded-full flex items-center justify-center p-0"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
                            Ranked Recruitment List
                            <Trophy className="w-6 h-6 text-accent-400" />
                        </h1>
                        <p className="text-gray-400 text-sm mt-1">
                            Analyzed {results.length} resumes. {selectedIndices.length} candidates selected.
                        </p>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <div className="flex bg-surface-800 border border-surface-700 rounded-lg p-1">
                        {[5, 10, 20].map(n => (
                            <button
                                key={n}
                                onClick={() => selectTop(n)}
                                className="px-3 py-1 text-[10px] font-bold text-gray-400 hover:text-white hover:bg-surface-700 rounded transition-all uppercase tracking-wider"
                            >
                                Top {n}
                            </button>
                        ))}
                    </div>
                    <button
                        onClick={handlePredictTeam}
                        disabled={isPredicting || results.length === 0}
                        className="btn-secondary px-4 py-2 text-xs border-accent-500/30 hover:bg-accent-500/10 text-accent-300"
                    >
                        {isPredicting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Users className="w-4 h-4" />}
                        Predict Ideal Team
                    </button>
                    <button
                        onClick={() => setIsEmailModalOpen(true)}
                        disabled={selectedIndices.length === 0}
                        className={`btn-primary px-4 py-2 text-xs shadow-lg shadow-brand-500/10 ${selectedIndices.length === 0 ? 'opacity-50 grayscale cursor-not-allowed' : ''}`}
                    >
                        <Send className="w-4 h-4" />
                        Bulk Email ({selectedIndices.length})
                    </button>
                </div>
            </div>

            {failedCount > 0 && (
                <div className="p-4 rounded-xl bg-danger-500/10 border border-danger-500/20 text-danger-400 text-sm flex items-center gap-3 animate-pulse">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <p>
                        <strong>{failedCount} resumes</strong> failed to process. They might be corrupted, too large, or not text-readable PDFs.
                    </p>
                </div>
            )}

            {results.length === 0 ? (
                <div className="h-[400px] card flex flex-col items-center justify-center text-center p-12">
                    <AlertCircle className="w-16 h-16 text-gray-700 mb-6" />
                    <h2 className="text-2xl font-bold text-white mb-2">No successfully analyzed resumes</h2>
                    <p className="text-gray-400 max-w-sm mb-8">All uploaded files encountered errors or were empty. Please check your PDF files and try again.</p>
                    <button onClick={() => navigate('/dashboard')} className="btn-primary px-10">Back to Dashboard</button>
                </div>
            ) : (
                /* Results Table */
                <div className="card overflow-hidden shadow-2xl border-surface-600/50">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-surface-700/40 border-b border-surface-600">
                                    <th className="px-4 py-4 w-10">
                                        <CheckSquare className="w-4 h-4 text-gray-500 mx-auto" />
                                    </th>
                                    <th className="px-6 py-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">Rank</th>
                                    <th className="px-6 py-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">Candidate Info</th>
                                    <th className="px-6 py-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">Contact Details</th>
                                    <th className="px-6 py-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">Exp / Domain</th>
                                    <th className="px-6 py-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest text-right">Match Score</th>
                                    <th className="px-6 py-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-surface-700">
                                {results.map((res, index) => (
                                    <tr key={index} className={`hover:bg-brand-500/[0.03] transition-colors group ${selectedIndices.includes(index) ? 'bg-brand-500/[0.05]' : ''}`}>
                                        <td className="px-4 py-5 text-center">
                                            <input
                                                type="checkbox"
                                                checked={selectedIndices.includes(index)}
                                                onChange={() => toggleSelection(index)}
                                                className="w-4 h-4 rounded border-surface-600 bg-surface-700 text-brand-500 focus:ring-brand-500/20 cursor-pointer"
                                            />
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className={`
                                            inline-flex items-center justify-center w-8 h-8 rounded-lg text-xs font-black
                                            ${index === 0 ? 'bg-accent-500 text-white shadow-glow-accent scale-110' :
                                                    index === 1 ? 'bg-brand-500/80 text-white' :
                                                        index === 2 ? 'bg-brand-500/60 text-white' :
                                                            'bg-surface-600 text-gray-400'}
                                        `}>
                                                #{index + 1}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div>
                                                <p className="font-bold text-white group-hover:text-brand-400 transition-colors">
                                                    {res.candidate_name || 'Unknown Candidate'}
                                                </p>
                                                <p className="text-[10px] text-gray-500 font-mono mt-1 flex items-center gap-1">
                                                    <span className="w-1 h-1 rounded-full bg-surface-500"></span>
                                                    {res.filename}
                                                </p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="space-y-1.5">
                                                <div className="flex items-center gap-2">
                                                    <Mail className="w-3.5 h-3.5 text-brand-400/70" />
                                                    <span className={`text-xs ${res.email ? 'text-gray-300' : 'text-gray-600 italic font-mono'}`}>
                                                        {res.email || 'null'}
                                                    </span>
                                                </div>
                                                {res.phone && (
                                                    <div className="flex items-center gap-2">
                                                        <Phone className="w-3.5 h-3.5 text-accent-400/70" />
                                                        <span className="text-xs text-gray-300">{res.phone}</span>
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="space-y-1">
                                                <div className="text-xs text-white font-semibold">
                                                    {res.candidate_experience} Years
                                                </div>
                                                <div className="text-[10px] text-brand-400 uppercase tracking-tighter bg-brand-500/10 inline-block px-1.5 py-0.5 rounded border border-brand-500/20 whitespace-nowrap">
                                                    {res.candidate_domain}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-right">
                                            <div className="flex flex-col items-end">
                                                <div className={`text-xl font-black ${res.final_score >= 80 ? 'text-success-400' :
                                                    res.final_score >= 60 ? 'text-warn-400' :
                                                        res.final_score >= 40 ? 'text-warn-500' : 'text-danger-400'
                                                    }`}>
                                                    {res.final_score.toFixed(1)}%
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-right">
                                            <button
                                                onClick={() => navigate('/results', { state: { result: res } })}
                                                className="inline-flex items-center gap-2 text-xs font-bold text-brand-400 hover:text-white bg-brand-500/10 hover:bg-brand-500 px-3 py-1.5 rounded-lg transition-all"
                                            >
                                                <ExternalLink className="w-3.5 h-3.5" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Email Modal */}
            {isEmailModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-surface-950/80 backdrop-blur-sm animate-fade-in">
                    <div className="card max-w-2xl w-full p-8 shadow-2xl shadow-brand-500/20 border-brand-500/30">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-black text-white flex items-center gap-3">
                                <Send className="w-6 h-6 text-brand-400" />
                                Send Bulk Email
                            </h2>
                            <button onClick={() => setIsEmailModalOpen(false)} className="text-gray-500 hover:text-white transition-colors">
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="space-y-5">
                            <div className="p-4 rounded-xl bg-brand-500/5 border border-brand-500/20">
                                <span className="text-[10px] font-bold text-brand-400 uppercase tracking-widest block mb-1">Recipients</span>
                                <p className="text-sm font-semibold text-white">
                                    {selectedIndices.length} candidates selected
                                </p>
                            </div>

                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Subject</label>
                                <input
                                    type="text"
                                    value={emailSubject}
                                    onChange={(e) => setEmailSubject(e.target.value)}
                                    className="input-field py-3 text-sm"
                                    placeholder="Interview Invitation - [Company Name]"
                                />
                            </div>

                            <div className="space-y-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Message Body</label>
                                <textarea
                                    value={emailMessage}
                                    onChange={(e) => setEmailMessage(e.target.value)}
                                    className="input-field py-3 text-sm min-h-[150px] resize-none"
                                    placeholder="We are pleased to invite you for an interview..."
                                />
                            </div>

                            <div className="flex items-center gap-4 pt-4">
                                <button
                                    onClick={handleSendBulkEmail}
                                    disabled={isSending}
                                    className="btn-primary flex-1 py-3"
                                >
                                    {isSending ? (
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                    ) : (
                                        <>
                                            <Send className="w-4 h-4" />
                                            Send to all ({selectedIndices.length})
                                        </>
                                    )}
                                </button>
                                <button
                                    onClick={() => setIsEmailModalOpen(false)}
                                    disabled={isSending}
                                    className="btn-secondary py-3 px-6"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Team Prediction Modal */}
            {isTeamModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-surface-950/90 backdrop-blur-md animate-fade-in">
                    <div className="card max-w-4xl w-full p-8 shadow-2xl shadow-accent-500/20 border-accent-500/30 relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent-500 to-brand-500"></div>

                        <div className="flex items-center justify-between mb-8">
                            <div>
                                <h2 className="text-3xl font-black text-white flex items-center gap-3">
                                    <Sparkles className="w-8 h-8 text-accent-400" />
                                    AI Team Prediction
                                </h2>
                                <p className="text-gray-400 text-sm mt-1">
                                    Our AI has analyzed skills, soft skills, and projects to form this dream team.
                                </p>
                            </div>
                            <button onClick={() => setIsTeamModalOpen(false)} className="text-gray-500 hover:text-white transition-colors">
                                <X className="w-8 h-8" />
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {predictedTeam?.map((item, i) => (
                                <div key={i} className="flex flex-col p-6 rounded-2xl bg-surface-800 border border-surface-700 hover:border-accent-500/50 transition-all group">
                                    <span className="text-[10px] font-black text-accent-400 uppercase tracking-[0.2em] mb-4 bg-accent-500/10 w-fit px-2 py-1 rounded">
                                        {item.role}
                                    </span>
                                    <h3 className="text-xl font-bold text-white group-hover:text-accent-300 transition-colors">
                                        {item.candidate.candidate_name || 'Anonymous'}
                                    </h3>
                                    <p className="text-xs text-gray-500 font-mono mt-1 mb-4 truncate">{item.candidate.filename}</p>

                                    <div className="space-y-3 mt-auto">
                                        <div className="flex justify-between items-end">
                                            <span className="text-[10px] text-gray-500 font-bold uppercase">Matched Skills</span>
                                            <span className="text-xs font-bold text-white">{item.candidate.matched_skills.length}</span>
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                            {item.candidate.matched_skills.slice(0, 3).map((s, si) => (
                                                <span key={si} className="text-[9px] px-1.5 py-0.5 rounded-full bg-surface-700 text-gray-400 border border-surface-600">
                                                    {s}
                                                </span>
                                            ))}
                                        </div>

                                        <div className="pt-4 border-t border-surface-700 flex items-center justify-between">
                                            <div className="text-center">
                                                <p className="text-[9px] text-gray-500 uppercase font-black">Score</p>
                                                <p className="text-lg font-black text-white">{item.candidate.final_score.toFixed(0)}%</p>
                                            </div>
                                            <button
                                                onClick={() => navigate('/results', { state: { result: item.candidate } })}
                                                className="p-2 rounded-lg bg-surface-700 text-accent-400 hover:bg-accent-500 hover:text-white transition-all"
                                            >
                                                <ExternalLink className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-10 flex justify-center">
                            <button
                                onClick={() => setIsTeamModalOpen(false)}
                                className="btn-secondary px-10 py-3 uppercase tracking-widest text-xs font-black"
                            >
                                Back to Results
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
