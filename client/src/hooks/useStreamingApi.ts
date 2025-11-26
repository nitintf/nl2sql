/**
 * Hook for handling streaming API calls
 * Manages the low-level fetch, streaming, and parsing of SSE data
 */

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export type StreamChunk = {
  token: string;
  tool_name?: string;
  done: boolean;
  model?: string;
};

export type StreamCallbacks = {
  onChunk: (chunk: string) => void;
  onComplete: () => void;
  onError: (error: Error) => void;
  onModel?: (model: string) => void;
  onTool?: (tool_name: string, content: string) => void;
};

export const useStreamingApi = () => {
  const streamChat = async (
    message: string,
    model: string,
    chatId: string,
    callbacks: StreamCallbacks,
    signal?: AbortSignal
  ): Promise<void> => {
    try {
      const response = await fetch(`${API_URL}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message, model, chat_id: chatId }),
        signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No reader available");
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          callbacks.onComplete();
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6)) as StreamChunk;

              if (data.done) {
                callbacks.onComplete();
                return;
              }

              if (data.model && callbacks.onModel) {
                callbacks.onModel(data.model);
              }

              if (data.tool_name && callbacks.onTool) {
                callbacks.onTool(data.tool_name, data.token);
                continue;
              }

              if (data.token) {
                callbacks.onChunk(data.token);
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error streaming response:", error);
      callbacks.onError(
        error instanceof Error ? error : new Error("Unknown error")
      );
    }
  };

  return { streamChat };
};

