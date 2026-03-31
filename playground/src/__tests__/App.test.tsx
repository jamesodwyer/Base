import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { App } from "../App";

// Minimal token graph fixture
const mockTokenGraph = {
  tokens: [
    {
      path: "color.brand.01",
      tier: "brand",
      category: "brand",
      type: "color",
      value: "#024dff",
      resolvedValue: "#024dff",
      references: [],
      referencedBy: [],
      modifier: null,
      sourceFile: "tokens/brand/color.json",
      description: "Primary brand color",
      isOrphan: false,
      hasBrokenRef: false,
    },
  ],
  stats: {
    total: 1,
    orphans: 0,
    brokenRefs: 0,
    coveragePercent: 5,
    tiers: { brand: 1 },
  },
};

const mockDiff = {
  desktopOnly: [],
  mobileOnly: [],
  shared: [],
};

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url === "/api/tokens") {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockTokenGraph),
          });
        }
        if (url === "/api/diff/desktop-mobile") {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockDiff),
          });
        }
        return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
      })
    );
  });

  it("renders loading state initially", () => {
    render(<App />);
    expect(screen.getByText("Loading tokens...")).toBeInTheDocument();
  });

  it("renders the app after tokens load", async () => {
    render(<App />);
    // Wait for loading to finish and StatusBar to appear
    await waitFor(() => {
      expect(screen.getByText("Token Playground")).toBeInTheDocument();
    });
  });

  it("renders all four tier columns after load", async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText("Core")).toBeInTheDocument();
      expect(screen.getByText("Brand")).toBeInTheDocument();
      expect(screen.getByText("Semantic")).toBeInTheDocument();
      expect(screen.getByText("Component")).toBeInTheDocument();
    });
  });

  it("shows stats badges after load", async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText("1 tokens")).toBeInTheDocument();
    });
  });
});
