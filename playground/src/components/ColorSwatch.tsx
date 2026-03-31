import { isColorValue } from "../utils/colorResolver";

interface ColorSwatchProps {
  value: unknown;
  size?: number;
}

export function ColorSwatch({ value, size = 14 }: ColorSwatchProps) {
  if (!isColorValue(value)) return null;

  const colorStr = String(value);
  const isTransparent = colorStr.includes(",0)") || colorStr === "transparent";

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: 3,
        flexShrink: 0,
        background: isTransparent ? "transparent" : colorStr,
        border: isTransparent ? "1px dashed #666" : `1px solid ${colorStr}33`,
      }}
    />
  );
}
