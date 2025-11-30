'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, Brain, Sparkles, AlertTriangle, CheckCircle, 
  ArrowRight, RotateCcw, Copy, Check, ChevronDown
} from 'lucide-react';
import Link from 'next/link';
import axios from 'axios';

interface ClassificationResult {
  text: string;
  local_model_label: string | null;
  gemini_label: string | null;
  gemini_explanation: string | null;
  final_label: string;
  is_bullying: boolean;
  bullying_type: string | null;
}

const exampleTexts = [
  "Hello, how are you today?",
  "You're such an idiot, nobody likes you",
  "I hate people from your country, go back where you came from",
  "Women shouldn't be allowed to vote",
  "Your religion is stupid and evil",
  "Great work on the project, really impressed!",
];

export default function DetectorPage() {
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [showExamples, setShowExamples] = useState(false);

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

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setInputText('');
    setResult(null);
    setError('');
  };

  const handleExampleClick = (text: string) => {
    setInputText(text);
    setShowExamples(false);
  };

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
              <Link href="/" className="text-gray-400 hover:text-white transition-colors">
                Home
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

      {/* Main Content */}
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="text-4xl font-display font-bold mb-4">
              <span className="gradient-text">AI-Powered</span> Detector
            </h1>
            <p className="text-gray-400 text-lg">
              Analyze any text for cyberbullying content using our dual-AI system
            </p>
          </motion.div>

          {/* Input Section */}
          <motion.div
            className="card p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Brain className="w-5 h-5 text-accent-primary" />
                Input Text
              </h2>
              <div className="relative">
                <button
                  onClick={() => setShowExamples(!showExamples)}
                  className="text-sm text-accent-primary hover:text-accent-secondary transition-colors flex items-center gap-1"
                >
                  Try Examples
                  <ChevronDown className={`w-4 h-4 transition-transform ${showExamples ? 'rotate-180' : ''}`} />
                </button>
                
                <AnimatePresence>
                  {showExamples && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="absolute right-0 top-full mt-2 w-80 bg-dark-700 border border-dark-500 rounded-xl shadow-xl z-10 overflow-hidden"
                    >
                      {exampleTexts.map((text, i) => (
                        <button
                          key={i}
                          onClick={() => handleExampleClick(text)}
                          className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-dark-600 transition-colors border-b border-dark-500 last:border-0"
                        >
                          {text.length > 50 ? text.slice(0, 50) + '...' : text}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter or paste text here to analyze for cyberbullying content..."
              className="input-field h-40 resize-none mb-4"
            />

            <div className="flex gap-3">
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !inputText.trim()}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Analyze with AI
                  </>
                )}
              </button>
              
              <button
                onClick={handleReset}
                className="btn-secondary px-4"
                title="Reset"
              >
                <RotateCcw className="w-5 h-5" />
              </button>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400"
              >
                {error}
              </motion.div>
            )}
          </motion.div>

          {/* Results Section */}
          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                {/* Final Result Card */}
                <div className={`card p-8 border-2 ${
                  result.is_bullying 
                    ? 'border-red-500/50 bg-red-500/5' 
                    : 'border-emerald-500/50 bg-emerald-500/5'
                }`}>
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      {result.is_bullying ? (
                        <div className="p-4 rounded-2xl bg-red-500/20">
                          <AlertTriangle className="w-8 h-8 text-red-400" />
                        </div>
                      ) : (
                        <div className="p-4 rounded-2xl bg-emerald-500/20">
                          <CheckCircle className="w-8 h-8 text-emerald-400" />
                        </div>
                      )}
                      <div>
                        <h3 className="text-2xl font-display font-bold">
                          {result.is_bullying ? 'Content Flagged' : 'Content Safe'}
                        </h3>
                        <p className="text-gray-400">
                          Classification: <span className="font-semibold text-white">{result.final_label}</span>
                        </p>
                      </div>
                    </div>
                    
                    <button
                      onClick={handleCopy}
                      className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors"
                      title="Copy result"
                    >
                      {copied ? (
                        <Check className="w-5 h-5 text-emerald-400" />
                      ) : (
                        <Copy className="w-5 h-5 text-gray-400" />
                      )}
                    </button>
                  </div>

                  {result.gemini_explanation && (
                    <div className="p-4 rounded-xl bg-dark-800 border border-dark-500">
                      <p className="text-sm text-gray-400 mb-1">AI Explanation</p>
                      <p className="text-white">{result.gemini_explanation}</p>
                    </div>
                  )}
                </div>

                {/* Model Comparison */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Local Model */}
                  <div className="card p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-2 rounded-lg bg-blue-500/20">
                        <Brain className="w-5 h-5 text-blue-400" />
                      </div>
                      <div>
                        <h4 className="font-semibold">Local Model</h4>
                        <p className="text-xs text-gray-500">HuggingFace - DistilBERT</p>
                      </div>
                    </div>
                    <div className={`p-4 rounded-xl ${
                      result.local_model_label === 'Not Cyberbullying'
                        ? 'bg-emerald-500/10 border border-emerald-500/30'
                        : 'bg-red-500/10 border border-red-500/30'
                    }`}>
                      <p className="font-semibold text-lg">
                        {result.local_model_label || 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Gemini API */}
                  <div className="card p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-2 rounded-lg bg-purple-500/20">
                        <Sparkles className="w-5 h-5 text-purple-400" />
                      </div>
                      <div>
                        <h4 className="font-semibold">Gemini API</h4>
                        <p className="text-xs text-gray-500">Google - Gemini 2.0 Flash</p>
                      </div>
                    </div>
                    <div className={`p-4 rounded-xl ${
                      result.gemini_label === 'Not Cyberbullying'
                        ? 'bg-emerald-500/10 border border-emerald-500/30'
                        : 'bg-red-500/10 border border-red-500/30'
                    }`}>
                      <p className="font-semibold text-lg">
                        {result.gemini_label || 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Analyzed Text */}
                <div className="card p-6">
                  <h4 className="font-semibold mb-3 text-gray-400">Analyzed Text</h4>
                  <p className="text-white bg-dark-800 p-4 rounded-xl border border-dark-500">
                    "{result.text}"
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Info Section */}
          {!result && (
            <motion.div
              className="grid md:grid-cols-3 gap-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              {[
                {
                  title: 'Dual AI Analysis',
                  description: 'Get results from both local ML model and Gemini API for comparison',
                  icon: <Brain className="w-6 h-6" />
                },
                {
                  title: 'Instant Results',
                  description: 'Real-time classification with detailed explanations',
                  icon: <Sparkles className="w-6 h-6" />
                },
                {
                  title: '5 Categories',
                  description: 'Detects race, gender, religion-based bullying and general harassment',
                  icon: <Shield className="w-6 h-6" />
                }
              ].map((item, i) => (
                <div key={i} className="card p-6 text-center">
                  <div className="inline-flex p-3 rounded-xl bg-accent-primary/20 text-accent-primary mb-4">
                    {item.icon}
                  </div>
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-gray-400">{item.description}</p>
                </div>
              ))}
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}
