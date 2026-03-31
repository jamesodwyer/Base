import type { Token } from "../types";

export interface TokenGroup {
  category: string;
  tokens: Token[];
  isComplete: boolean;
}

export function groupTokensByCategory(tokens: Token[]): TokenGroup[] {
  const groups = new Map<string, Token[]>();

  for (const token of tokens) {
    const existing = groups.get(token.category) || [];
    existing.push(token);
    groups.set(token.category, existing);
  }

  return Array.from(groups.entries()).map(([category, groupTokens]) => ({
    category,
    tokens: groupTokens,
    isComplete: groupTokens.every((t) => !t.hasBrokenRef),
  }));
}

export function filterTokensByTier(tokens: Token[], tier: Token["tier"]): Token[] {
  return tokens.filter((t) => t.tier === tier);
}

export function searchTokens(tokens: Token[], query: string): Token[] {
  if (!query.trim()) return tokens;
  const lower = query.toLowerCase();
  return tokens.filter(
    (t) =>
      t.path.toLowerCase().includes(lower) ||
      t.description.toLowerCase().includes(lower) ||
      String(t.resolvedValue).toLowerCase().includes(lower)
  );
}

export function getReferencedChain(token: Token, allTokens: Token[]): string[] {
  const chain: string[] = [token.path];
  const tokenMap = new Map(allTokens.map((t) => [t.path, t]));

  // Walk upstream (what this token references)
  let current = token;
  while (current.references.length > 0) {
    const ref = current.references[0];
    if (chain.includes(ref)) break;
    chain.unshift(ref);
    const target = tokenMap.get(ref);
    if (!target) break;
    current = target;
  }

  // Walk downstream (what references this token)
  function addDownstream(path: string): void {
    const t = tokenMap.get(path);
    if (!t) return;
    for (const dep of t.referencedBy) {
      if (!chain.includes(dep)) {
        chain.push(dep);
        addDownstream(dep);
      }
    }
  }
  addDownstream(token.path);

  return chain;
}

export const TIER_COLORS: Record<Token["tier"], string> = {
  core: "#7fdbca",
  brand: "#c792ea",
  semantic: "#f78c6c",
  component: "#ffcb6b",
};
