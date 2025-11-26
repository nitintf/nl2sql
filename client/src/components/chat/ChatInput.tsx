import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  type PromptInputMessage,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputTools,
  PromptInputButton,
} from "@/components/ai-elements/prompt-input";
import {
  ModelSelector,
  ModelSelectorContent,
  ModelSelectorEmpty,
  ModelSelectorGroup,
  ModelSelectorInput,
  ModelSelectorItem,
  ModelSelectorList,
  ModelSelectorLogo,
  ModelSelectorLogoGroup,
  ModelSelectorName,
  ModelSelectorTrigger,
} from "@/components/ai-elements/model-selector";
import { Button } from "@/components/ui/button";
import { StopCircleIcon, CheckIcon, MessagesSquareIcon } from "lucide-react";
import type { ChatStatus } from "@/hooks";
import { useState } from "react";

type ChatInputProps = {
  text: string;
  status: ChatStatus;
  isStreaming: boolean;
  selectedModel: string;
  onModelChange: (model: string) => void;
  onTextChange: (text: string) => void;
  onSubmit: (message: PromptInputMessage) => void;
  onStop: () => void;
  newChatClick: () => void;
};

const models = [
  {
    id: "gpt-4o",
    name: "GPT-4o",
    chef: "OpenAI",
    chefSlug: "openai",
    providers: ["openai", "azure"],
  },
  {
    id: "gpt-4o-mini",
    name: "GPT-4o Mini",
    chef: "OpenAI",
    chefSlug: "openai",
    providers: ["openai", "azure"],
  },
  {
    id: "gpt-3.5-turbo",
    name: "GPT-3.5 Turbo",
    chef: "OpenAI",
    chefSlug: "openai",
    providers: ["openai", "azure"],
  },
];

export const ChatInput = ({
  text,
  status,
  isStreaming,
  selectedModel,
  onModelChange,
  onTextChange,
  onSubmit,
  onStop,
  newChatClick,
}: ChatInputProps) => {
  const [modelSelectorOpen, setModelSelectorOpen] = useState(false);

  const selectedModelData = models.find((m) => m.id === selectedModel);

  return (
    <div className="shrink-0 bg-background/80 backdrop-blur-sm">
      <div className="mx-auto w-full max-w-4xl px-4 py-4">
        <div className="rounded-2xl border border-border/50 bg-card/50 shadow-lg shadow-black/5 backdrop-blur-sm">
          <PromptInput  onSubmit={onSubmit}>
            <PromptInputBody>
              <PromptInputTextarea
                onChange={(event) => onTextChange(event.target.value)}
                value={text}
                placeholder="Ask me anything about SQL..."
                className="resize-none border-0 bg-transparent focus-visible:ring-0"
              />
            </PromptInputBody>

            <PromptInputFooter>
              <PromptInputTools>
                <PromptInputButton onClick={newChatClick}>
                  <MessagesSquareIcon className="size-4" />
                  <p>New Chat</p>
                </PromptInputButton>


                <ModelSelector
                  onOpenChange={setModelSelectorOpen}
                  open={modelSelectorOpen}
                >
                  <ModelSelectorTrigger asChild>
                    <PromptInputButton>
                      {selectedModelData?.chefSlug && (
                        <ModelSelectorLogo provider={selectedModelData.chefSlug} />
                      )}
                      {selectedModelData?.name && (
                        <ModelSelectorName>
                          {selectedModelData.name}
                        </ModelSelectorName>
                      )}
                    </PromptInputButton>
                  </ModelSelectorTrigger>
                  <ModelSelectorContent>
                    <ModelSelectorInput placeholder="Search models..." />
                    <ModelSelectorList>
                      <ModelSelectorEmpty>No models found.</ModelSelectorEmpty>
                      <ModelSelectorGroup heading="OpenAI Models">
                        {models.map((m) => (
                          <ModelSelectorItem
                            key={m.id}
                            onSelect={() => {
                              onModelChange(m.id);
                              setModelSelectorOpen(false);
                            }}
                            value={m.id}
                          >
                            <ModelSelectorLogo provider={m.chefSlug} />
                            <ModelSelectorName>{m.name}</ModelSelectorName>
                            <ModelSelectorLogoGroup>
                              {m.providers.map((provider) => (
                                <ModelSelectorLogo
                                  key={provider}
                                  provider={provider}
                                />
                              ))}
                            </ModelSelectorLogoGroup>
                            {selectedModel === m.id ? (
                              <CheckIcon className="ml-auto size-4" />
                            ) : (
                              <div className="ml-auto size-4" />
                            )}
                          </ModelSelectorItem>
                        ))}
                      </ModelSelectorGroup>
                    </ModelSelectorList>
                  </ModelSelectorContent>
                </ModelSelector>
              </PromptInputTools>

              {isStreaming ? (
                <Button
                  type="button"
                  size="sm"
                  onClick={onStop}
                  className="h-8 w-8 p-0"
                >
                  <StopCircleIcon className="h-5 w-5" />
                </Button>
              ) : (
                <PromptInputSubmit disabled={!text.trim()} status={status} />
              )}
            </PromptInputFooter>
          </PromptInput>
        </div>
      </div>
    </div>
  );
};


