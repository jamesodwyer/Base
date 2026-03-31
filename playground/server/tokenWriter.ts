import fs from "fs";

export function updateTokenValue(
  filePath: string,
  tokenPath: string,
  newValue: string | number | Record<string, unknown>
): void {
  const content = fs.readFileSync(filePath, "utf-8");
  const json = JSON.parse(content);

  const parts = tokenPath.split(".");
  let current: Record<string, unknown> = json;

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    if (!(part in current)) {
      throw new Error(`Token not found at path: ${tokenPath}`);
    }
    if (i === parts.length - 1) {
      const tokenNode = current[part] as Record<string, unknown>;
      if (!tokenNode || typeof tokenNode !== "object" || !("$value" in tokenNode)) {
        throw new Error(`Token not found at path: ${tokenPath}`);
      }
      tokenNode.$value = newValue;
    } else {
      current = current[part] as Record<string, unknown>;
    }
  }

  fs.writeFileSync(filePath, JSON.stringify(json, null, 2) + "\n");
}
