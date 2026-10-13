import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const source = await readFile(new URL("../matcher.js", import.meta.url), "utf8");
const context = vm.createContext({});
vm.runInContext(source, context);
const { matchField } = context.JobAutofillMatcher;

const cases = [
  ["First Name", "", "text", "firstName"],
  ["last_name", "", "text", "lastName"],
  ["Email Address", "", "email", "email"],
  ["Phone Number", "", "tel", "phone"],
  ["LinkedIn Profile URL", "", "url", "linkedin"],
  ["GitHub URL", "", "url", "github"],
  ["Personal Website", "", "url", "website"],
  ["Legal name", "name", "text", "fullName"],
  ["Full Legal Name", "", "text", "fullName"],
  ["City", "address-level2", "text", "city"],
  ["Your Location", "", "text", "location"],
];

for (const [descriptor, autocomplete, inputType, expected] of cases) {
  test(`matches ${descriptor} as ${expected}`, () => {
    assert.equal(matchField({ descriptor, autocomplete, inputType }), expected);
  });
}

test("does not treat preferred first name as legal first name", () => {
  assert.equal(matchField({ descriptor: "Preferred First Name", inputType: "text" }), null);
});

test("does not treat company website as a personal website", () => {
  assert.equal(matchField({ descriptor: "Company website", inputType: "url" }), null);
});

test("does not fill the native-language legal name", () => {
  assert.equal(matchField({ descriptor: "Full Legal Name in Native Language", inputType: "text" }), null);
});
