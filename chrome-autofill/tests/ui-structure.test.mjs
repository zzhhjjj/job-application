import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const manifest = JSON.parse(await readFile(new URL("../manifest.json", import.meta.url), "utf8"));
const popup = await readFile(new URL("../popup.html", import.meta.url), "utf8");
const script = await readFile(new URL("../popup.js", import.meta.url), "utf8");

test("uses the updated extension version", () => {
  assert.equal(manifest.version, "0.2.0");
});

test("offers a persistent editor window", () => {
  assert.match(popup, /id="open-profile-window"/);
  assert.match(script, /chrome\.windows\.create/);
  assert.match(script, /standalone=1/);
});

test("automatically saves profile edits", () => {
  assert.match(script, /form\.addEventListener\("input"/);
  assert.match(script, /chrome\.storage\.local\.set/);
});
