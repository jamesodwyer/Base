import { useCallback } from "react";
import type { TokenGraph } from "../types";

interface UseTokenEditReturn {
  updateToken: (
    tokenPath: string,
    newValue: string | number
  ) => Promise<TokenGraph | null>;
}

export function useTokenEdit(
  onSuccess: (data: TokenGraph) => void
): UseTokenEditReturn {
  const updateToken = useCallback(
    async (tokenPath: string, newValue: string | number) => {
      try {
        const res = await fetch(`/api/tokens/${tokenPath}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ value: newValue }),
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.error || `HTTP ${res.status}`);
        }
        const data: TokenGraph = await res.json();
        onSuccess(data);
        return data;
      } catch (err) {
        console.error("Token update failed:", err);
        return null;
      }
    },
    [onSuccess]
  );

  return { updateToken };
}
