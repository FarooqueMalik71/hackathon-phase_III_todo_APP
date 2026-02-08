"use client";

import React, { useState, useEffect, useRef } from "react";
import { chatAPI } from "@/lib/api/chatAPI";
import { Message, ToolCall } from "@/lib/types/chat";
import { notifyTaskChange } from "@/lib/taskSync";
import { Send, Loader2, AlertCircle, MessageCircle, CheckCircle2, XCircle, Wrench, Bot, User } from "lucide-react";

interface ChatInterfaceProps {
  conversationId?: number | null;
  onConversationCreated?: (conversationId: number) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId: initialConversationId = null,
  onConversationCreated,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(initialConversationId);
  const [toolCallsMap, setToolCallsMap] = useState<Record<number, ToolCall[]>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);

  /** Simple markdown to HTML renderer for chat messages */
  const renderMarkdown = (text: string) => {
    if (!text) return "";
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-black/10 dark:bg-white/10 px-1 rounded text-xs">$1</code>')
      .replace(/^(\d+)\.\s/gm, '<span class="text-blue-400 font-medium">$1.</span> ')
      .replace(/^-\s/gm, '<span class="text-blue-400">&#8226;</span> ')
      .replace(/\n/g, '<br/>');
  };

  // Update conversation ID when prop changes
  useEffect(() => {
    setCurrentConversationId(initialConversationId);
    if (initialConversationId) {
      loadConversationMessages(initialConversationId);
    } else {
      setMessages([]);
    }
  }, [initialConversationId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadConversationMessages = async (conversationId: number) => {
    try {
      const msgs = await chatAPI.getConversationMessages(conversationId);
      setMessages(msgs);
      setError(null);
    } catch (error: any) {
      console.error("Failed to load messages:", error);
      setError("Failed to load conversation history");
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setError(null);

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: Date.now(),
      conversation_id: currentConversationId || 0,
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage({
        conversation_id: currentConversationId,
        message: userMessage,
      });

      // Update conversation ID if this was the first message
      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        onConversationCreated?.(response.conversation_id);
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now() + 1,
        conversation_id: response.conversation_id,
        role: "assistant",
        content: response.response,
        created_at: new Date().toISOString(),
      };

      // Store tool calls and notify dashboard of task changes
      if (response.tool_calls.length > 0) {
        setToolCallsMap((prev) => ({
          ...prev,
          [assistantMessage.id]: response.tool_calls,
        }));

        // Notify dashboard to refresh if any task tool was used
        const taskTools = ["add_task", "delete_task", "complete_task", "update_task", "list_tasks"];
        const hasTaskChange = response.tool_calls.some(
          (tc) => taskTools.includes(tc.tool) && tc.result.success
        );
        if (hasTaskChange) {
          notifyTaskChange("tasks-changed");
        }
      }

      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUserMessage.id),
        { ...tempUserMessage, conversation_id: response.conversation_id },
        assistantMessage,
      ]);
    } catch (error: any) {
      console.error("Failed to send message:", error);

      // Remove temp message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));

      // Show user-friendly error
      if (error.response?.status === 503) {
        setError("AI service is temporarily unavailable. Please try again later.");
      } else if (error.response?.status === 404) {
        setError("Chat endpoint not found. Please check backend configuration.");
      } else {
        setError(error.response?.data?.detail?.message || "Failed to send message. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 shadow-lg">
        <div className="flex items-center gap-3">
          <MessageCircle className="w-6 h-6" />
          <div>
            <h2 className="text-lg font-semibold">AI Todo Assistant</h2>
            <p className="text-xs opacity-90">
              {currentConversationId
                ? `Conversation #${currentConversationId}`
                : "Start a new conversation"}
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <MessageCircle className="w-16 h-16 mb-4 opacity-50" />
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm text-center mt-2 max-w-md">
              Try: &quot;Add a task to buy groceries tomorrow&quot; or &quot;List my tasks&quot;
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {/* Avatar for assistant */}
                {message.role === "assistant" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                    message.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  }`}
                >
                  <div
                    className="text-sm whitespace-pre-wrap break-words [&_strong]:font-semibold [&_code]:text-xs"
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }}
                  />

                  {/* Tool calls for assistant messages */}
                  {message.role === "assistant" && toolCallsMap[message.id] && (
                    <div className="mt-3 space-y-2">
                      {toolCallsMap[message.id].map((toolCall, index) => (
                        <div
                          key={index}
                          className="flex items-start gap-2 p-2 rounded-lg bg-white/10 dark:bg-black/20 text-xs border border-white/5"
                        >
                          <Wrench className="w-4 h-4 mt-0.5 flex-shrink-0 text-blue-400" />
                          <div className="flex-1">
                            <p className="font-medium mb-1 capitalize">{toolCall.tool.replace(/_/g, " ")}</p>
                            <div className="flex items-center gap-1">
                              {toolCall.result.success ? (
                                <>
                                  <CheckCircle2 className="w-3 h-3 text-green-500" />
                                  <span className="text-green-600 dark:text-green-400">
                                    {(toolCall.result as any).result?.message || "Done"}
                                  </span>
                                </>
                              ) : (
                                <>
                                  <XCircle className="w-3 h-3 text-red-500" />
                                  <span className="text-red-600 dark:text-red-400">
                                    {toolCall.result.error || "Failed"}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <p className="text-xs opacity-50 mt-2">
                    {new Date(message.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>

                {/* Avatar for user */}
                {message.role === "user" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl px-4 py-3 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                  <span className="text-sm text-gray-500 dark:text-gray-400">Thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}

        {/* Error message */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
        <div className="flex items-end gap-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (English or Roman Urdu)"
            disabled={isLoading}
            rows={1}
            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-2xl
                     bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed resize-none"
            style={{ minHeight: "48px", maxHeight: "120px" }}
          />

          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-2xl
                     disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-500
                     transition-colors duration-200 flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>

        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};
