# Tariff stance classifier rubric — v3 (= v2 + MTB/GSP clarification)

You label U.S. federal lobbying activity descriptions by what the client is
asking for **with respect to tariffs**. Apply this rubric exactly. Classify only
what the **text** states — never infer a position from who the client is.

## Central rule — classify the DIRECTION OF THE ASK, not the instrument

Section 232, Section 301, IEEPA, antidumping/countervailing duties (AD/CVD),
de minimis, USMCA are all **direction-neutral**. The same instrument appears on
both sides:
- a Section 301 **exclusion**, or **extension of tariff exclusions** = relief
  (getting *out* from under a tariff)
- a petition *for* antidumping/countervailing duties = protection (putting a
  barrier *up*)

Read carefully: *"extension of tariff exclusions"* is **relief**, not an
extension of tariffs.

**Two instruments ARE directional.** The Miscellaneous Tariff Bill (MTB) and the
Generalized System of Preferences (GSP) are duty-**relief** programs by design.
*Supporting / renewing / extending* MTB or GSP → `relief`. But a **bare mention**
of MTB/GSP as a topic, with no support/oppose verb, is still `unclear` (you don't
know whether they back it).

## Decision order (top-down, first match wins)

1. Is there a **concrete** directional ask on tariffs?
   - reduce / remove / avoid / delay / suspend / be-exempted-from / get-an-
     exclusion-from a tariff or duty burden on the client, its inputs, or its
     products — or (foreign actor) remove a U.S. tariff on their goods / avoid
     retaliation → **`relief`**
   - impose / raise / maintain / expand / strengthen-enforcement-of tariffs or
     import barriers on imports or competitors, to the client's own benefit →
     **`protection`**
   - the description contains concrete asks in **both** directions → **`mixed`**
2. No concrete ask, **but** the text uses an explicit passive **watching verb**
   about tariffs (monitor / track / follow / report on / stay apprised of /
   assess developments) and nothing more → **`monitoring`**
3. Otherwise → **`unclear`**

## Rules (these are where v1 went wrong — apply them strictly)

- **Concrete asks only.** Aspirational or rhetorical framing is **not** a
  directional ask. "Supports the Administration's goal of promoting American
  manufacturing" *while every concrete request is for exclusions/reductions* →
  `relief`, **not** `mixed`. Reserve `mixed` for genuinely competing **concrete**
  requests (e.g. "supports suspending the duty on our imported inputs **and**
  supports new tariffs on competing finished goods").
- **`monitoring` requires an explicit watching verb.** A line that only *names* a
  tariff, instrument, or bill with no verb is **`unclear`**, not `monitoring`
  (e.g. a bare "Section 232 steel and aluminum tariffs"). "**Impact of** [a
  tariff] on [a country]" is a topic, not a watching verb → `unclear`.
- **Ask beats posture.** "Monitor **and advocate for** an exclusion" → `relief`.
  But "monitor and **engage on** tariff policy" with no stated direction →
  `unclear` (active engagement without a direction is not monitoring, and not an
  ask).
- **"Restore / return tariffs to an earlier (pre-increase) baseline"** = `relief`
  (rolling the tariff back down). If such wording is self-contradictory on its
  face, mark it `unclear` or low confidence rather than guessing.
- **Multi-issue / numbered descriptions:** read each clause; find the operative
  **verb** on each tariff item before labeling (don't be misled by an instrument
  name). Classify on the tariff-relevant asks only; if the tariff clause has no
  direction → `unclear`; if asks genuinely conflict → `mixed`.

## Confidence

`confidence` ∈ [0,1] = how strongly the **text** supports the label:
- explicit directional verb present → high (0.85–1.0)
- direction implied but not stated → low (0.3–0.6)
- genuinely ambiguous / self-contradictory → ~0.3

## Output

One object per input item: `{"id": int, "label": one of
relief|protection|monitoring|mixed|unclear, "confidence": float,
"rationale": "<=15 words quoting the operative phrase"}`.
