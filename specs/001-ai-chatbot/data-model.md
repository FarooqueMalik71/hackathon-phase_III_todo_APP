# Data Model: AI-Powered Todo Chatbot

## Entity: Conversation
Represents a single chat session with metadata

**Fields**:
- id: Integer (Primary Key, Auto-increment)
- user_id: String (Foreign Key to User, required)
- created_at: DateTime (Timestamp, required, default: current time)
- updated_at: DateTime (Timestamp, required, default: current time)

**Relationships**:
- One-to-Many with Message entity (conversation has many messages)

**Validation Rules**:
- user_id must exist in User table
- created_at and updated_at must be valid timestamps

## Entity: Message
Individual chat message within a conversation

**Fields**:
- id: Integer (Primary Key, Auto-increment)
- conversation_id: Integer (Foreign Key to Conversation, required)
- role: String (Enum: "user" or "assistant", required)
- content: Text (Message content, required, max length: 2000 characters)
- created_at: DateTime (Timestamp, required, default: current time)

**Relationships**:
- Many-to-One with Conversation entity (message belongs to one conversation)

**Validation Rules**:
- conversation_id must exist in Conversation table
- role must be either "user" or "assistant"
- content must not exceed 2000 characters
- created_at must be valid timestamp

## Entity: Task (Reused from existing Phase II)
Todo item managed through the chat interface (reuses existing task entity structure)

**Fields**:
- id: String (Primary Key, UUID, required)
- user_id: String (Foreign Key to User, required)
- title: String (Task title, required, max length: 200 characters)
- description: Text (Task description, optional, max length: 1000 characters)
- completed: Boolean (Completion status, required, default: false)
- due_date: DateTime (Due date, optional)
- priority: String (Enum: "low", "medium", "high", optional)
- created_at: DateTime (Timestamp, required, default: current time)
- updated_at: DateTime (Timestamp, required, default: current time)

**State Transitions**:
- Active → Completed (when marked as complete)
- Completed → Active (when marked as incomplete)

**Validation Rules**:
- user_id must exist in User table
- title must not exceed 200 characters
- priority must be one of allowed values
- due_date must be valid if provided

## Relationships Summary
- User (1) → Conversation (Many)
- Conversation (1) → Message (Many)
- User (1) → Task (Many)