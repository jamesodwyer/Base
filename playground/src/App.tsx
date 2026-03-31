import { useState, useMemo, useCallback } from "react";
import { useTokens } from "./hooks/useTokens";
import { useTokenEdit } from "./hooks/useTokenEdit";
import { getReferencedChain } from "./utils/tokenHelpers";
import { StatusBar } from "./components/StatusBar";
import { TierColumn } from "./components/TierColumn";
import { TokenEditor } from "./components/TokenEditor";
import type { Token, TokenGraph } from "./types";
import styles from "./App.module.css";

const TIERS: Token["tier"][] = ["core", "brand", "semantic", "component"];

export function App() {
  const {
    tokens, stats, loading, error,
    search, setSearch,
    viewMode, setViewMode,
    diff,
    selectedToken, setSelectedToken,
    reload, getTokensByTier,
  } = useTokens();

  const [editingToken, setEditingToken] = useState<Token | null>(null);

  const handleTokensUpdate = useCallback(
    (_data: TokenGraph) => {
      reload();
      setEditingToken(null);
    },
    [reload]
  );

  const { updateToken } = useTokenEdit(handleTokensUpdate);

  const highlightedPaths = useMemo(() => {
    if (!selectedToken) return new Set<string>();
    const token = tokens.find((t) => t.path === selectedToken);
    if (!token) return new Set<string>();
    return new Set(getReferencedChain(token, tokens));
  }, [selectedToken, tokens]);

  const handleTokenClick = useCallback(
    (path: string) => {
      if (selectedToken === path) {
        const token = tokens.find((t) => t.path === path);
        if (token) setEditingToken(token);
      } else {
        setSelectedToken(path);
      }
    },
    [selectedToken, tokens, setSelectedToken]
  );

  const handleSave = useCallback(
    (tokenPath: string, newValue: string | number) => {
      updateToken(tokenPath, newValue);
    },
    [updateToken]
  );

  if (loading) return <div className={styles.loading}>Loading tokens...</div>;
  if (error) return <div className={styles.error}>Error: {error}</div>;

  return (
    <div className={styles.app}>
      <StatusBar
        stats={stats}
        search={search}
        onSearchChange={setSearch}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />
      <div className={styles.columns}>
        {TIERS.map((tier) => (
          <TierColumn
            key={tier}
            tier={tier}
            tokens={getTokensByTier(tier)}
            selectedToken={selectedToken}
            highlightedPaths={highlightedPaths}
            onTokenClick={handleTokenClick}
          />
        ))}
      </div>
      {editingToken && (
        <TokenEditor
          token={editingToken}
          allTokens={tokens}
          onSave={handleSave}
          onClose={() => setEditingToken(null)}
        />
      )}
    </div>
  );
}
