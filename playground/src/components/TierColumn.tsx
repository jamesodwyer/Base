import { useState, useCallback } from "react";
import type { Token } from "../types";
import { groupTokensByCategory, TIER_COLORS } from "../utils/tokenHelpers";
import { TokenRow } from "./TokenRow";
import styles from "./TierColumn.module.css";

interface TierColumnProps {
  tier: Token["tier"];
  tokens: Token[];
  selectedToken: string | null;
  highlightedPaths: Set<string>;
  onTokenClick: (path: string) => void;
}

const INITIAL_SHOW_COUNT = 5;

export function TierColumn({
  tier,
  tokens,
  selectedToken,
  highlightedPaths,
  onTokenClick,
}: TierColumnProps) {
  const [collapsedCategories, setCollapsedCategories] = useState<Set<string>>(new Set());
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  const groups = groupTokensByCategory(tokens);
  const tierColor = TIER_COLORS[tier];

  const toggleCategory = useCallback((category: string) => {
    setCollapsedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) next.delete(category);
      else next.add(category);
      return next;
    });
  }, []);

  const toggleExpand = useCallback((category: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) next.delete(category);
      else next.add(category);
      return next;
    });
  }, []);

  const columnClasses = [
    styles.column,
    tier === "semantic" ? styles.columnSemantic : "",
    tier === "brand" ? styles.columnBrand : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={columnClasses}>
      <div className={styles.header}>
        <span className={styles.tierName} style={{ color: tierColor }}>
          {tier.charAt(0).toUpperCase() + tier.slice(1)}
        </span>
        <span className={styles.tokenCount}>{tokens.length}</span>
      </div>
      <div className={styles.body}>
        {groups.map((group) => {
          const isCollapsed = collapsedCategories.has(group.category);
          const isExpanded = expandedCategories.has(group.category);
          const visibleTokens = isExpanded
            ? group.tokens
            : group.tokens.slice(0, INITIAL_SHOW_COUNT);
          const hasMore = group.tokens.length > INITIAL_SHOW_COUNT && !isExpanded;

          return (
            <div key={group.category} className={styles.categoryGroup}>
              <div
                className={styles.categoryHeader}
                onClick={() => toggleCategory(group.category)}
              >
                <span>
                  {isCollapsed ? "\u25b6 " : "\u25bc "}
                  {group.category} ({group.tokens.length})
                </span>
                {group.isComplete && <span className={styles.complete}>\u2713</span>}
              </div>
              {!isCollapsed &&
                visibleTokens.map((token) => (
                  <TokenRow
                    key={token.path}
                    token={token}
                    isHighlighted={highlightedPaths.has(token.path)}
                    onClick={onTokenClick}
                  />
                ))}
              {!isCollapsed && hasMore && (
                <div className={styles.moreIndicator} onClick={() => toggleExpand(group.category)}>
                  +{group.tokens.length - INITIAL_SHOW_COUNT} more...
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
