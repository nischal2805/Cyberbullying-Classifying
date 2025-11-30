'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, Send, MessageCircle, Heart, AlertTriangle, 
  LogOut, User, PlusCircle, X, Loader2
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

interface Post {
  id: string;
  user_id: string;
  username: string;
  content: string;
  image_url: string | null;
  timestamp: string;
  likes: number;
  comments_count: number;
}

interface Comment {
  id: string;
  user_id: string;
  username: string;
  content: string;
  timestamp: string;
  is_bullying: boolean;
  bullying_type: string | null;
}

export default function FeedPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserData | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showNewPost, setShowNewPost] = useState(false);
  const [newPostContent, setNewPostContent] = useState('');
  const [isPosting, setIsPosting] = useState(false);
  const [expandedPost, setExpandedPost] = useState<string | null>(null);
  const [comments, setComments] = useState<{ [key: string]: Comment[] }>({});
  const [newComment, setNewComment] = useState<{ [key: string]: string }>({});
  const [commentWarning, setCommentWarning] = useState<string | null>(null);

  useEffect(() => {
    // Check auth
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token || !userData) {
      router.push('/login');
      return;
    }
    
    setUser(JSON.parse(userData));
    fetchPosts();
  }, [router]);

  const fetchPosts = async () => {
    try {
      const response = await axios.get('/api/posts');
      setPosts(response.data);
    } catch (err) {
      console.error('Failed to fetch posts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchComments = async (postId: string) => {
    try {
      const response = await axios.get(`/api/posts/${postId}/comments`);
      setComments(prev => ({ ...prev, [postId]: response.data }));
    } catch (err) {
      console.error('Failed to fetch comments:', err);
    }
  };

  const handleCreatePost = async () => {
    if (!newPostContent.trim()) return;
    
    setIsPosting(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/posts', 
        { content: newPostContent },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewPostContent('');
      setShowNewPost(false);
      fetchPosts();
    } catch (err) {
      console.error('Failed to create post:', err);
    } finally {
      setIsPosting(false);
    }
  };

  const handleAddComment = async (postId: string) => {
    const content = newComment[postId];
    if (!content?.trim()) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `/api/posts/${postId}/comments`,
        { post_id: postId, content },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Check if comment was flagged
      if (response.data.is_bullying) {
        setCommentWarning(`Your comment was flagged as "${response.data.bullying_type}" content. This affects your reputation score.`);
        setTimeout(() => setCommentWarning(null), 5000);
        
        // Update user reputation locally
        if (user) {
          const newScore = Math.max(0, user.reputation_score - 0.5);
          setUser({ ...user, reputation_score: newScore });
          localStorage.setItem('user', JSON.stringify({ ...user, reputation_score: newScore }));
        }
      }

      setNewComment(prev => ({ ...prev, [postId]: '' }));
      fetchComments(postId);
      fetchPosts(); // Refresh comment count
    } catch (err) {
      console.error('Failed to add comment:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  const toggleComments = (postId: string) => {
    if (expandedPost === postId) {
      setExpandedPost(null);
    } else {
      setExpandedPost(postId);
      if (!comments[postId]) {
        fetchComments(postId);
      }
    }
  };

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-accent-primary animate-spin" />
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
              <Link href="/detector" className="text-gray-400 hover:text-white transition-colors">
                Detector
              </Link>
              
              {/* User Info */}
              <Link 
                href="/profile"
                className="flex items-center gap-3 px-4 py-2 rounded-xl bg-dark-700 border border-dark-500 hover:border-accent-primary/50 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-accent-gradient flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="text-sm font-semibold">{user?.username}</p>
                  <p className="text-xs text-gray-500">Rep: {user?.reputation_score}/10</p>
                </div>
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

      {/* Warning Toast */}
      <AnimatePresence>
        {commentWarning && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-24 left-1/2 -translate-x-1/2 z-50 px-6 py-4 rounded-xl bg-red-500/20 border border-red-500/50 text-red-400 max-w-md"
          >
            {commentWarning}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-2xl mx-auto">
          {/* Create Post Button */}
          <motion.button
            onClick={() => setShowNewPost(true)}
            className="w-full card p-4 mb-6 flex items-center gap-4 hover:border-accent-primary/50 transition-colors"
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
          >
            <div className="w-10 h-10 rounded-full bg-accent-gradient flex items-center justify-center">
              <PlusCircle className="w-5 h-5 text-white" />
            </div>
            <span className="text-gray-400">What's on your mind?</span>
          </motion.button>

          {/* New Post Modal */}
          <AnimatePresence>
            {showNewPost && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-6"
                onClick={() => setShowNewPost(false)}
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="w-full max-w-lg card p-6"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-display font-bold">Create Post</h3>
                    <button
                      onClick={() => setShowNewPost(false)}
                      className="p-2 rounded-lg hover:bg-dark-600 transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <textarea
                    value={newPostContent}
                    onChange={(e) => setNewPostContent(e.target.value)}
                    placeholder="Share your thoughts..."
                    className="input-field h-32 resize-none mb-4"
                    autoFocus
                  />
                  
                  <div className="flex justify-end gap-3">
                    <button
                      onClick={() => setShowNewPost(false)}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCreatePost}
                      disabled={isPosting || !newPostContent.trim()}
                      className="btn-primary flex items-center gap-2"
                    >
                      {isPosting ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          Post
                        </>
                      )}
                    </button>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Posts */}
          {posts.length === 0 ? (
            <div className="card p-12 text-center">
              <p className="text-gray-400 mb-4">No posts yet. Be the first to share something!</p>
              <button
                onClick={() => setShowNewPost(true)}
                className="btn-primary"
              >
                Create First Post
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {posts.map((post, index) => (
                <motion.div
                  key={post.id}
                  className="card p-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  {/* Post Header */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-full bg-accent-gradient flex items-center justify-center">
                      <span className="text-white font-semibold">
                        {post.username.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <p className="font-semibold">{post.username}</p>
                      <p className="text-xs text-gray-500">{formatDate(post.timestamp)}</p>
                    </div>
                  </div>

                  {/* Post Content */}
                  <p className="text-gray-300 mb-4">{post.content}</p>

                  {/* Post Actions */}
                  <div className="flex items-center gap-4 pt-4 border-t border-dark-500">
                    <button className="flex items-center gap-2 text-gray-400 hover:text-red-400 transition-colors">
                      <Heart className="w-5 h-5" />
                      <span className="text-sm">{post.likes}</span>
                    </button>
                    <button
                      onClick={() => toggleComments(post.id)}
                      className={`flex items-center gap-2 transition-colors ${
                        expandedPost === post.id ? 'text-accent-primary' : 'text-gray-400 hover:text-accent-primary'
                      }`}
                    >
                      <MessageCircle className="w-5 h-5" />
                      <span className="text-sm">{post.comments_count}</span>
                    </button>
                  </div>

                  {/* Comments Section */}
                  <AnimatePresence>
                    {expandedPost === post.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="mt-4 pt-4 border-t border-dark-500 overflow-hidden"
                      >
                        {/* Comments List */}
                        <div className="space-y-3 mb-4">
                          {comments[post.id]?.map((comment) => (
                            <div
                              key={comment.id}
                              className={`p-3 rounded-xl ${
                                comment.is_bullying 
                                  ? 'bg-red-500/10 border border-red-500/30' 
                                  : 'bg-dark-800'
                              }`}
                            >
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-sm font-semibold">{comment.username}</span>
                                <span className="text-xs text-gray-500">{formatDate(comment.timestamp)}</span>
                                {comment.is_bullying && (
                                  <span className="ml-auto flex items-center gap-1 text-xs text-red-400">
                                    <AlertTriangle className="w-3 h-3" />
                                    Flagged
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-gray-300">{comment.content}</p>
                            </div>
                          ))}
                          
                          {comments[post.id]?.length === 0 && (
                            <p className="text-sm text-gray-500 text-center py-2">
                              No comments yet
                            </p>
                          )}
                        </div>

                        {/* Add Comment */}
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={newComment[post.id] || ''}
                            onChange={(e) => setNewComment(prev => ({ ...prev, [post.id]: e.target.value }))}
                            placeholder="Write a comment..."
                            className="input-field flex-1 py-2"
                            onKeyPress={(e) => e.key === 'Enter' && handleAddComment(post.id)}
                          />
                          <button
                            onClick={() => handleAddComment(post.id)}
                            disabled={!newComment[post.id]?.trim()}
                            className="btn-primary py-2 px-4"
                          >
                            <Send className="w-4 h-4" />
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
