/**
 * Hook for managing AI chat state and interactions
 * Uses the streaming API hook to handle messages
 */

import { useState, useCallback } from "react";
import { nanoid } from "nanoid";
import { useStreamingApi } from "./useStreamingApi";

export type ChatMessage = {
  key: string;
  from: "user" | "assistant";
  model?: string;
  versions: {
    id: string;
    content: string;
  }[];
};

export type ChatStatus = "submitted" | "streaming" | "ready" | "error";

export const useAiChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<ChatStatus>("ready");
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const { streamChat } = useStreamingApi();

  const updateAssistantMessage = useCallback(
    (messageId: string, content: string) => {
      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.versions.some((v) => v.id === messageId)) {
            return {
              ...msg,
              versions: msg.versions.map((v) =>
                v.id === messageId ? { ...v, content } : v
              ),
            };
          }
          return msg;
        })
      );
    },
    []
  );

  const updateAssistantModel = useCallback((messageId: string, model: string) => {
    setMessages((prev) =>
      prev.map((msg) => {
        if (msg.versions.some((v) => v.id === messageId)) {
          return {
            ...msg,
            model,
          };
        }
        return msg;
      })
    );
  }, []);

  const streamResponse = useCallback(
    async (userMessage: string, selectedModel: string, chatId: string) => {
      setStatus("streaming");

      // Create new abort controller for this request
      const controller = new AbortController();
      setAbortController(controller);

      // Create assistant message placeholder
      const assistantMessageId = nanoid();
      const assistantMessage: ChatMessage = {
        key: nanoid(),
        from: "assistant",
        versions: [
          {
            id: assistantMessageId,
            content: "",
          },
        ],
      };

      setMessages((prev) => [...prev, assistantMessage]);

      let currentContent = "";

      try {
        await streamChat(
          userMessage,
          selectedModel,
          chatId,
          {
            onChunk: (chunk: string) => {
              currentContent += chunk;
              updateAssistantMessage(assistantMessageId, currentContent);
            },
            onModel: (model: string) => {
              updateAssistantModel(assistantMessageId, model);
            },
            onComplete: () => {
              setStatus("ready");
              setAbortController(null);
            },
            onError: (error: Error) => {
              if (error.name === "AbortError") {
                console.log("Request was cancelled");
                setStatus("ready");
              } else {
                console.error("Chat error:", error);
                setStatus("error");
                updateAssistantMessage(
                  assistantMessageId,
                  "Sorry, I encountered an error. Please try again."
                );
                setTimeout(() => setStatus("ready"), 2000);
              }
              setAbortController(null);
            },
          },
          controller.signal
        );
      } catch (error) {
        console.error("Stream error:", error);
        setAbortController(null);
      }
    },
    [streamChat, updateAssistantMessage, updateAssistantModel]
  );

  const sendMessage = useCallback(
    (content: string, selectedModel: string, chatId: string) => {
      if (!content.trim()) return;

      setStatus("submitted");

      // Add user message
      const userMessage: ChatMessage = {
        key: nanoid(),
        from: "user",
        versions: [
          {
            id: nanoid(),
            content,
          },
        ],
      };

      setMessages((prev) => [...prev, userMessage]);

      // Stream assistant response
      streamResponse(content, selectedModel, chatId);
    },
    [streamResponse]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setStatus("ready");
  }, []);

  const stopStreaming = useCallback(() => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setStatus("ready");
    }
  }, [abortController]);

  return {
    messages,
    status,
    sendMessage,
    clearMessages,
    stopStreaming,
    isStreaming: status === "streaming",
    isReady: status === "ready",
  };
};

