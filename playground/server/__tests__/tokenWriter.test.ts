import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { updateTokenValue } from "../tokenWriter";
import fs from "fs";
import path from "path";
import os from "os";

describe("updateTokenValue", () => {
  let tmpDir: string;
  let testFile: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "token-writer-test-"));
    testFile = path.join(tmpDir, "test.json");
    fs.writeFileSync(
      testFile,
      JSON.stringify(
        {
          color: {
            brand: {
              "01": {
                $type: "color",
                $value: "#024dff",
                $description: "Primary brand color",
              },
            },
          },
        },
        null,
        2
      )
    );
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true });
  });

  it("updates $value at the correct nested path", () => {
    updateTokenValue(testFile, "color.brand.01", "#FF0000");

    const updated = JSON.parse(fs.readFileSync(testFile, "utf-8"));
    expect(updated.color.brand["01"].$value).toBe("#FF0000");
  });

  it("preserves other fields like $type and $description", () => {
    updateTokenValue(testFile, "color.brand.01", "#FF0000");

    const updated = JSON.parse(fs.readFileSync(testFile, "utf-8"));
    expect(updated.color.brand["01"].$type).toBe("color");
    expect(updated.color.brand["01"].$description).toBe("Primary brand color");
  });

  it("throws for a non-existent token path", () => {
    expect(() => {
      updateTokenValue(testFile, "color.brand.99", "#FF0000");
    }).toThrow("Token not found");
  });
});
