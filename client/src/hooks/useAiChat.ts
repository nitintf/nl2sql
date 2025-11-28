import { useState, useCallback } from "react";
import { nanoid } from "nanoid";
import { useStreamingApi } from "./useStreamingApi";

export type ChatMessage = {
  key: string;
  from: "user" | "assistant";
  model?: string;
  tools?: ChatTool[];
  versions: {
    id: string;
    content: string;
  }[];
};

export type ChatTool = {
  name: string;
  content: string;
  id: string;
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

      const controller = new AbortController();
      setAbortController(controller);

      const assistantMessageId = nanoid();
      const assistantMessageKey = nanoid();
      const assistantMessage: ChatMessage = {
        key: assistantMessageKey,
        from: "assistant",
        tools: [],
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
            onTool: (tool_name: string, tool_call_id: string, content: string) => {
              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.key === assistantMessageKey) {
                    return {
                      ...msg,
                      tools: [
                        ...(msg.tools || []),
                        { name: tool_name, content, id: tool_call_id },
                      ],
                    };
                  }
                  return msg;
                })
              );
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

