import { API_URL } from "@/lib/constants";
import { useQuery } from "@tanstack/react-query";

export type QuerySuggestion = {
    question: string;
  };
  
  export type SuggestionsResponse = {
    suggestions: QuerySuggestion[];
  };
  
  /**
   * Fetch query suggestions from the API
   */
  export const fetchSuggestions = async (): Promise<SuggestionsResponse> => {
    const response = await fetch(`${API_URL}/api/v1/chat/suggestions`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
  
    if (!response.ok) {
      throw new Error(`Failed to fetch suggestions: ${response.statusText}`);
    }
  
    return response.json();
  };

export const useSuggestions = () => {
  return useQuery({
    queryKey: ["suggestions"],
    queryFn: fetchSuggestions,
    staleTime: Infinity, // Suggestions don't change, cache forever
    gcTime: Infinity, // Keep in cache forever
    retry: 2,
  });
};

