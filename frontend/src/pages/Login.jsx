import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, Lock, LogIn, Loader2, ShieldCheck, UserCog } from 'lucide-react'
import { login } from '../services/api'

export default function Login() {
    const navigate = useNavigate()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            const data = await login(email, password)
            if (data.role === 'recruiter') {
                navigate('/dashboard')
            } else {
                navigate('/upload')
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-[80vh] flex items-center justify-center px-4 py-12 animate-fade-in">
            <div className="max-w-md w-full">
                {/* Brand Logo/Icon */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/20 mb-4">
                        <ShieldCheck className="w-8 h-8 text-brand-400" />
                    </div>
                    <h1 className="text-3xl font-extrabold text-white tracking-tight">Welcome Back</h1>
                    <p className="text-gray-400 mt-2">Sign in to your account to continue</p>
                </div>

                <div className="card p-8 border-brand-500/10 shadow-2xl shadow-brand-500/5">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div className="p-3 rounded-lg bg-danger-500/10 border border-danger-500/20 text-danger-400 text-xs font-medium animate-shake">
                                {error}
                            </div>
                        )}

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
                            <div className="flex items-center justify-between ml-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Password</label>
                                <a href="#" className="text-[10px] font-bold text-brand-400 hover:text-brand-300 uppercase tracking-wider transition-colors">Forgot?</a>
                            </div>
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
                            className="btn-primary w-full py-3.5 mt-2 shadow-lg shadow-brand-500/20 group overflow-hidden"
                        >
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    <span>Sign In</span>
                                    <LogIn className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-surface-700 text-center">
                        <p className="text-sm text-gray-500">
                            Don't have an account? {' '}
                            <Link to="/register" className="font-bold text-brand-400 hover:text-brand-300 transition-colors">
                                Create Account
                            </Link>
                        </p>
                    </div>
                </div>

                {/* Quick Role Select (Optional for demo) */}
                <div className="mt-8 grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-surface-800/40 border border-surface-700/50 hover:border-brand-500/30 transition-all text-center cursor-default group">
                        <UserCog className="w-5 h-5 text-gray-500 group-hover:text-brand-400 mx-auto mb-2 transition-colors" />
                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Recruiter Portal</span>
                    </div>
                    <div className="p-4 rounded-xl bg-surface-800/40 border border-surface-700/50 hover:border-brand-500/30 transition-all text-center cursor-default group">
                        <ShieldCheck className="w-5 h-5 text-gray-500 group-hover:text-brand-400 mx-auto mb-2 transition-colors" />
                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Candidate Access</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
