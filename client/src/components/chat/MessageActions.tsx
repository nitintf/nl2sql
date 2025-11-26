import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { CopyIcon, RefreshCwIcon } from "lucide-react";

type MessageActionsProps = {
  content: string;
  messageKey: string;
  onCopy: (content: string) => void;
  onRegenerate: (messageKey: string) => void;
  isStreaming: boolean;
};

export const MessageActions = ({
  content,
  messageKey,
  onCopy,
  onRegenerate,
  isStreaming,
}: MessageActionsProps) => {
  return (
    <TooltipProvider>
      <div className="flex items-center gap-1">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              className="size-8 p-0"
              onClick={() => onCopy(content)}
            >
              <CopyIcon className="size-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Copy</p>
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              className="size-8 p-0"
              onClick={() => onRegenerate(messageKey)}
              disabled={isStreaming}
            >
              <RefreshCwIcon className="size-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Regenerate</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
};

