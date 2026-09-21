# Blend Style Database V3 — twenty group shapes on the seven vibe axes

**Supersedes `BLEND_STYLE_DATABASE_V2.md`** (2026-09-17). A blend style is still the room's
identity — a name, a colour, a vector — but the vector is now on the **seven vibe factors only**,
so a style is a *shape of an evening for a group*, and every one of them is a kind of night people
recognise. Preferences never enter the style; they decide venues, not identity.

**Authored, not clustered.** V2's 24 styles were k-medians centres over 30,000 simulated rooms on
ten factors. Those vectors do not translate to the split scale. These twenty are written from the
shape library (`FACTORS_V5.md` §5) and the group types the chemistry work named; **re-derive
them by clustering real rooms as soon as there are a few hundred** — the method in V2 §2 still
applies, on seven axes.

The room vector is built as before: abstention over members (each member weighted by firmness
per factor), then the room-level payback of `OUTING_PLAN_ENGINE.md` §13.6.1, on vibe factors.
Nearest style by L1; `similarity = max(0, 1 − L1 / 350)` (seven axes, an average gap of 50 per
axis is total dissimilarity).

---

## 1. The twenty

| Style | `ENRG` | `AFFIL` | `CROWD` | `TALK` | `ROAM` | `MOVE` | `GAMES` | The group, in a line |
|---|---|---|---|---|---|---|---|---|
| **The Whole Team Out** | 80 | 85 | 70 | 40 | 60 | 60 | 75 | our people, building, something to do at every stop |
| **The Catch-Up** | 30 | 90 | 30 | 90 | 10 | 10 | 20 | one table, hours, nowhere to be |
| **The Send-Off** | 88 | 35 | 85 | 15 | 75 | 80 | 40 | loud, everyone, anything, three places |
| **Out to Be Seen** | 70 | 20 | 90 | 30 | 45 | 55 | 10 | the room, packed, facing out |
| **The Long Table** | 40 | 88 | 45 | 80 | 5 | 10 | 30 | one place, no next stop, our table |
| **Chase the Night** | 90 | 45 | 80 | 15 | 95 | 70 | 25 | wherever is open, whatever is next |
| **Down the Front** | 75 | 40 | 75 | 10 | 40 | 60 | 10 | the noise is the point; the act is a preference on top |
| **Big Room, Loud Night** | 85 | 40 | 92 | 12 | 40 | 75 | 10 | the fullest floor, all night |
| **Game Night** | 60 | 75 | 55 | 50 | 30 | 30 | 92 | something to play, our people, one place |
| **The Easy Good One** | 55 | 65 | 60 | 60 | 45 | 35 | 40 | no agenda, no theme, just out |
| **Small and Perfect** | 25 | 85 | 15 | 90 | 15 | 10 | 15 | two or three people, low light, nothing rushed |
| **Slow and Steady** | 35 | 70 | 40 | 75 | 25 | 15 | 30 | calm, sat down, a couple of places at most |
| **The Wander** | 45 | 65 | 50 | 70 | 90 | 55 | 20 | keep moving, but talking — streets, courtyards, doors |
| **Floor First** | 85 | 50 | 80 | 15 | 35 | 95 | 10 | on your feet from the first stop |
| **Meet the Room** | 60 | 10 | 75 | 55 | 50 | 40 | 35 | out to meet people — where public rooms live |
| **Table Then Floor** | 70 | 70 | 70 | 45 | 60 | 65 | 25 | dinner-quiet first, then it builds — the classic two-stop |
| **The Quiet Crowd** | 40 | 60 | 85 | 60 | 40 | 20 | 20 | somewhere packed but sat — a market, a street, a mela |
| **Open Air** | 50 | 70 | 45 | 70 | 40 | 65 | 45 | a lawn, a terrace, moving about, talking |
| **The Regulars** | 45 | 80 | 50 | 65 | 10 | 20 | 55 | the usual place, the usual people, a game on |
| **Anything Goes** | 65 | 55 | 65 | 40 | 70 | 60 | 55 | a room with no strong pole — the median night |

Twenty. Every axis is represented at both extremes; *Anything Goes* is the centre, where rooms
land when nobody is firm on much (and it is the style that `DRIFT` rooms take once they stop
drifting).

---

## 2. Palettes

Hue by rule from the signature — heat from `ENRG`, depth from `AFFIL` (inward = deeper), light
from `TALK` (conversation = warmer, lighter), electric from `MOVE`, green from `ROAM`. Base is the
room background, deep the text on it. Authored; check against the app's theme.

| Style | Base | Deep |
|---|---|---|
| The Whole Team Out | `#E4572E` | `#2A1A12` |
| The Catch-Up | `#8A6A3C` | `#1B140A` |
| The Send-Off | `#E02F4A` | `#210A0F` |
| Out to Be Seen | `#7A2E8C` | `#170D1A` |
| The Long Table | `#9A7040` | `#1E1508` |
| Chase the Night | `#D93B5A` | `#220A10` |
| Down the Front | `#5B3FD9` | `#0F0C1F` |
| Big Room, Loud Night | `#B02E5A` | `#1E1016` |
| Game Night | `#D98A2B` | `#241708` |
| The Easy Good One | `#3F7A8C` | `#0D1A1E` |
| Small and Perfect | `#6B4A7A` | `#150E19` |
| Slow and Steady | `#5E6B4A` | `#111408` |
| The Wander | `#3F8C6B` | `#0C1A14` |
| Floor First | `#C7305F` | `#200A12` |
| Meet the Room | `#2F7FA6` | `#0A1620` |
| Table Then Floor | `#C06A4A` | `#22110C` |
| The Quiet Crowd | `#A6772E` | `#1F1708` |
| Open Air | `#5E8C4A` | `#101A0C` |
| The Regulars | `#7A6A55` | `#171310` |
| Anything Goes | `#6E7B8B` | `#12161B` |

---

## 3. The chip

Next to the style name, the chemistry word — a psychology tag from `CHEMISTRY_V2.md` if one fires
(*Caught the Spark · Running Hot · Slow Burn · Could Go Late · Our Table · Meet the Room · Table and
Floor · Packed but Ours · Buzz, Not Noise · Common Ground · On Our Feet · Settle Then Roam*), else
the formation word (*In Sync · Got Your Back · Best of Both · Along for the Ride · Something for
Everyone · Open Night*). *The Whole Team Out · In Sync*. The chip freezes with the
plan at hosting; the style keeps recomputing by abstention as people join.

---

## 4. What changed from V2, and why

- **Ten axes → seven.** Styles that were really about a preference — *The Proper Dinner*,
  *Supper and a Set*, *The Old City Wander*, *Purani Dilli Run*, *Dressed and Seen* — are gone
  as styles. The rooms they described still exist; they are a shape (*The Long Table*, *Down the
  Front*, *The Wander*, *The Quiet Crowd*, *Out to Be Seen*) with preference badges on the members.
- **Four new axes** give four new kinds of room that had no name: *The Wander* (`ROAM` high,
  `TALK` high), *Floor First* (`MOVE`), *Meet the Room* (`AFFIL` low as a want), *The Quiet
  Crowd* (`CROWD` high, `ENRG` low).
- **The similarity denominator** is 350, not 500, for seven axes.
- **Authored, not clustered** — see the top. The first few hundred real rooms replace this list.

## 5. Open

- Whether twenty is the right number on seven axes; the clustering decides.
- Whether *Anything Goes* should be shown as a style at all, or the room should read as *Open
  Night* until it leans somewhere.
- Palettes and names untested, as in V2.
