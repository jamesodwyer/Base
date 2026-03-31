import express, { type Express, type Request, type Response } from "express";
import { IncomingMessage, ServerResponse } from "http";
import { Socket } from "net";
import path from "path";
import { parseTokenFiles } from "./tokenParser";
import { resolveTokenGraph } from "./referenceResolver";
import { updateTokenValue } from "./tokenWriter";
import type { Token, HealthStats, DesktopMobileDiff } from "./types";

// Known framework components for coverage calculation
const FRAMEWORK_COMPONENTS = [
  "button", "icon", "layout", "badge", "selectionControl",
  "card", "input", "accordion", "modal", "tooltip",
  "tabs", "breadcrumb", "pagination", "dropdown", "tag",
  "avatar", "alert", "toast", "skeleton", "divider",
];

function computeStats(tokens: Token[]): HealthStats {
  const orphans = tokens.filter((t) => t.isOrphan).length;
  const brokenRefs = tokens.filter((t) => t.hasBrokenRef).length;
  const tiers: Record<string, number> = {};
  for (const t of tokens) {
    tiers[t.tier] = (tiers[t.tier] || 0) + 1;
  }

  const componentCategories = new Set(
    tokens.filter((t) => t.tier === "component").map((t) => t.category)
  );
  const coveredCount = FRAMEWORK_COMPONENTS.filter((c) => componentCategories.has(c)).length;
  const coveragePercent = Math.round((coveredCount / FRAMEWORK_COMPONENTS.length) * 100);

  return { total: tokens.length, orphans, brokenRefs, coveragePercent, tiers };
}

function computeDesktopMobileDiff(tokens: Token[]): DesktopMobileDiff {
  const desktopTokens = tokens.filter((t) =>
    t.sourceFile.includes("desktop")
  );
  const mobileTokens = tokens.filter((t) =>
    t.sourceFile.includes("mobile")
  );

  const desktopPaths = new Set(desktopTokens.map((t) => t.path));
  const mobilePaths = new Set(mobileTokens.map((t) => t.path));

  const desktopOnly = [...desktopPaths].filter((p) => !mobilePaths.has(p));
  const mobileOnly = [...mobilePaths].filter((p) => !desktopPaths.has(p));

  const sharedPaths = [...desktopPaths].filter((p) => mobilePaths.has(p));
  const shared = sharedPaths.map((p) => {
    const dt = desktopTokens.find((t) => t.path === p)!;
    const mt = mobileTokens.find((t) => t.path === p)!;
    const dv = dt.resolvedValue ?? dt.value;
    const mv = mt.resolvedValue ?? mt.value;
    return {
      path: p,
      desktopValue: typeof dv === "object" ? JSON.stringify(dv) : dv,
      mobileValue: typeof mv === "object" ? JSON.stringify(mv) : mv,
      isDifferent: JSON.stringify(dv) !== JSON.stringify(mv),
    };
  });

  return { desktopOnly, mobileOnly, shared };
}

export function createApp(tokensDir: string) {
  const app: Express = express();
  app.use(express.json());

  let tokens: Token[] = [];

  function reload(): void {
    tokens = parseTokenFiles(tokensDir);
    tokens = resolveTokenGraph(tokens);
  }

  reload();

  app.get("/api/tokens", (_req: Request, res: Response) => {
    const stats = computeStats(tokens);
    res.json({ tokens, stats });
  });

  app.get("/api/tokens/:path(*)", (req: Request, res: Response) => {
    const tokenPath = req.params.path;
    const token = tokens.find((t) => t.path === tokenPath);
    if (!token) {
      res.status(404).json({ error: "Token not found" });
      return;
    }
    res.json(token);
  });

  app.put("/api/tokens/:path(*)", (req: Request, res: Response) => {
    const tokenPath = req.params.path;
    const { value } = req.body;
    if (value === undefined) {
      res.status(400).json({ error: "Missing 'value' in request body" });
      return;
    }

    const token = tokens.find((t) => t.path === tokenPath);
    if (!token) {
      res.status(404).json({ error: "Token not found" });
      return;
    }

    const fullPath = path.resolve(path.dirname(tokensDir), token.sourceFile);
    try {
      updateTokenValue(fullPath, tokenPath, value);
      reload();
      const stats = computeStats(tokens);
      res.json({ tokens, stats });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Write failed";
      res.status(500).json({ error: message });
    }
  });

  app.get("/api/health", (_req: Request, res: Response) => {
    const stats = computeStats(tokens);
    res.json(stats);
  });

  app.get("/api/diff/desktop-mobile", (_req: Request, res: Response) => {
    const diff = computeDesktopMobileDiff(tokens);
    res.json(diff);
  });

  // Test helper: simulates HTTP requests via app.handle() without starting a real server.
  // Uses real IncomingMessage/ServerResponse so Express route matching works correctly.
  //
  // IMPORTANT: We must not overwrite app.request — Express's expressInit middleware calls
  // setPrototypeOf(req, app.request) to set the prototype of incoming requests. If we
  // replace app.request with our function, req.headers becomes undefined and body-parser
  // throws. We use a Proxy to intercept only the 'request' property access for tests
  // while leaving the real app.request prototype intact for Express internals.
  function makeRequest(urlPath: string, options?: { method?: string; body?: unknown }) {
    return new Promise<{ status: number; json: () => Promise<unknown> }>((resolve) => {
      const method = (options?.method || "GET").toUpperCase();

      const socket = new Socket();
      const req = new IncomingMessage(socket);
      req.method = method;
      req.url = urlPath;
      req.headers = {};
      // Pre-populate body so routes can access req.body without streaming
      (req as unknown as Record<string, unknown>).body = options?.body ?? {};

      const rawRes = new ServerResponse(req);
      let chunks = "";
      (rawRes as unknown as Record<string, unknown>).write = (chunk: string | Buffer) => {
        chunks += typeof chunk === "string" ? chunk : chunk.toString();
        return true;
      };
      (rawRes as unknown as Record<string, unknown>).end = (chunk?: string | Buffer) => {
        if (chunk) chunks += typeof chunk === "string" ? chunk : chunk.toString();
        resolve({
          status: rawRes.statusCode,
          json: async () => JSON.parse(chunks) as unknown,
        });
      };

      app.handle(
        req as unknown as Request,
        rawRes as unknown as Response,
        () => {
          resolve({ status: 404, json: async () => ({ error: "Not found" }) });
        }
      );
    });
  }

  // Return a Proxy over the real Express app. The proxy intercepts only 'request'
  // to return our test helper, while the original app.request (the Express IncomingMessage
  // prototype) remains untouched so Express internals work correctly.
  return new Proxy(app, {
    get(target, prop, receiver) {
      if (prop === "request") return makeRequest;
      return Reflect.get(target, prop, receiver);
    },
  }) as Express & { request: typeof makeRequest };
}
