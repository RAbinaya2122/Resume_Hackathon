import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { User, Mail, Lock, UserPlus, Loader2, Sparkles, Building2 } from 'lucide-react'
import { register } from '../services/api'

export default function Register() {
    const navigate = useNavigate()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [fullName, setFullName] = useState('')
    const [role, setRole] = useState('candidate')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            await register(email, password, fullName, role)
            alert('Registration successful! Please login.')
            navigate('/login')
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-[90vh] flex items-center justify-center px-4 py-16 animate-fade-in">
            <div className="max-w-md w-full">
                {/* Brand Logo/Icon */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/20 mb-4">
                        <Sparkles className="w-8 h-8 text-brand-400" />
                    </div>
                    <h1 className="text-3xl font-extrabold text-white tracking-tight">Create Account</h1>
                    <p className="text-gray-400 mt-2">Join our AI-powered screening platform</p>
                </div>

                <div className="card p-8 border-brand-500/10 shadow-2xl shadow-brand-500/5">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="p-3 rounded-lg bg-danger-500/10 border border-danger-500/20 text-danger-400 text-xs font-medium animate-shake">
                                {error}
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-3 mb-2 p-1 bg-surface-800 rounded-xl border border-surface-700/50">
                            <button
                                type="button"
                                onClick={() => setRole('candidate')}
                                className={`flex items-center justify-center gap-2 py-2.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all ${role === 'candidate'
                                        ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20 active-scale'
                                        : 'text-gray-500 hover:text-gray-300'
                                    }`}
                            >
                                <User className="w-3.5 h-3.5" />
                                Candidate
                            </button>
                            <button
                                type="button"
                                onClick={() => setRole('recruiter')}
                                className={`flex items-center justify-center gap-2 py-2.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all ${role === 'recruiter'
                                        ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20 active-scale'
                                        : 'text-gray-500 hover:text-gray-300'
                                    }`}
                            >
                                <Building2 className="w-3.5 h-3.5" />
                                Recruiter
                            </button>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Full Name</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500 group-focus-within:text-brand-400 transition-colors">
                                    <User className="w-4.5 h-4.5" />
                                </div>
                                <input
                                    type="text"
                                    required
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="input-field pl-11 py-3 text-sm focus:ring-brand-500/20"
                                    placeholder="John Doe"
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Email Address</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500 group-focus-within:text-brand-400 transition-colors">
                                    <Mail className="w-4.5 h-4.5" />
                                </div>
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="input-field pl-11 py-3 text-sm focus:ring-brand-500/20"
                                    placeholder="name@company.com"
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Password</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500 group-focus-within:text-brand-400 transition-colors">
                                    <Lock className="w-4.5 h-4.5" />
                                </div>
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field pl-11 py-3 text-sm focus:ring-brand-500/20"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary w-full py-3.5 mt-4 shadow-lg shadow-brand-500/20 group overflow-hidden"
                        >
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    <span>Create Account</span>
                                    <UserPlus className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-surface-700 text-center">
                        <p className="text-sm text-gray-500">
                            Already have an account? {' '}
                            <Link to="/login" className="font-bold text-brand-400 hover:text-brand-300 transition-colors">
                                Sign In
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
