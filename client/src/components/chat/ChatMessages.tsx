import {
  MessageBranch,
  MessageBranchContent,
} from "@/components/ai-elements/message";
import { Message, MessageContent } from "@/components/ai-elements/message";
import { MessageResponse } from "@/components/ai-elements/message";
import { Loader } from "@/components/ai-elements/loader";
import type { ChatMessage } from "@/hooks";
import { MessageActions } from "./MessageActions";
import { ModelSelectorLogo } from "../ai-elements/model-selector";
import { ChatTools } from "./ChatTools";

type ChatMessagesProps = {
  messages: ChatMessage[];
  isStreaming: boolean;
  onCopy: (content: string) => void;
  onRegenerate: (messageKey: string) => void;
};

export const ChatMessages = ({
  messages,
  isStreaming,
  onCopy,
  onRegenerate,
}: ChatMessagesProps) => {
  return (
    <div className="space-y-4 py-4">
      {messages.map(({ versions, ...message }, index) => {
        const isLastMessage = index === messages.length - 1;
        const showActions =
          message.from === "assistant" && (!isStreaming || !isLastMessage);

        const messageTools = message.tools || [];
        const showTools = showActions && !isStreaming && messageTools.length > 0;
        const showLoader =
          message.from === "assistant" && isStreaming && isLastMessage;

        return (
          <MessageBranch defaultBranch={0} key={message.key}>
            <MessageBranchContent>
              {versions.map((version) => (
                <Message
                  from={message.from}
                  key={`${message.key}-${version.id}`}
                >
                  <div
                    className={
                      message.from === "user"
                        ? "ml-auto w-fit max-w-[80%] rounded-2xl"
                        : "mr-auto w-fit max-w-[80%]"
                    }
                  >
                    {showLoader && !version.content ? (
                      <Loader />
                    ) : (
                      <>
                        <MessageContent className="prose prose-invert max-w-none">
                          <MessageResponse>{version.content}</MessageResponse>
                          {showTools ? <ChatTools tools={messageTools} /> : null}
                        </MessageContent>

                        {/* Action buttons for AI messages */}
                        {showActions && (
                          <div className="mt-3 flex items-center gap-2">
                            <MessageActions
                              content={version.content}
                              messageKey={message.key}
                              onCopy={onCopy}
                              onRegenerate={onRegenerate}
                              isStreaming={isStreaming}
                            />
                            {message.model && (
                              <span className="text-xs text-muted-foreground flex items-center gap-2">
                                <ModelSelectorLogo
                                  provider={"openai"}
                                  className="size-4"
                                />
                                <span className="text-sm text-muted-foreground -mt-1">
                                  {message.model}
                                </span>
                              </span>
                            )}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </Message>
              ))}
            </MessageBranchContent>
          </MessageBranch>
        );
      })}
    </div>
  );
};
