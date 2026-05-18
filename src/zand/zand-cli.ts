#!/usr/bin/env tsx
/**
 * zand-cli.ts — JSON-in JSON-out wrapper for parity testing.
 *
 * Usage: tsx zand-cli.ts '<json>'
 * where <json> = {"fixture": "path", "number": ..., "attention": ..., "content": ..., "star": ...}
 *
 * Outputs the zand result as JSON on stdout. Errors are caught and
 * returned as {"mode": "error", "message": "..."}.
 */
import { zand, InvalidAddressError, JsonObject, BlockLoader } from "./zand.ts";
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";

const args = JSON.parse(process.argv[2] || "{}");
const fixturePath = args.fixture as string;
const block = JSON.parse(readFileSync(fixturePath, "utf8")) as JsonObject;
const here = dirname(fixturePath);

// Generic block_loader (mirrors run-tezt.py block_loader)
const loader: BlockLoader = (name: string) => {
  const path = join(here, `${name}.json`);
  if (existsSync(path)) {
    return JSON.parse(readFileSync(path, "utf8"));
  }
  return null;
};

try {
  const result = zand(
    block,
    args.number ?? null,
    args.attention ?? null,
    args.content ?? null,
    args.star ?? false,
    args.star ? loader : null,
  );
  console.log(JSON.stringify(result));
} catch (e) {
  if (e instanceof InvalidAddressError) {
    console.log(JSON.stringify({ mode: "error", message: e.message }));
  } else {
    console.error(`Error: ${e}`);
    process.exit(1);
  }
}
