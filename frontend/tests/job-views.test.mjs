import assert from "node:assert/strict";
import test from "node:test";
import { matchesJobView } from "../app/tracking.ts";

const job = { additionGroup: "latest", availability: "active", personal: { stage: "pending" }, unread: [] };
test("addition queue is independent of read status and includes interested jobs", () => {
  assert.equal(matchesJobView(job, "latest"), true);
  assert.equal(matchesJobView({ ...job, personal: { stage: "interested" } }, "latest"), true);
  assert.equal(matchesJobView(job, "earlier"), false);
  assert.equal(matchesJobView({ ...job, additionGroup: "earlier" }, "earlier"), true);
  assert.equal(matchesJobView({ ...job, additionGroup: null }, "latest"), false);
});
test("applied, ignored and inactive jobs leave both addition queues", () => {
  for (const additionGroup of ["latest", "earlier"]) {
    for (const stage of ["applied", "ignored"]) {
      assert.equal(matchesJobView({ ...job, additionGroup, personal: { stage } }, additionGroup), false);
    }
    for (const availability of ["closed", "not_seen", "no_match"]) {
      assert.equal(matchesJobView({ ...job, additionGroup, availability }, additionGroup), false);
    }
    assert.equal(matchesJobView({ ...job, additionGroup, availability: "unverified" }, additionGroup), true);
  }
});
