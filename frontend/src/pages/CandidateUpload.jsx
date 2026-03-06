import { useState } from 'react'
import { FileUp, Loader2, CheckCircle, AlertCircle, FileText, ChevronRight, Sparkles } from 'lucide-react'
import FileDropzone from '../components/FileDropzone'
import { uploadResumeCandidate } from '../services/api'
import SkillGrid from '../components/SkillGrid'

export default function CandidateUpload() {
    const [files, setFiles] = useState([])
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')

    const handleUpload = async () => {
        if (files.length === 0) {
            setError('Please select a file first.')
            return
        }

        setLoading(true)
        setError('')
        setResult(null)

        try {
            const data = await uploadResumeCandidate(files[0])
            setResult(data.data)
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed. Please ensure file is a valid PDF.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="max-w-4xl mx-auto px-4 py-12 animate-slide-up">
            <div className="text-center mb-10">
                <h1 className="text-4xl font-black text-white leading-tight uppercase tracking-tight">
                    Candidate <span className="text-brand-500">Resume Portal</span>
                </h1>
                <p className="text-gray-400 mt-2 text-lg">Upload your resume to get instant AI-extracted insights and skills.</p>
            </div>

            <div className="grid md:grid-cols-5 gap-8 items-start">
                {/* Upload Section */}
                <div className="md:col-span-2 space-y-6">
                    <div className="card p-6 border-brand-500/10">
                        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4">Upload Resume</h2>
                        <FileDropzone
                            files={files}
                            onFilesChange={setFiles}
                            multiple={false}
                            accept={{ 'application/pdf': ['.pdf'] }}
                        />

                        <button
                            onClick={handleUpload}
                            disabled={loading || files.length === 0}
                            className={`btn-primary w-full mt-6 py-4 shadow-lg active-scale ${loading ? 'opacity-70 cursor-wait' : ''}`}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Processing with OCR...
                                </>
                            ) : (
                                <>
                                    <FileUp className="w-5 h-5" />
                                    Submit Application
                                </>
                            )}
                        </button>

                        {error && (
                            <div className="mt-4 p-3 rounded-lg bg-danger-500/10 border border-danger-500/20 text-danger-400 text-xs font-medium animate-shake flex items-center gap-2">
                                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                {error}
                            </div>
                        )}
                    </div>

                    <div className="p-6 rounded-2xl bg-surface-800/30 border border-surface-700/50">
                        <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-3 flex items-center gap-2">
                            <CheckCircle className="w-3.5 h-3.5 text-success-500" />
                            How it works
                        </h3>
                        <ul className="space-y-3">
                            {[
                                'Upload your PDF resume',
                                'AI extracts your contact info',
                                'System identifies 50+ core skills',
                                'Experience & Domain validation'
                            ].map((step, i) => (
                                <li key={i} className="flex items-center gap-2 text-xs text-gray-400">
                                    <ChevronRight className="w-3 h-3 text-brand-500" />
                                    {step}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Result Section */}
                <div className="md:col-span-3">
                    {result ? (
                        <div className="space-y-6 animate-fade-in">
                            <div className="card p-8 border-brand-500/20 shadow-xl shadow-brand-500/5">
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="w-16 h-16 rounded-2xl bg-success-500/10 border border-success-500/20 flex items-center justify-center">
                                        <CheckCircle className="w-8 h-8 text-success-400" />
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-extrabold text-white">Extraction Complete</h2>
                                        <p className="text-gray-400 text-sm">We successfully parsed your profile</p>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-6 mb-8">
                                    <div className="space-y-1">
                                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Candidate Name</span>
                                        <p className="text-lg font-bold text-white">{result.candidate_name || 'Not found'}</p>
                                    </div>
                                    <div className="space-y-1">
                                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Primary Domain</span>
                                        <div className="flex items-center gap-2">
                                            <span className="px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 text-[10px] font-black uppercase border border-brand-500/20">
                                                {result.domain}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="space-y-1">
                                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Email</span>
                                        <p className="text-sm font-medium text-gray-300">{result.email || 'Not found'}</p>
                                    </div>
                                    <div className="space-y-1">
                                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Experience</span>
                                        <p className="text-base font-bold text-white">{result.experience_years} Years</p>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                                        <Sparkles className="w-4 h-4 text-brand-400" />
                                        Extracted Skills ({result.skills?.length})
                                    </h3>
                                    <SkillGrid skills={result.skills} />
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-[500px] flex flex-col items-center justify-center text-center p-12 rounded-3xl border-2 border-dashed border-surface-700 bg-surface-800/10">
                            <div className="w-20 h-20 rounded-full bg-surface-800 border border-surface-700 flex items-center justify-center mb-6">
                                <FileText className="w-10 h-10 text-surface-600" />
                            </div>
                            <h3 className="text-xl font-bold text-gray-400 mb-2">No Data Extracted</h3>
                            <p className="text-sm text-gray-600 max-w-xs">Upload your resume to see the AI power and your extracted profile details.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
