import {
  InlineCitation,
  InlineCitationCard,
  InlineCitationCardBody,
  InlineCitationCardTrigger,
  InlineCitationCarousel,
  InlineCitationCarouselContent,
  InlineCitationCarouselHeader,
  InlineCitationCarouselIndex,
  InlineCitationCarouselItem,
  InlineCitationCarouselNext,
  InlineCitationCarouselPrev,
  InlineCitationSource,
  InlineCitationText,
} from "@/components/ai-elements/inline-citation";

import { ChatTool } from "@/hooks/useAiChat";
import { ToolCase } from "lucide-react";

interface ChatToolsProps {
  tools: ChatTool[];
}

export const ChatTools = ({ tools }: ChatToolsProps) => {
  return (
    <InlineCitation>
      <InlineCitationText>
        <ToolCase className="size-4 text-primary" />
      </InlineCitationText>
      <InlineCitationCard>
        <InlineCitationCardTrigger sources={tools.map((tool) => tool.name)} />
        <InlineCitationCardBody>
          <InlineCitationCarousel>
            <InlineCitationCarouselHeader>
              <InlineCitationCarouselPrev />
              <InlineCitationCarouselNext />
              <InlineCitationCarouselIndex />
            </InlineCitationCarouselHeader>
            <InlineCitationCarouselContent>
              {tools.map((tool) => (
                <InlineCitationCarouselItem key={tool.id}>
                  <InlineCitationSource
                    description={tool.content}
                    title={tool.name}
                    url={tool.id}
                  />
                </InlineCitationCarouselItem>
              ))}
            </InlineCitationCarouselContent>
          </InlineCitationCarousel>
        </InlineCitationCardBody>
      </InlineCitationCard>
    </InlineCitation>
  );
};
