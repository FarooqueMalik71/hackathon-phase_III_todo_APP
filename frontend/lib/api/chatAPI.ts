import axios, { AxiosInstance } from "axios";
import {
  ChatRequest,
  ChatResponse,
  Conversation,
  Message,
} from "@/lib/types/chat";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ChatAPIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 0,
    });

    // Add auth token from localStorage to every request
    this.client.interceptors.request.use((config) => {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("auth-token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    });
  }

  /**
   * Send a chat message (auth-protected, user from JWT)
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>(
      `/api/chat`,
      request
    );
    return response.data;
  }

  /**
   * Get all conversations for the authenticated user
   */
  async getConversations(limit: number = 50): Promise<Conversation[]> {
    const response = await this.client.get<Conversation[]>(
      `/api/conversations`,
      { params: { limit } }
    );
    return response.data;
  }

  /**
   * Get messages for a specific conversation
   */
  async getConversationMessages(
    conversationId: number,
    limit: number = 100
  ): Promise<Message[]> {
    const response = await this.client.get<Message[]>(
      `/api/conversations/${conversationId}/messages`,
      { params: { limit } }
    );
    return response.data;
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: number): Promise<void> {
    await this.client.delete(
      `/api/conversations/${conversationId}`
    );
  }
}

// Export singleton instance
export const chatAPI = new ChatAPIService();

// Export class for custom instances
export default ChatAPIService;
