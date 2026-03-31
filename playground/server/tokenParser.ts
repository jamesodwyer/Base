import fs from "fs";
import path from "path";
import type { Token, Modifier } from "./types";

const METADATA_KEYS = new Set(["tokenSetOrder", "$themes", "$metadata"]);
const SKIP_FILES = new Set(["$metadata.json", "$themes.json"]);

export function assignTier(filePath: string): Token["tier"] {
  const normalized = filePath.replace(/\\/g, "/");
  if (normalized.includes("/core/") || normalized.includes("/global/")) return "core";
  if (normalized.includes("/brand/")) return "brand";
  if (normalized.includes("/semantic/")) return "semantic";
  if (normalized.includes("/component/")) return "component";
  return "core";
}

export function extractReferences(value: string): string[] {
  const refs: string[] = [];
  const regex = /\{([^}]+)\}/g;
  let match;
  while ((match = regex.exec(value)) !== null) {
    refs.push(match[1]);
  }
  return refs;
}

function extractModifier(extensions: Record<string, unknown> | undefined): Modifier | null {
  if (!extensions) return null;
  const studioTokens = extensions["studio.tokens"] as Record<string, unknown> | undefined;
  if (!studioTokens?.modify) return null;
  const mod = studioTokens.modify as Record<string, string>;
  return {
    type: mod.type as Modifier["type"],
    value: mod.value,
    space: (mod.space || "hsl") as Modifier["space"],
    ...(mod.color ? { color: mod.color } : {}),
  };
}

export function flattenTokens(json: Record<string, unknown>, filePath: string): Token[] {
  const tier = assignTier(filePath);
  const tokens: Token[] = [];

  function walk(obj: Record<string, unknown>, pathParts: string[]): void {
    for (const [key, val] of Object.entries(obj)) {
      if (METADATA_KEYS.has(key)) continue;
      if (key.startsWith("$")) continue;

      const value = val as Record<string, unknown>;
      if (value && typeof value === "object" && "$value" in value) {
        const rawValue = value.$value;
        const tokenPath = [...pathParts, key].join(".");
        const references = typeof rawValue === "string" ? extractReferences(rawValue) : [];
        const modifier = extractModifier(
          value.$extensions as Record<string, unknown> | undefined
        );

        tokens.push({
          path: tokenPath,
          tier,
          category: "",
          type: (value.$type as string) || "unknown",
          value: rawValue as Token["value"],
          resolvedValue: null,
          references,
          referencedBy: [],
          modifier,
          sourceFile: filePath,
          description: (value.$description as string) || "",
          isOrphan: false,
          hasBrokenRef: false,
        });
      } else if (value && typeof value === "object" && !Array.isArray(value)) {
        walk(value, [...pathParts, key]);
      }
    }
  }

  walk(json, []);
  return tokens;
}

function assignCategories(tokens: Token[]): void {
  for (const token of tokens) {
    const parts = token.path.split(".");
    switch (token.tier) {
      case "core": {
        if (parts[0] === "core" && parts.length >= 3) {
          token.category = parts[1] === "color" ? parts[2] : parts[1];
        } else {
          token.category = parts[0];
        }
        break;
      }
      case "brand": {
        if (parts[0] === "color" && parts.length >= 3) {
          token.category = parts[1];
        } else if (parts[0] === "brand") {
          token.category = parts[1];
        } else {
          token.category = parts[0];
        }
        break;
      }
      case "semantic": {
        if (parts[0] === "color" && parts.length >= 4) {
          token.category = `${parts[1]}.${parts[2]}`;
        } else if (parts[0] === "color" && parts.length === 3) {
          token.category = parts[1];
        } else {
          token.category = parts[0];
        }
        break;
      }
      case "component": {
        token.category = parts[0];
        break;
      }
    }
  }
}

export function parseTokenFiles(tokensDir: string): Token[] {
  const allTokens: Token[] = [];

  function walkDir(dir: string): void {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walkDir(fullPath);
      } else if (entry.name.endsWith(".json") && !SKIP_FILES.has(entry.name)) {
        const relativePath = path.relative(path.dirname(tokensDir), fullPath);
        const content = fs.readFileSync(fullPath, "utf-8");
        const json = JSON.parse(content);
        const fileTokens = flattenTokens(json, relativePath);
        allTokens.push(...fileTokens);
      }
    }
  }

  walkDir(tokensDir);
  assignCategories(allTokens);
  return allTokens;
}
