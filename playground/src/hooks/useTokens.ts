import { useState, useEffect, useCallback } from "react";
import type { Token, TokenGraph, DesktopMobileDiff } from "../types";
import { searchTokens, filterTokensByTier } from "../utils/tokenHelpers";

interface UseTokensReturn {
  tokens: Token[];
  stats: TokenGraph["stats"] | null;
  loading: boolean;
  error: string | null;
  search: string;
  setSearch: (query: string) => void;
  viewMode: "desktop" | "mobile" | "diff";
  setViewMode: (mode: "desktop" | "mobile" | "diff") => void;
  diff: DesktopMobileDiff | null;
  selectedToken: string | null;
  setSelectedToken: (path: string | null) => void;
  reload: () => Promise<void>;
  getTokensByTier: (tier: Token["tier"]) => Token[];
}

export function useTokens(): UseTokensReturn {
  const [allTokens, setAllTokens] = useState<Token[]>([]);
  const [stats, setStats] = useState<TokenGraph["stats"] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [viewMode, setViewMode] = useState<"desktop" | "mobile" | "diff">("desktop");
  const [diff, setDiff] = useState<DesktopMobileDiff | null>(null);
  const [selectedToken, setSelectedToken] = useState<string | null>(null);

  const fetchTokens = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch("/api/tokens");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: TokenGraph = await res.json();
      setAllTokens(data.tokens);
      setStats(data.stats);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch tokens");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDiff = useCallback(async () => {
    try {
      const res = await fetch("/api/diff/desktop-mobile");
      if (!res.ok) return;
      const data: DesktopMobileDiff = await res.json();
      setDiff(data);
    } catch {
      // Non-critical
    }
  }, []);

  useEffect(() => {
    fetchTokens();
    fetchDiff();
  }, [fetchTokens, fetchDiff]);

  const filteredTokens = search ? searchTokens(allTokens, search) : allTokens;

  const getTokensByTier = useCallback(
    (tier: Token["tier"]) => filterTokensByTier(filteredTokens, tier),
    [filteredTokens]
  );

  return {
    tokens: filteredTokens,
    stats,
    loading,
    error,
    search,
    setSearch,
    viewMode,
    setViewMode,
    diff,
    selectedToken,
    setSelectedToken,
    reload: fetchTokens,
    getTokensByTier,
  };
}
