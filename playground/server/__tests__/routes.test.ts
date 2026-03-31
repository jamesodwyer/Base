import { describe, it, expect, beforeAll } from "vitest";
import { createApp } from "../routes";
import path from "path";

describe("API routes", () => {
  let app: ReturnType<typeof createApp>;

  beforeAll(() => {
    const tokensDir = path.resolve(__dirname, "../../../tokens");
    app = createApp(tokensDir);
  });

  it("GET /api/tokens returns token graph", async () => {
    const res = await app.request("/api/tokens");
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.tokens).toBeDefined();
    expect(data.stats).toBeDefined();
    expect(data.tokens.length).toBeGreaterThan(400);
    expect(data.stats.total).toBeGreaterThan(400);
  });

  it("GET /api/tokens/:path returns a single token", async () => {
    const res = await app.request("/api/tokens/color.brand.01");
    expect(res.status).toBe(200);
    const token = await res.json();
    expect(token.path).toBe("color.brand.01");
    expect(token.type).toBe("color");
  });

  it("GET /api/tokens/:path returns 404 for unknown token", async () => {
    const res = await app.request("/api/tokens/nonexistent.token");
    expect(res.status).toBe(404);
  });

  it("GET /api/health returns stats", async () => {
    const res = await app.request("/api/health");
    expect(res.status).toBe(200);
    const stats = await res.json();
    expect(stats.total).toBeGreaterThan(400);
    expect(typeof stats.orphans).toBe("number");
    expect(typeof stats.brokenRefs).toBe("number");
    expect(typeof stats.coveragePercent).toBe("number");
  });

  it("GET /api/diff/desktop-mobile returns diff", async () => {
    const res = await app.request("/api/diff/desktop-mobile");
    expect(res.status).toBe(200);
    const diff = await res.json();
    expect(diff.desktopOnly).toBeDefined();
    expect(diff.mobileOnly).toBeDefined();
    expect(diff.shared).toBeDefined();
  });
});
