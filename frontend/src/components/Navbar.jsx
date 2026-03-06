import { Link, useLocation, useNavigate } from 'react-router-dom'
import { BrainCircuit, LayoutDashboard, Home, FileSearch, LogIn, LogOut, User, FileUp } from 'lucide-react'
import { logout } from '../services/api'

export default function Navbar() {
    const { pathname } = useLocation()
    const navigate = useNavigate()
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    const navItems = [
        { to: '/', label: 'Home', icon: Home },
    ]

    if (token) {
        if (role === 'recruiter') {
            navItems.push({ to: '/dashboard', label: 'Screening', icon: LayoutDashboard })
            navItems.push({ to: '/history', label: 'History', icon: FileSearch })
        } else {
            navItems.push({ to: '/upload', label: 'Upload Portal', icon: FileUp })
        }
    }

    return (
        <header className="sticky top-0 z-40 border-b border-surface-700/60 bg-surface-900/80 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2.5 group">
                        <div className="w-8 h-8 rounded-lg bg-brand-gradient flex items-center justify-center shadow-glow-brand group-hover:shadow-glow-accent transition-all duration-300">
                            <BrainCircuit className="w-5 h-5 text-white" />
                        </div>
                        <span className="font-bold text-base text-white tracking-tight">
                            Resume<span className="text-gradient">AI</span>
                        </span>
                    </Link>

                    {/* Brand Meta (Hidden on mobile) */}
                    <div className="hidden md:flex items-center px-3 py-1 bg-surface-800 rounded-full border border-surface-700 ml-4">
                        <span className="w-1.5 h-1.5 rounded-full bg-success-500 animate-pulse mr-2"></span>
                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">v1.2 Platform</span>
                    </div>

                    {/* Nav links */}
                    <nav className="hidden lg:flex items-center gap-1 mx-auto">
                        {navItems.map(({ to, label, icon: Icon }) => (
                            <Link
                                key={to}
                                to={to}
                                className={pathname === to ? 'nav-link-active' : 'nav-link'}
                            >
                                <span className="flex items-center gap-1.5">
                                    <Icon className="w-4 h-4" />
                                    {label}
                                </span>
                            </Link>
                        ))}
                    </nav>

                    {/* Auth / CTA */}
                    <div className="flex items-center gap-3">
                        {!token ? (
                            <>
                                <Link to="/login" className="nav-link text-xs">
                                    <span className="flex items-center gap-1.5">
                                        <LogIn className="w-4 h-4" />
                                        Log In
                                    </span>
                                </Link>
                                <Link to="/register" className="btn-primary text-[11px] px-5 py-2 uppercase tracking-wider font-extrabold shadow-glow-brand">
                                    Get Started
                                </Link>
                            </>
                        ) : (
                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-800/50 border border-surface-700">
                                    <div className="w-6 h-6 rounded-full bg-brand-500/20 flex items-center justify-center">
                                        <User className="w-3.5 h-3.5 text-brand-400" />
                                    </div>
                                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                                        {role}
                                    </span>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="p-2 text-gray-500 hover:text-danger-400 transition-colors"
                                    title="Logout"
                                >
                                    <LogOut className="w-5 h-5" />
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    )
}
