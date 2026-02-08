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
  private userId: string;

  constructor(userId: string = "user123") {
    this.userId = userId;
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${userId}`,
      },
      timeout: 30000, // 30 second timeout
    });
  }

  /**
   * Send a chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>(
      `/api/${this.userId}/chat`,
      request
    );
    return response.data;
  }

  /**
   * Get all conversations for the user
   */
  async getConversations(limit: number = 50): Promise<Conversation[]> {
    const response = await this.client.get<Conversation[]>(
      `/api/${this.userId}/conversations`,
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
      `/api/${this.userId}/conversations/${conversationId}/messages`,
      { params: { limit } }
    );
    return response.data;
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: number): Promise<void> {
    await this.client.delete(
      `/api/${this.userId}/conversations/${conversationId}`
    );
  }

  /**
   * Set user ID for authentication
   */
  setUserId(userId: string) {
    this.userId = userId;
    this.client.defaults.headers.Authorization = `Bearer ${userId}`;
  }
}

// Export singleton instance
export const chatAPI = new ChatAPIService();

// Export class for custom instances
export default ChatAPIService;
