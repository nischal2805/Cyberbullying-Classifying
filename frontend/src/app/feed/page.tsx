"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import {
  Send,
  MessageCircle,
  Shield,
  AlertTriangle,
  LogOut,
  User,
  Heart,
  Trash2,
  Search,
  X,
  Star,
  Users,
} from "lucide-react";

interface UserData {
  uid: string;
  email: string;
  displayName?: string;
  reputation?: number;
}

interface Comment {
  id: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: string;
  isBullying: boolean;
  bullyingType?: string;
  confidence?: number;
}

interface Post {
  id: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: string;
  isBullying: boolean;
  bullyingType?: string;
  confidence?: number;
  likes: string[];
  commentCount: number;
}

interface SearchResult {
  uid: string;
  email: string;
  displayName?: string;
  reputation?: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function FeedPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserData | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [newPost, setNewPost] = useState("");
  const [loading, setLoading] = useState(false);
  const [comments, setComments] = useState<{ [key: string]: Comment[] }>({});
  const [newComment, setNewComment] = useState<{ [key: string]: string }>({});
  const [expandedPost, setExpandedPost] = useState<string | null>(null);
  const [loadingComments, setLoadingComments] = useState<{ [key: string]: boolean }>({});
  const [submittingComment, setSubmittingComment] = useState<{ [key: string]: boolean }>({});
  
  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showSearch, setShowSearch] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);

  // Fetch fresh user data from API on mount
  const fetchUserData = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      const response = await axios.get(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const userData = response.data;
      setUser(userData);
      localStorage.setItem("user", JSON.stringify(userData));
    } catch (error) {
      console.error("Failed to fetch user data:", error);
      // Try to use cached data if API fails
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      } else {
        router.push("/login");
      }
    }
  }, [router]);

  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);

  const fetchPosts = useCallback(async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_BASE}/api/posts`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(response.data.posts || []);
    } catch (error) {
      console.error("Failed to fetch posts:", error);
    }
  }, []);

  useEffect(() => {
    if (user) {
      fetchPosts();
    }
  }, [user, fetchPosts]);

  const fetchComments = async (postId: string) => {
    setLoadingComments((prev) => ({ ...prev, [postId]: true }));
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_BASE}/api/posts/${postId}/comments`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setComments((prev) => ({ ...prev, [postId]: response.data.comments || [] }));
    } catch (error) {
      console.error("Failed to fetch comments:", error);
    } finally {
      setLoadingComments((prev) => ({ ...prev, [postId]: false }));
    }
  };

  const handleSubmitPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPost.trim() || !user) return;

    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        `${API_BASE}/api/posts`,
        { content: newPost },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewPost("");
      fetchPosts();
      // Refresh user data to get updated reputation
      fetchUserData();
    } catch (error) {
      console.error("Failed to create post:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (postId: string) => {
    const commentText = newComment[postId];
    if (!commentText?.trim() || !user) return;

    setSubmittingComment((prev) => ({ ...prev, [postId]: true }));
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        `${API_BASE}/api/posts/${postId}/comments`,
        { content: commentText },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewComment((prev) => ({ ...prev, [postId]: "" }));
      fetchComments(postId);
      fetchPosts();
      // Refresh user data to get updated reputation
      fetchUserData();
    } catch (error: any) {
      console.error("Failed to add comment:", error);
      const errorMsg = error.response?.data?.detail || "Failed to post comment. Please try again.";
      alert(errorMsg);
    } finally {
      setSubmittingComment((prev) => ({ ...prev, [postId]: false }));
    }
  };

  const handleDeleteComment = async (postId: string, commentId: string) => {
    if (!confirm("Are you sure you want to delete this comment?")) return;
    
    try {
      const token = localStorage.getItem("token");
      await axios.delete(`${API_BASE}/api/posts/${postId}/comments/${commentId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchComments(postId);
      fetchPosts();
    } catch (error) {
      console.error("Failed to delete comment:", error);
      alert("Failed to delete comment. You can only delete your own comments.");
    }
  };

  const handleLikePost = async (postId: string) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        `${API_BASE}/api/posts/${postId}/like`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchPosts();
    } catch (error) {
      console.error("Failed to like post:", error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/login");
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

  // Search users function
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearchLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_BASE}/api/users/search`, {
        params: { q: searchQuery },
        headers: { Authorization: `Bearer ${token}` },
      });
      setSearchResults(response.data.users || []);
    } catch (error) {
      console.error("Failed to search users:", error);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const getReputationColor = (reputation: number) => {
    if (reputation >= 80) return "text-green-400";
    if (reputation >= 60) return "text-yellow-400";
    if (reputation >= 40) return "text-orange-400";
    return "text-red-400";
  };

  const getReputationBadge = (reputation: number) => {
    if (reputation >= 90) return { label: "Excellent", color: "bg-green-500" };
    if (reputation >= 70) return { label: "Good", color: "bg-blue-500" };
    if (reputation >= 50) return { label: "Fair", color: "bg-yellow-500" };
    if (reputation >= 30) return { label: "Poor", color: "bg-orange-500" };
    return { label: "Critical", color: "bg-red-500" };
  };

  if (!user) {
    return (
      <div className="min-h-screen animated-bg flex items-center justify-center">
        <div className="floating-orb orb-1"></div>
        <div className="floating-orb orb-2"></div>
        <div className="floating-orb orb-3"></div>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  const badge = getReputationBadge(user.reputation || 100);

  return (
    <div className="min-h-screen animated-bg">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-card border-b border-white/10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-purple-400" />
            <h1 className="text-xl font-bold gradient-text">SafeSpace</h1>
          </div>

          <div className="flex items-center gap-4">
            {/* Search Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowSearch(!showSearch)}
              className="p-2 rounded-lg glass-card hover:bg-white/10 transition-colors"
            >
              <Search className="w-5 h-5 text-gray-300" />
            </motion.button>

            {/* User Info - Click to go to Profile */}
            <Link href="/profile" className="flex items-center gap-3 glass-card px-4 py-2 rounded-xl hover:bg-white/10 transition-colors cursor-pointer">
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-purple-400" />
                <span className="text-white font-medium">
                  {user.displayName || user.email?.split("@")[0]}
                </span>
              </div>
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 text-yellow-400" />
                <span className={`font-bold ${getReputationColor(user.reputation || 100)}`}>
                  {user.reputation || 100}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${badge.color} text-white ml-1`}>
                  {badge.label}
                </span>
              </div>
            </Link>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleLogout}
              className="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 transition-colors"
            >
              <LogOut className="w-5 h-5 text-red-400" />
            </motion.button>
          </div>
        </div>
      </header>

      {/* Search Modal */}
      <AnimatePresence>
        {showSearch && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4"
          >
            <div className="glass-card rounded-2xl p-4 border border-white/20">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">Search Users</h3>
                <button
                  onClick={() => {
                    setShowSearch(false);
                    setSearchResults([]);
                    setSearchQuery("");
                  }}
                  className="ml-auto p-1 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="Search by name or email..."
                  className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSearch}
                  disabled={searchLoading}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-xl text-white font-medium transition-colors disabled:opacity-50"
                >
                  {searchLoading ? "..." : <Search className="w-5 h-5" />}
                </motion.button>
              </div>

              {/* Search Results */}
              <div className="max-h-64 overflow-y-auto space-y-2">
                {searchResults.length > 0 ? (
                  searchResults.map((result) => {
                    const userBadge = getReputationBadge(result.reputation || 100);
                    return (
                      <div
                        key={result.uid}
                        className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/10"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <span className="text-white font-bold">
                              {(result.displayName || result.email)?.[0]?.toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <p className="text-white font-medium">
                              {result.displayName || result.email?.split("@")[0]}
                            </p>
                            <p className="text-gray-400 text-sm">{result.email}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Star className="w-4 h-4 text-yellow-400" />
                          <span className={`font-bold ${getReputationColor(result.reputation || 100)}`}>
                            {result.reputation || 100}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${userBadge.color} text-white`}>
                            {userBadge.label}
                          </span>
                        </div>
                      </div>
                    );
                  })
                ) : searchQuery && !searchLoading ? (
                  <p className="text-center text-gray-400 py-4">No users found</p>
                ) : null}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8 relative z-10 pb-16">
        {/* Create Post */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card rounded-2xl p-6 mb-8 border border-white/10"
        >
          <form onSubmit={handleSubmitPost}>
            <textarea
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
              placeholder="What's on your mind? Share something positive..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none h-24"
            />
            <div className="flex justify-between items-center mt-4">
              <p className="text-sm text-gray-400">
                <Shield className="w-4 h-4 inline mr-1" />
                Your post will be analyzed for harmful content
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={loading || !newPost.trim()}
                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl text-white font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                  />
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Post
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </motion.div>

        {/* Posts Feed */}
        <div className="space-y-6">
          <AnimatePresence>
            {posts.map((post, index) => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.1 }}
                className={`glass-card rounded-2xl p-6 border ${
                  post.isBullying ? "border-red-500/50" : "border-white/10"
                }`}
              >
                {/* Post Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                      <span className="text-white font-bold text-lg">
                        {post.userName?.[0]?.toUpperCase() || "U"}
                      </span>
                    </div>
                    <div>
                      <p className="text-white font-medium">{post.userName}</p>
                      <p className="text-gray-400 text-sm">
                        {new Date(post.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  {post.isBullying && (
                    <div className="flex items-center gap-2 px-3 py-1 bg-red-500/20 rounded-full">
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                      <span className="text-red-400 text-sm font-medium">
                        {post.bullyingType || "Harmful"}
                      </span>
                    </div>
                  )}
                </div>

                {/* Post Content */}
                <p className="text-white mb-4 whitespace-pre-wrap">{post.content}</p>

                {/* Post Actions */}
                <div className="flex items-center gap-4 pt-4 border-t border-white/10">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleLikePost(post.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-colors ${
                      post.likes?.includes(user.uid)
                        ? "bg-pink-500/20 text-pink-400"
                        : "bg-white/5 text-gray-400 hover:bg-white/10"
                    }`}
                  >
                    <Heart
                      className={`w-5 h-5 ${
                        post.likes?.includes(user.uid) ? "fill-current" : ""
                      }`}
                    />
                    <span>{post.likes?.length || 0}</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => toggleComments(post.id)}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 text-gray-400 hover:bg-white/10 transition-colors"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>{post.commentCount || 0}</span>
                  </motion.button>
                </div>

                {/* Comments Section */}
                <AnimatePresence>
                  {expandedPost === post.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-4 pt-4 border-t border-white/10"
                    >
                      {/* Add Comment */}
                      <div className="flex gap-2 mb-4">
                        <input
                          type="text"
                          value={newComment[post.id] || ""}
                          onChange={(e) =>
                            setNewComment((prev) => ({
                              ...prev,
                              [post.id]: e.target.value,
                            }))
                          }
                          onKeyDown={(e) => {
                            if (e.key === "Enter" && !submittingComment[post.id]) {
                              handleAddComment(post.id);
                            }
                          }}
                          placeholder="Write a comment..."
                          disabled={submittingComment[post.id]}
                          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                        <motion.button
                          whileHover={{ scale: submittingComment[post.id] ? 1 : 1.05 }}
                          whileTap={{ scale: submittingComment[post.id] ? 1 : 0.95 }}
                          onClick={() => handleAddComment(post.id)}
                          disabled={submittingComment[post.id] || !newComment[post.id]?.trim()}
                          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-xl text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[56px]"
                        >
                          {submittingComment[post.id] ? (
                            <motion.div
                              animate={{ rotate: 360 }}
                              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                              className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                            />
                          ) : (
                            <Send className="w-5 h-5" />
                          )}
                        </motion.button>
                      </div>

                      {/* Comments List */}
                      {loadingComments[post.id] ? (
                        <div className="flex justify-center py-4">
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            className="w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full"
                          />
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {comments[post.id]?.map((comment) => (
                            <div
                              key={comment.id}
                              className={`p-3 rounded-xl ${
                                comment.isBullying
                                  ? "bg-red-500/10 border border-red-500/30"
                                  : "bg-white/5"
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex items-center gap-2 mb-2">
                                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                                    <span className="text-white font-bold text-sm">
                                      {comment.userName?.[0]?.toUpperCase() || "U"}
                                    </span>
                                  </div>
                                  <span className="text-white font-medium text-sm">
                                    {comment.userName}
                                  </span>
                                  <span className="text-gray-500 text-xs">
                                    {new Date(comment.timestamp).toLocaleDateString()}
                                  </span>
                                  {comment.isBullying && (
                                    <span className="text-xs px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full">
                                      {comment.bullyingType || "Harmful"}
                                    </span>
                                  )}
                                </div>
                                
                                {/* Delete Button - Only show for user's own comments */}
                                {comment.userId === user.uid && (
                                  <motion.button
                                    whileHover={{ scale: 1.1 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={() => handleDeleteComment(post.id, comment.id)}
                                    className="p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                                    title="Delete comment"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </motion.button>
                                )}
                              </div>
                              <p className="text-gray-300 text-sm ml-10">
                                {comment.content}
                              </p>
                            </div>
                          ))}
                          {comments[post.id]?.length === 0 && (
                            <p className="text-center text-gray-500 py-4">
                              No comments yet. Be the first to comment!
                            </p>
                          )}
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>

          {posts.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-16"
            >
              <MessageCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-400 mb-2">
                No posts yet
              </h3>
              <p className="text-gray-500">
                Be the first to share something positive!
              </p>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}
