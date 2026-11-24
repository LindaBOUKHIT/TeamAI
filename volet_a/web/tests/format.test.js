import test from "node:test";
import assert from "node:assert/strict";
import { formatDecimal, formatInteger, plural } from "../src/ui/format.js";

const clean = (text) => text.replace(/\s/g, " ");

test("format : deux décimales avec la virgule française", () => {
    assert.equal(formatDecimal(0.40814146399497986), "0,41");
    assert.equal(formatDecimal(0.00010458), "0,00");
    assert.equal(formatDecimal(386.4), "386,40");
    assert.equal(clean(formatDecimal(1234.5)), "1 234,50");
});

test("format : entiers et accords au singulier pour 0 et 1", () => {
    assert.equal(clean(formatInteger(86260)), "86 260");
    assert.equal(plural(0, "bloc"), "0 bloc");
    assert.equal(plural(1, "bloc suspect", "blocs suspects"), "1 bloc suspect");
    assert.equal(plural(3, "bloc suspect", "blocs suspects"), "3 blocs suspects");
});
