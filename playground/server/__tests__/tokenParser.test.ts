import { describe, it, expect } from "vitest";
import { parseTokenFiles, flattenTokens, assignTier } from "../tokenParser";
import path from "path";

describe("assignTier", () => {
  it("assigns core tier for core/ files", () => {
    expect(assignTier("tokens/core/dimension.json")).toBe("core");
  });

  it("assigns core tier for global/ files", () => {
    expect(assignTier("tokens/global/dimension.json")).toBe("core");
  });

  it("assigns brand tier for brand/ files", () => {
    expect(assignTier("tokens/brand/color.json")).toBe("brand");
  });

  it("assigns semantic tier for semantic/ files", () => {
    expect(assignTier("tokens/semantic/colorLight.json")).toBe("semantic");
  });

  it("assigns component tier for component/ files", () => {
    expect(assignTier("tokens/component/spacing/desktop.json")).toBe("component");
  });
});

describe("flattenTokens", () => {
  it("flattens nested object to dot-path tokens", () => {
    const json = {
      color: {
        brand: {
          "01": {
            $type: "color",
            $value: "#024dff",
            $description: "Primary brand color",
          },
        },
      },
    };

    const tokens = flattenTokens(json, "tokens/brand/color.json");
    expect(tokens).toHaveLength(1);
    expect(tokens[0].path).toBe("color.brand.01");
    expect(tokens[0].type).toBe("color");
    expect(tokens[0].value).toBe("#024dff");
    expect(tokens[0].tier).toBe("brand");
    expect(tokens[0].sourceFile).toBe("tokens/brand/color.json");
  });

  it("extracts modifier from $extensions", () => {
    const json = {
      color: {
        interactive: {
          primary: {
            fill: {
              hover: {
                $type: "color",
                $value: "{color.interactive.primary.fill.default}",
                $description: "Hover state",
                $extensions: {
                  "studio.tokens": {
                    modify: {
                      type: "darken",
                      value: "{core.color.modify.100}",
                      space: "hsl",
                    },
                  },
                },
              },
            },
          },
        },
      },
    };

    const tokens = flattenTokens(json, "tokens/semantic/colorLight.json");
    expect(tokens).toHaveLength(1);
    expect(tokens[0].modifier).toEqual({
      type: "darken",
      value: "{core.color.modify.100}",
      space: "hsl",
    });
  });

  it("extracts references from $value strings", () => {
    const json = {
      core: {
        dimension: {
          "200": {
            $type: "dimension",
            $value: "{core.dimension.100}*2",
            $description: "Small spacing",
          },
        },
      },
    };

    const tokens = flattenTokens(json, "tokens/core/dimension.json");
    expect(tokens[0].references).toEqual(["core.dimension.100"]);
  });

  it("skips $metadata keys like tokenSetOrder", () => {
    const json = { tokenSetOrder: ["core/dimension"] };
    const tokens = flattenTokens(json, "tokens/$metadata.json");
    expect(tokens).toHaveLength(0);
  });
});

describe("parseTokenFiles", () => {
  it("parses the real token files", () => {
    const tokensDir = path.resolve(__dirname, "../../../tokens");
    const tokens = parseTokenFiles(tokensDir);

    // We know there are ~558+ tokens
    expect(tokens.length).toBeGreaterThan(400);

    // Check a known token exists
    const brand01 = tokens.find((t) => t.path === "color.brand.01");
    expect(brand01).toBeDefined();
    expect(brand01!.tier).toBe("brand");
    expect(brand01!.type).toBe("color");

    // Check a dimension token
    const dim100 = tokens.find((t) => t.path === "core.dimension.100");
    expect(dim100).toBeDefined();
    expect(dim100!.tier).toBe("core");
    expect(dim100!.value).toBe("4px");
  });
});
