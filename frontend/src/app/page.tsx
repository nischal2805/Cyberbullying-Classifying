'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Zap, Brain, ArrowRight, Sparkles, AlertTriangle, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import axios from 'axios';

interface ClassificationResult {
  text: string;
  local_model_label: string | null;
  groq_label: string | null;
  groq_explanation: string | null;
  final_label: string;
  is_bullying: boolean;
  bullying_type: string | null;
}

export default function Home() {
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    
    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('/api/classify', { text: inputText });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze text');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-dark-900/80 backdrop-blur-xl border-b border-dark-500/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-accent-gradient">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-display font-bold gradient-text">CyberGuard</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/detector" className="text-gray-400 hover:text-white transition-colors">
                Detector
              </Link>
              <Link href="/feed" className="text-gray-400 hover:text-white transition-colors">
                Feed
              </Link>
              <Link href="/login" className="btn-secondary text-sm py-2 px-4">
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-dark-700 border border-dark-500 mb-8">
              <Sparkles className="w-4 h-4 text-accent-primary" />
              <span className="text-sm text-gray-400">Powered by Advanced AI</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-display font-bold mb-6">
              <span className="gradient-text">Protect</span> Your Community
              <br />
              <span className="text-white">From Cyberbullying</span>
            </h1>
            
            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-12">
              Advanced AI classification system that detects harmful content in real-time.
              Protect your community with intelligent content moderation.
            </p>
          </motion.div>

          {/* Demo Section */}
          <motion.div
            className="max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="card p-8">
              <h2 className="text-2xl font-display font-bold mb-6 flex items-center gap-3">
                <Zap className="w-6 h-6 text-accent-primary" />
                Try It Now
              </h2>
              
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter any text to analyze for cyberbullying content..."
                className="input-field h-32 resize-none mb-4"
              />
              
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !inputText.trim()}
                className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    Analyze Text
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400"
                >
                  {error}
                </motion.div>
              )}

              {/* Results */}
              <AnimatePresence>
                {result && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="mt-6 space-y-4"
                  >
                    {/* Final Result */}
                    <div className={`p-6 rounded-xl border ${
                      result.is_bullying 
                        ? 'bg-red-500/10 border-red-500/30' 
                        : 'bg-emerald-500/10 border-emerald-500/30'
                    }`}>
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-sm text-gray-400 uppercase tracking-wider">Final Result</span>
                        {result.is_bullying ? (
                          <span className="status-danger flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" />
                            {result.final_label}
                          </span>
                        ) : (
                          <span className="status-safe flex items-center gap-2">
                            <CheckCircle className="w-4 h-4" />
                            Safe Content
                          </span>
                        )}
                      </div>
                      
                      {result.groq_explanation && (
                        <p className="text-gray-300 text-sm">
                          <span className="font-semibold text-accent-primary">Analysis:</span>{' '}
                          {result.groq_explanation}
                        </p>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-display font-bold text-center mb-12">
            Why <span className="gradient-text">CyberGuard</span>?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Brain className="w-8 h-8" />,
                title: 'AI-Powered Detection',
                description: 'Advanced machine learning models for accurate content classification'
              },
              {
                icon: <Zap className="w-8 h-8" />,
                title: 'Real-Time Detection',
                description: 'Instant classification of text content with detailed explanations'
              },
              {
                icon: <Shield className="w-8 h-8" />,
                title: 'Multi-Category Detection',
                description: 'Identifies race, gender, religion-based bullying and general harassment'
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                className="card text-center"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="inline-flex p-4 rounded-2xl bg-accent-gradient mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-display font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-dark-500/50">
        <div className="max-w-7xl mx-auto text-center text-gray-500">
          <p>&copy; 2025 CyberGuard. Built with AI for a safer internet.</p>
        </div>
      </footer>
    </div>
  );
}
