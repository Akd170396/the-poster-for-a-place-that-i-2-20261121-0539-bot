// Entry for make.fun bounty the-poster-for-a-place-that-i-2-20261121-0539.
// Writes the travel poster for VELMARA (a place that does not exist) to
// /output/entry.png. The artwork is rendered by render.py (PIL) and the
// resulting entry.png is committed beside this file; this program copies
// it to the output directory. Set MAKEFUN_OUTPUT_DIR for local testing.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
