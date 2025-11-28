import { DatabaseZapIcon } from "lucide-react";

interface ChatHeaderProps {
  chatId: string;
}

export const ChatHeader = ({ chatId }: ChatHeaderProps) => {
  return (
    <div className="shrink-0 border-b border-border/50">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <DatabaseZapIcon className="size-4 text-primary" />
          </div>
          <h1 className="text-lg font-semibold">NL2SQL</h1>
        </div>
        <div className="flex items-center gap-2">
          <p className="text-sm text-muted-foreground">Chat ID:</p>
          <p className="text-sm text-muted-foreground">{chatId}</p>
        </div>
      </div>
    </div>
  );
};
