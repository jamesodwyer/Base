import type { Token } from "./types";

export function resolveTokenGraph(tokens: Token[]): Token[] {
  const tokenMap = new Map<string, Token>();
  for (const token of tokens) {
    tokenMap.set(token.path, token);
  }

  // Reset mutable fields
  for (const token of tokens) {
    token.referencedBy = [];
    token.resolvedValue = null;
    token.isOrphan = false;
    token.hasBrokenRef = false;
  }

  // Populate referencedBy
  for (const token of tokens) {
    for (const ref of token.references) {
      const target = tokenMap.get(ref);
      if (target) {
        target.referencedBy.push(token.path);
      } else {
        token.hasBrokenRef = true;
      }
    }
  }

  // Resolve values (with cycle protection)
  const resolving = new Set<string>();

  function resolveValue(token: Token): string | number | Record<string, unknown> | Array<Record<string, unknown>> | null {
    if (token.resolvedValue !== null) return token.resolvedValue;
    if (resolving.has(token.path)) return null; // cycle

    resolving.add(token.path);

    const rawValue = token.value;
    if (typeof rawValue !== "string") {
      token.resolvedValue = rawValue;
      resolving.delete(token.path);
      return rawValue;
    }

    // Check if it's a pure reference like "{color.brand.01}"
    const pureRefMatch = rawValue.match(/^\{([^}]+)\}$/);
    if (pureRefMatch && !rawValue.includes("*") && !rawValue.includes("/")) {
      const target = tokenMap.get(pureRefMatch[1]);
      if (target) {
        const resolved = resolveValue(target);
        token.resolvedValue = resolved;
        resolving.delete(token.path);
        return resolved;
      }
    }

    // Check for math expressions like "{core.dimension.100}*2" or "{ref}/2"
    const mathMatch = rawValue.match(/^\{([^}]+)\}\s*([*/+-])\s*(.+)$/);
    if (mathMatch) {
      const [, refPath, operator, operandStr] = mathMatch;
      const target = tokenMap.get(refPath);
      if (target) {
        const resolved = resolveValue(target);
        if (resolved !== null && typeof resolved === "string") {
          const numericBase = parseFloat(resolved);
          const operand = parseFloat(operandStr);
          if (!isNaN(numericBase) && !isNaN(operand)) {
            let result: number;
            switch (operator) {
              case "*": result = numericBase * operand; break;
              case "/": result = numericBase / operand; break;
              case "+": result = numericBase + operand; break;
              case "-": result = numericBase - operand; break;
              default: result = numericBase;
            }
            const unit = resolved.replace(/[\d.-]/g, "");
            token.resolvedValue = unit ? `${result}${unit}` : result.toString();
            resolving.delete(token.path);
            return token.resolvedValue;
          }
        } else if (resolved !== null && typeof resolved === "number") {
          const operand = parseFloat(operandStr);
          if (!isNaN(operand)) {
            let result: number;
            switch (operator) {
              case "*": result = resolved * operand; break;
              case "/": result = resolved / operand; break;
              case "+": result = resolved + operand; break;
              case "-": result = resolved - operand; break;
              default: result = resolved;
            }
            token.resolvedValue = result;
            resolving.delete(token.path);
            return result;
          }
        }
      }
    }

    // No references — raw value is the resolved value
    if (token.references.length === 0) {
      token.resolvedValue = rawValue;
      resolving.delete(token.path);
      return rawValue;
    }

    // Fallback: unresolved
    token.resolvedValue = rawValue;
    resolving.delete(token.path);
    return rawValue;
  }

  for (const token of tokens) {
    resolveValue(token);
  }

  // Mark orphans: unreferenced tokens that aren't in the component tier
  // Also exclude core tokens (they're primitives, being unreferenced is normal)
  for (const token of tokens) {
    if (
      token.referencedBy.length === 0 &&
      token.tier !== "component" &&
      token.tier !== "core"
    ) {
      token.isOrphan = true;
    }
  }

  return tokens;
}
