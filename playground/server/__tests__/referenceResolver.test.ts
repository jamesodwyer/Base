import { describe, it, expect } from "vitest";
import { resolveTokenGraph } from "../referenceResolver";
import type { Token } from "../types";

function makeToken(overrides: Partial<Token>): Token {
  return {
    path: "test.token",
    tier: "core",
    category: "test",
    type: "dimension",
    value: "4px",
    resolvedValue: null,
    references: [],
    referencedBy: [],
    modifier: null,
    sourceFile: "tokens/core/test.json",
    description: "",
    isOrphan: false,
    hasBrokenRef: false,
    ...overrides,
  };
}

describe("resolveTokenGraph", () => {
  it("resolves a direct reference", () => {
    const tokens = [
      makeToken({ path: "core.dimension.100", value: "4px" }),
      makeToken({
        path: "core.dimension.200",
        value: "{core.dimension.100}*2",
        references: ["core.dimension.100"],
      }),
    ];

    const resolved = resolveTokenGraph(tokens);
    const dim200 = resolved.find((t) => t.path === "core.dimension.200");
    expect(dim200!.resolvedValue).toBe("8px");
  });

  it("resolves a simple color reference", () => {
    const tokens = [
      makeToken({ path: "color.brand.01", type: "color", value: "#024dff" }),
      makeToken({
        path: "color.interactive.primary.fill.default",
        tier: "semantic",
        type: "color",
        value: "{color.brand.01}",
        references: ["color.brand.01"],
      }),
    ];

    const resolved = resolveTokenGraph(tokens);
    const fill = resolved.find((t) => t.path === "color.interactive.primary.fill.default");
    expect(fill!.resolvedValue).toBe("#024dff");
  });

  it("populates referencedBy", () => {
    const tokens = [
      makeToken({ path: "color.brand.01", type: "color", value: "#024dff" }),
      makeToken({
        path: "color.interactive.primary.fill.default",
        tier: "semantic",
        type: "color",
        value: "{color.brand.01}",
        references: ["color.brand.01"],
      }),
    ];

    const resolved = resolveTokenGraph(tokens);
    const brand = resolved.find((t) => t.path === "color.brand.01");
    expect(brand!.referencedBy).toContain("color.interactive.primary.fill.default");
  });

  it("marks broken references", () => {
    const tokens = [
      makeToken({
        path: "color.test",
        type: "color",
        value: "{color.nonexistent}",
        references: ["color.nonexistent"],
      }),
    ];

    const resolved = resolveTokenGraph(tokens);
    expect(resolved[0].hasBrokenRef).toBe(true);
  });

  it("marks orphan tokens (unreferenced, non-component)", () => {
    const tokens = [
      makeToken({
        path: "color.accent.purple",
        tier: "brand",
        type: "color",
        value: "#A733FF",
      }),
    ];

    const resolved = resolveTokenGraph(tokens);
    expect(resolved[0].isOrphan).toBe(true);
  });

  it("does not mark component tokens as orphans", () => {
    const tokens = [
      makeToken({
        path: "button.spacing.medium.blockPadding",
        tier: "component",
        type: "spacing",
        value: "{core.dimension.200}",
        references: ["core.dimension.200"],
      }),
    ];

    const resolved = resolveTokenGraph(tokens);
    expect(resolved[0].isOrphan).toBe(false);
  });
});
