export type ThreadOut = {
  id: string;
  session_key: string | null;
  created_at: string;
};

export type MessageOut = {
  id: number;
  role: string;
  content: string;
  created_at: string;
  retrieval_debug_id?: string | null;
};

export type MessagesListResponse = {
  thread_id: string;
  messages: MessageOut[];
};

export type PostMessageResponse = {
  assistant_message: string;
  user: MessageOut;
  assistant: MessageOut;
  debug?: Record<string, unknown> | null;
};
