import { Suggestion, Suggestions } from "@/components/ai-elements/suggestion";

type ChatEmptyStateProps = {
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
};

export const ChatEmptyState = ({
  suggestions,
  onSuggestionClick,
}: ChatEmptyStateProps) => {
  return (
    <div className="absolute inset-0 flex items-center justify-center px-4">
      <div className="mx-auto w-full max-w-3xl text-center">
        <h2 className="mb-6 text-2xl font-semibold">Hello, Anonymous</h2>
        <Suggestions wrap>
          {suggestions.map((suggestion) => (
            <Suggestion
              key={suggestion}
              onClick={() => onSuggestionClick(suggestion)}
              suggestion={suggestion}
            />
          ))}
        </Suggestions>
      </div>
    </div>
  );
};

