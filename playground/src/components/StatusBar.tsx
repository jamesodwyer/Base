import type { HealthStats } from "../types";
import styles from "./StatusBar.module.css";

interface StatusBarProps {
  stats: HealthStats | null;
  search: string;
  onSearchChange: (query: string) => void;
  viewMode: "desktop" | "mobile" | "diff";
  onViewModeChange: (mode: "desktop" | "mobile" | "diff") => void;
}

export function StatusBar({
  stats,
  search,
  onSearchChange,
  viewMode,
  onViewModeChange,
}: StatusBarProps) {
  return (
    <div className={styles.bar}>
      <div className={styles.left}>
        <span className={styles.title}>Token Playground</span>
        <input
          type="text"
          className={styles.search}
          placeholder="Search tokens..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      <div className={styles.right}>
        {stats && (
          <>
            <span className={`${styles.badge} ${styles.badgeTotal}`}>
              {stats.total} tokens
            </span>
            <span className={`${styles.badge} ${styles.badgeOrphans}`}>
              {stats.orphans} orphans
            </span>
            <span className={`${styles.badge} ${styles.badgeBroken}`}>
              {stats.brokenRefs} broken refs
            </span>
            <span className={`${styles.badge} ${styles.badgeCoverage}`}>
              {stats.coveragePercent}% coverage
            </span>
          </>
        )}
        <div className={styles.viewToggle}>
          <span className={styles.viewLabel}>View:</span>
          {(["desktop", "mobile", "diff"] as const).map((mode) => (
            <button
              key={mode}
              className={`${styles.viewButton} ${viewMode === mode ? styles.viewButtonActive : ""}`}
              onClick={() => onViewModeChange(mode)}
            >
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
