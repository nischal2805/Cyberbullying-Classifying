'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, User, Mail, AlertTriangle, 
  LogOut, ArrowLeft, TrendingDown, TrendingUp
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import axios from 'axios';

interface UserData {
  id: string;
  email: string;
  username: string;
  reputation_score: number;
  is_banned: boolean;
}

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token || !userData) {
      router.push('/login');
      return;
    }
    
    setUser(JSON.parse(userData));
    
    // Fetch latest user data from API
    fetchUserData(token);
  }, [router]);

  const fetchUserData = async (token: string) => {
    try {
      const response = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
    } catch (err) {
      console.error('Failed to fetch user data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  const getReputationColor = (score: number) => {
    if (score >= 8) return 'text-emerald-400';
    if (score >= 5) return 'text-amber-400';
    return 'text-red-400';
  };

  const getReputationBg = (score: number) => {
    if (score >= 8) return 'bg-emerald-500';
    if (score >= 5) return 'bg-amber-500';
    return 'bg-red-500';
  };

  const getReputationStatus = (score: number) => {
    if (score >= 8) return 'Excellent';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Fair';
    return 'At Risk';
  };

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-accent-primary/30 border-t-accent-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-dark-900/80 backdrop-blur-xl border-b border-dark-500/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-accent-gradient">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-display font-bold gradient-text">CyberGuard</span>
            </Link>
            
            <div className="flex items-center gap-4">
              <Link href="/feed" className="text-gray-400 hover:text-white transition-colors">
                Feed
              </Link>
              <Link href="/detector" className="text-gray-400 hover:text-white transition-colors">
                Detector
              </Link>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5 text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-2xl mx-auto">
          {/* Back Link */}
          <Link 
            href="/feed" 
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Feed
          </Link>

          {/* Profile Header */}
          <motion.div
            className="card p-8 mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex items-center gap-6 mb-6">
              <div className="w-20 h-20 rounded-full bg-accent-gradient flex items-center justify-center">
                <span className="text-3xl font-bold text-white">
                  {user.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h1 className="text-2xl font-display font-bold mb-1">{user.username}</h1>
                <div className="flex items-center gap-2 text-gray-400">
                  <Mail className="w-4 h-4" />
                  <span>{user.email}</span>
                </div>
              </div>
            </div>

            {user.is_banned && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-400">
                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                <span>Your account has been restricted due to policy violations.</span>
              </div>
            )}
          </motion.div>

          {/* Reputation Card */}
          <motion.div
            className="card p-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <Shield className="w-5 h-5 text-accent-primary" />
              Reputation Score
            </h2>

            {/* Score Display */}
            <div className="text-center mb-8">
              <div className={`text-6xl font-display font-bold mb-2 ${getReputationColor(user.reputation_score)}`}>
                {user.reputation_score}
                <span className="text-2xl text-gray-500">/10</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                {user.reputation_score >= 5 ? (
                  <TrendingUp className={`w-5 h-5 ${getReputationColor(user.reputation_score)}`} />
                ) : (
                  <TrendingDown className={`w-5 h-5 ${getReputationColor(user.reputation_score)}`} />
                )}
                <span className={`font-semibold ${getReputationColor(user.reputation_score)}`}>
                  {getReputationStatus(user.reputation_score)}
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="h-3 bg-dark-800 rounded-full overflow-hidden">
                <motion.div 
                  className={`h-full ${getReputationBg(user.reputation_score)} rounded-full`}
                  initial={{ width: 0 }}
                  animate={{ width: `${(user.reputation_score / 10) * 100}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                />
              </div>
            </div>

            {/* Info */}
            <div className="p-4 rounded-xl bg-dark-800 border border-dark-500">
              <h3 className="font-semibold mb-2">How it works</h3>
              <ul className="text-sm text-gray-400 space-y-2">
                <li>- Your reputation starts at 10 points</li>
                <li>- Every 2 flagged comments reduces your score by 1</li>
                <li>- Accounts below 5 points are restricted</li>
                <li>- Be respectful to maintain a good reputation</li>
              </ul>
            </div>
          </motion.div>

          {/* Account Actions */}
          <motion.div
            className="mt-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <button
              onClick={handleLogout}
              className="w-full btn-secondary flex items-center justify-center gap-2"
            >
              <LogOut className="w-5 h-5" />
              Sign Out
            </button>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
