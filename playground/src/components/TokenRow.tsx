import type { Token } from "../types";
import { ColorSwatch } from "./ColorSwatch";
import styles from "./TokenRow.module.css";

interface TokenRowProps {
  token: Token;
  isHighlighted: boolean;
  onClick: (path: string) => void;
}

export function TokenRow({ token, isHighlighted, onClick }: TokenRowProps) {
  const shortName = token.path.split(".").slice(-2).join(".");
  const isColor = token.type === "color";
  const resolvedStr = token.resolvedValue != null ? String(token.resolvedValue) : "";

  const rowClasses = [
    styles.row,
    isHighlighted ? styles.rowHighlighted : "",
    token.hasBrokenRef ? styles.rowBroken : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={rowClasses} onClick={() => onClick(token.path)} title={token.description}>
      {isColor && <ColorSwatch value={resolvedStr || token.value} />}
      <span className={styles.name}>{shortName}</span>
      <div className={styles.meta}>
        {token.modifier && (
          <span className={styles.modifier}>
            {token.modifier.type} {token.modifier.value.replace(/\{[^}]+\}/g, "").replace("*", "\u00d7")}
          </span>
        )}
        {token.references.length > 0 && (
          <span className={styles.reference}>
            \u2190 {token.references[0].split(".").slice(-2).join(".")}
          </span>
        )}
        {token.referencedBy.length > 0 && (
          <span className={styles.refCount}>\u2192{token.referencedBy.length}</span>
        )}
        {token.isOrphan && <span className={styles.orphanBadge}>orphan</span>}
        {!isColor && token.references.length === 0 && (
          <span className={styles.rawValue}>{resolvedStr || String(token.value)}</span>
        )}
      </div>
    </div>
  );
}
