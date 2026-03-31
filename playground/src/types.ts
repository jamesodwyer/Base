export interface Modifier {
  type: "darken" | "lighten" | "alpha" | "mix";
  value: string;
  space: "hsl" | "lch" | "srgb";
  color?: string;
}

export interface Token {
  path: string;
  tier: "core" | "brand" | "semantic" | "component";
  category: string;
  type: string;
  value: string | number | Record<string, unknown> | Array<Record<string, unknown>>;
  resolvedValue: string | number | Record<string, unknown> | Array<Record<string, unknown>> | null;
  references: string[];
  referencedBy: string[];
  modifier: Modifier | null;
  sourceFile: string;
  description: string;
  isOrphan: boolean;
  hasBrokenRef: boolean;
}

export interface TokenGraph {
  tokens: Token[];
  stats: HealthStats;
}

export interface HealthStats {
  total: number;
  orphans: number;
  brokenRefs: number;
  coveragePercent: number;
  tiers: Record<string, number>;
}

export interface DesktopMobileDiff {
  desktopOnly: string[];
  mobileOnly: string[];
  shared: Array<{
    path: string;
    desktopValue: string | number;
    mobileValue: string | number;
    isDifferent: boolean;
  }>;
}
