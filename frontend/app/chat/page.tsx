/**
 * Chat Page Component
 * Main page for the AI chatbot with conversation history
 */
"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { chatAPI } from "@/lib/api/chatAPI";
import { Conversation } from "@/lib/types/chat";
import { MessageCircle, Plus, Trash2, Clock, ArrowLeft } from "lucide-react";
import { motion } from "framer-motion";

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<
    number | null
  >(null);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [showSidebar, setShowSidebar] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true);
      const convs = await chatAPI.getConversations();
      setConversations(convs);

      // Auto-select most recent conversation if none selected
      if (!currentConversationId && convs.length > 0) {
        setCurrentConversationId(convs[0].id);
      }
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const handleNewConversation = () => {
    setCurrentConversationId(null);
  };

  const handleConversationCreated = (conversationId: number) => {
    setCurrentConversationId(conversationId);
    loadConversations(); // Reload to show new conversation in list
  };

  const handleDeleteConversation = async (conversationId: number) => {
    if (!confirm("Are you sure you want to delete this conversation?")) {
      return;
    }

    try {
      await chatAPI.deleteConversation(conversationId);
      setConversations((prev) =>
        prev.filter((c) => c.id !== conversationId)
      );

      // If deleted conversation was selected, clear selection
      if (currentConversationId === conversationId) {
        setCurrentConversationId(null);
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      alert("Failed to delete conversation");
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar - Conversation History */}
      <motion.div
        initial={{ width: showSidebar ? 320 : 0 }}
        animate={{ width: showSidebar ? 320 : 0 }}
        className="bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-hidden"
      >
        <div className="h-full flex flex-col">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 space-y-2">
            <Link
              href="/dashboard"
              className="w-full px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg
                       flex items-center gap-2 transition-colors duration-200 text-sm"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Dashboard</span>
            </Link>
            <button
              onClick={handleNewConversation}
              className="w-full px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg
                       flex items-center justify-center gap-2 transition-colors duration-200"
            >
              <Plus className="w-5 h-5" />
              <span>New Conversation</span>
            </button>
          </div>

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto p-2">
            {isLoadingConversations ? (
              <div className="flex items-center justify-center h-32 text-gray-500">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : conversations.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-gray-500 dark:text-gray-400 px-4 text-center">
                <MessageCircle className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-sm">No conversations yet</p>
              </div>
            ) : (
              <div className="space-y-2">
                {conversations.map((conv) => (
                  <motion.div
                    key={conv.id}
                    whileHover={{ scale: 1.02 }}
                    className={`p-3 rounded-lg cursor-pointer transition-colors duration-200 group
                              ${
                                currentConversationId === conv.id
                                  ? "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
                                  : "bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700"
                              }`}
                    onClick={() => setCurrentConversationId(conv.id)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          Conversation #{conv.id}
                        </p>
                        <div className="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
                          <MessageCircle className="w-3 h-3" />
                          <span>{conv.message_count} messages</span>
                        </div>
                        <div className="flex items-center gap-1 mt-1 text-xs text-gray-400 dark:text-gray-500">
                          <Clock className="w-3 h-3" />
                          <span>{formatDate(conv.updated_at)}</span>
                        </div>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteConversation(conv.id);
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 dark:hover:bg-red-900/20
                                 rounded transition-all duration-200"
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <ChatInterface
          conversationId={currentConversationId}
          onConversationCreated={handleConversationCreated}
        />
      </div>
    </div>
  );
}
