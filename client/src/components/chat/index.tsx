import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import type { PromptInputMessage } from "@/components/ai-elements/prompt-input";
import { useState } from "react";
import { useAiChat } from "@/hooks";
import { ChatHeader } from "./ChatHeader";
import { ChatEmptyState } from "./ChatEmptyState";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";
import { nanoid } from "nanoid";

const suggestions = [
  "What is SQL?",
  "Explain database normalization",
  "How do I write a JOIN query?",
  "What's the difference between SQL and NoSQL?",
];

interface ChatProps {
  chatId: string;
  setChatId: (chatId: string) => void;
}

export const Chat = ({ chatId, setChatId }: ChatProps) => {
  const [text, setText] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<string>("gpt-4o-mini");

  const { messages, status, sendMessage, stopStreaming, isStreaming, clearMessages } =
    useAiChat();

  const handleSubmit = (message: PromptInputMessage) => {
    const hasText = Boolean(message.text?.trim());

    if (!hasText) {
      return;
    }

    sendMessage(message.text || "", selectedModel, chatId);
    setText("");
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion, selectedModel, chatId);
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const handleRegenerate = (messageKey: string) => {
    const messageIndex = messages.findIndex((m) => m.key === messageKey);
    if (messageIndex > 0) {
      const previousMessage = messages[messageIndex - 1];
      if (previousMessage.from === "user") {
        sendMessage(previousMessage.versions[0].content, selectedModel, chatId);
      }
    }
  };

  const handleNewChat = () => {
    setChatId(nanoid());
    clearMessages();
    setText("");
  };

  return (
    <div className="relative flex h-screen w-full flex-col overflow-hidden bg-gradient-to-b from-background to-background/95 pb-8">
      <ChatHeader chatId={chatId} />

      <div className="flex-1 overflow-hidden">
        <Conversation className="h-full">
          <ConversationContent className="mx-auto max-w-4xl px-4">
            {messages.length === 0 ? (
              <ChatEmptyState
                suggestions={suggestions}
                onSuggestionClick={handleSuggestionClick}
              />
            ) : (
              <ChatMessages
                messages={messages}
                isStreaming={isStreaming}
                onCopy={handleCopy}
                onRegenerate={handleRegenerate}
              />
            )}
          </ConversationContent>
          <ConversationScrollButton />
        </Conversation>
      </div>

      <ChatInput
        text={text}
        status={status}
        isStreaming={isStreaming}
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        onTextChange={setText}
        onSubmit={handleSubmit}
        onStop={stopStreaming}
        newChatClick={handleNewChat}
      />
    </div>
  );
};

export default Chat;

