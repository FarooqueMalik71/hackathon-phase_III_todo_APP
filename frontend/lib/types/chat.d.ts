export interface Message {
  id: number;
  conversation_id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ToolCall {
  tool: string;
  arguments: Record<string, any>;
  result: {
    success: boolean;
    message?: string;
    error?: string;
    [key: string]: any;
  };
}

export interface ChatRequest {
  conversation_id?: number | null;
  message: string;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
  response_time: number;
}

export interface Conversation {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}
