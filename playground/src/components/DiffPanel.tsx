import type { DesktopMobileDiff } from "../types";
import styles from "./DiffPanel.module.css";

interface DiffPanelProps {
  diff: DesktopMobileDiff | null;
}

export function DiffPanel({ diff }: DiffPanelProps) {
  if (!diff) return null;

  const different = diff.shared.filter((s) => s.isDifferent);

  return (
    <div className={styles.panel}>
      <div className={styles.title}>DESKTOP vs MOBILE</div>
      {different.slice(0, 3).map((item) => (
        <div key={item.path} className={styles.diffRow}>
          <span>{item.path.split(".").slice(-2).join(".")}</span>
          <span>
            <span className={styles.desktopValue}>{String(item.desktopValue)}</span>
            {" vs "}
            <span className={styles.mobileValue}>{String(item.mobileValue)}</span>
          </span>
        </div>
      ))}
      {diff.desktopOnly.length > 0 && (
        <div className={styles.summary}>
          Desktop has {diff.desktopOnly.length} tokens missing from mobile
        </div>
      )}
      {diff.mobileOnly.length > 0 && (
        <div className={styles.summary}>
          Mobile has {diff.mobileOnly.length} tokens not in desktop
        </div>
      )}
    </div>
  );
}
