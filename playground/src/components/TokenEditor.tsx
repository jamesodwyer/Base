import { useState, useMemo } from "react";
import type { Token } from "../types";
import { isColorValue } from "../utils/colorResolver";
import styles from "./TokenEditor.module.css";

interface TokenEditorProps {
  token: Token;
  allTokens: Token[];
  onSave: (tokenPath: string, newValue: string | number) => void;
  onClose: () => void;
}

const TIER_ORDER = ["core", "brand", "semantic", "component"];

export function TokenEditor({ token, allTokens, onSave, onClose }: TokenEditorProps) {
  const [value, setValue] = useState(String(token.value));
  const [showSuggestions, setShowSuggestions] = useState(false);

  const isReference = value.includes("{");
  const isColor = token.type === "color";
  const currentTierIndex = TIER_ORDER.indexOf(token.tier);

  const suggestions = useMemo(() => {
    if (!isReference) return [];
    const query = value.match(/\{([^}]*)$/)?.[1]?.toLowerCase() || "";
    return allTokens
      .filter((t) => {
        const targetTierIndex = TIER_ORDER.indexOf(t.tier);
        return targetTierIndex < currentTierIndex || t.tier === token.tier;
      })
      .filter((t) => t.path.toLowerCase().includes(query))
      .slice(0, 20);
  }, [value, isReference, allTokens, currentTierIndex, token.tier]);

  const handleSave = () => {
    onSave(token.path, value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !showSuggestions) handleSave();
    if (e.key === "Escape") onClose();
  };

  const applySuggestion = (path: string) => {
    const newValue = value.replace(/\{[^}]*$/, `{${path}}`);
    setValue(newValue);
    setShowSuggestions(false);
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.editor} onClick={(e) => e.stopPropagation()}>
        <div className={styles.title}>{token.path}</div>
        <div className={styles.description}>{token.description}</div>

        <div className={styles.label}>Value</div>

        {isColor && (
          <div className={styles.colorPreview}>
            <input
              type="color"
              className={styles.colorInput}
              value={isColorValue(value) ? value : "#000000"}
              onChange={(e) => setValue(e.target.value)}
            />
            <span style={{ fontSize: 10, color: "#888" }}>or type a reference below</span>
          </div>
        )}

        <input
          className={styles.input}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setShowSuggestions(e.target.value.includes("{"));
          }}
          onKeyDown={handleKeyDown}
          autoFocus
        />

        {showSuggestions && suggestions.length > 0 && (
          <div className={styles.suggestions}>
            {suggestions.map((s) => (
              <div key={s.path} className={styles.suggestion} onClick={() => applySuggestion(s.path)}>
                {s.path}
              </div>
            ))}
          </div>
        )}

        <div className={styles.buttons}>
          <button className={styles.cancelButton} onClick={onClose}>Cancel</button>
          <button className={styles.saveButton} onClick={handleSave}>Save</button>
        </div>
      </div>
    </div>
  );
}
