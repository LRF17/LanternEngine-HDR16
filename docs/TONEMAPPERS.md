# Native+ tone mappers: audit (0.9.38.2 beta 2)

Why lanterns and flames are brighter with Vanilla+ than with PsychoV-30 at the same settings, what
in that comes from the curves and what from their integration, what was corrected, and what was
tried and not kept. The code audited is the one the workflow builds: Lantern 0.9.38 (`4715bca`)
with `ports/lantern/nativeplus-engine.patch`; the references are RenoDX `b6b32f4` (`test30.hlsl`,
`test17.hlsl`, `DICE.hlsl`, the Cyberpunk 2077, Order of the Sinking Star, Starfield and
FromSoftware Engine mods, `.agents/skills/handle-sdr-tonemap-lut`) and souperman9's
`renodx-bloodborne.addon64` (its shaders, decompiled; its Bloodborne branch is not public).

Each point is marked **[contract]** (required by the tone mapper's own code or comments),
**[RenoDX]** (what RenoDX's mods do), **[deduction]** (this audit's reasoning or model) or
**[to measure]** (needs a capture in the game).

## The chain

Both tone mappers run in Native+'s replacement of the game's final composite
(`bb_composite_hdr.frag`), on the game's own inputs:

1. **Scene**: the game's HDR scene (RGBA16F, before its tone curve) times its tint, gain and
   vignettes: `x`, linear BT.709, exactly as the game computes it (`bb_composite.glsl`, written
   from the game's shader code for all 1380 variants of its composite).
2. **Tone mapper** on `x`, in place of the game's curve, to the display's peak in units of the
   game's white (peak / Game Brightness).
3. **Bloom** `g` (the game's bloom texture, B10G11R11 float, with its tint).
4. **Color matrix** (the game's 3x4 matrix, rows 840..851; desaturation that varies by place).
5. The result encoded as the game encodes (its gamma), written as the difference with the game's
   own output into the composite's RGBA16F target, so the target holds the HDR color plus the
   game's grain.
6. **Color table** (`bb_color_grading.frag`): the game's 16^3 table, exactly as the game applies
   it up to white; above white the color divided by its largest channel, graded, scaled back; a
   color outside BT.709 through RenoDX's gamut bridge.
7. Copies, the game's DLAA, the upscaler: all in 16-bit (RGBA16F) in Native+.
8. **Final pass** (`hdr_output.frag`): decode (pure 2.2), BT.709 to BT.2020, what is still below
   0 dropped, times Game Brightness, each channel clipped at the peak, PQ. The HUD is told apart
   by luminance against a copy taken before the game draws it.

## Why Vanilla+ is brighter

Measured on the model of the chain (grey, interiors: curve k 2.30, c 0.46; peak 1000 nits, Game
Brightness 203; PsychoV-30 with RenoDX's own code):

| Scene x | Game (SDR) | Vanilla+ | PsychoV-30 |
|---:|---:|---:|---:|
| 0.01 | 1.4 nits | 1.4 | 1.0 |
| 0.18 | 33 | 33 | 33 |
| 0.5 | 101 | 142 | 106 |
| 1 | 166 | 439 | 215 |
| 2 | 199 | 819 | 388 |
| 4 | 203 | 965 | 595 |
| 16 | 203 | 999 | 887 |

1. **The curves themselves (most of the difference).** **[deduction]**, measured above.
   - Vanilla+ continues the game's curve in a straight line from a *scene* value of 0.18 (where
     the game's curve gives about 0.17), with the game's slope there, and only then rolls off to
     the peak (`CInfinityRollOff`, anchor 0.18, strength 1.5). The line grows with the scene's
     light: the scene's range from 0.5 to 2 (lanterns, flames, lit walls) is already 1.4 to 4 times
     the game's, and reaches 80 % of a 1000-nit peak at x = 2. Confirmed in souperman9's addon: the
     tangent at x = 0.18, `+ bloom`, no clamp **[contract: Vanilla+'s reference]**.
   - PsychoV-30 anchors where the game's curve gives mid grey (0.18 out), with the game's log-log
     slope there, then follows a perceptual (Naka-Rushton-like) response that tends to the peak
     only as the light grows without bound: half the peak around x = 3, 90 % near x = 16
     **[contract: test30's F(x)]**. It stays close to the game's own image through the mid tones
     (106 nits against 101 at x = 0.5), RenoDX's neutral-by-default rule
     **[RenoDX: handle-sdr-tonemap-lut]**. Below mid grey it follows its own shape, not the game's
     toe: the deepest shadows are darker (1.0 against 1.4 nits at x = 0.01; with Vanilla+,
     Shadows at 45 gives PsychoV-30's shadows within 6 %).
   - So at the same settings PsychoV-30 is not "dimmer by mistake": its shoulder starts where the
     game's does, Vanilla+'s does not. Raising PsychoV-30's exposure would brighten everything,
     mid tones included, and was not done.

2. **The bloom (a large part around lights).** **[deduction]**, model:
   - Vanilla+ adds the bloom `g` unbounded to the light before its roll-off (souperman9's addon:
     `_263 + _270`). A halo of g = 1.2 over a dark wall (x = 0.5): 353 nits.
   - PsychoV-30 adds the game's own screen blend, clamped, on the part below white:
     `t + clamp(g) (1 - min(t, 1))`. The same halo: 203 nits, the game's white, exactly as the game
     shows it; on a light already brighter than white, nothing. This is the game's operator (the
     game clamps the bloom to 1 and screen-blends it), kept where the image is within SDR.
   - It was not changed: no reference requires more (the game's own bloom is clamped to white),
     and the only reason would be more nits. Whether the game's bloom texture goes much above 1
     around lanterns is **[to measure]** (procedure below).

3. **The purity coupling (colors only, no brightness).** **[contract]**, corrected (below).

4. **Not a cause.** The color table bridge returns the color unchanged with an identity table
   (largest relative change 4e-16 on a grey ramp up to 6x white), the 16-bit chain keeps values
   above white through every pass, and the final pass only encodes. PsychoV-30's peak and anchors
   are the same as Vanilla+'s. The final clip at the peak does not touch PsychoV-30's output
   (inside the BT.2020 cube and under the peak by construction, 0 of 791 test colors above it).

### Detail and color near the peak

Nits gained per doubling of the scene's light (the gradation left in the brightest areas: the
moon, a fire's core), and a flame's saturation (orange (1, 0.45, 0.08), BT.2020 `1 - min/max`):

| | Vanilla+ | PsychoV-30 | PsychoV-30, Highlights 60 | PsychoV-30, Highlights 70 |
|---|---:|---:|---:|---:|
| x 4 -> 8 | +29 nits | +178 | +140 | +90 |
| x 8 -> 16 | +5 | +115 | +65 | +32 |
| grey at x = 1 / 2 / 4 | 439 / 819 / 965 | 215 / 388 / 595 | 290 / 527 / 753 | 377 / 662 / 864 |
| flame saturation at x = 5 / 20 | 0.80 / 0.25 | 0.78 / 0.50 | 0.70 / 0.29 | 0.59 / 0.13 |

Near the peak, brightness and color cannot both be kept: an orange at 1000 nits of luminance would
need a red channel far above what the display shows **[deduction]**. Vanilla+ reaches the peak
early and turns the brightest lights white; PsychoV-30 keeps gradation and color for fewer nits.
PsychoV-30's Highlights slider (RenoDX's highlight grading on physiological Yf, mid grey and
shadows unchanged) moves between the two while keeping 3 to 6 times Vanilla+'s detail near the
peak: the user control for brighter PsychoV-30 highlights, neutral at 50.

## Corrected

- **PsychoV-30: the game's slope passed as `cone_response_exponent`.** test30 takes its cone power
  as `contrast * cone_response_exponent` but its purity as `purity_scale / contrast`
  **[contract]**. Native+ passed the game's slope (1.05 to 1.17 in the scenes measured) as
  `contrast`, so it also took purity down by that much at neutral settings. RenoDX's mods pass a
  vanilla slope as `cone_response_exponent` (Cyberpunk 2077: `psychovConeResponse`; Order of the
  Sinking Star: `SinkingStarResolvePsychoVConeResponse`) **[RenoDX]**. Now `contrast` is the
  menu's Contrast (1 neutral) and the game's slope is `cone_response_exponent`. Measured on
  RenoDX's own code: the luminance is unchanged (identical grey ramp; flame orange 115 nits at
  x = 1 both ways), the colors are about 10 % more saturated (flame orange 0.787 to 0.870, blood
  red 0.871 to 0.927, moon blue 0.603 to 0.648).

Checked and kept:

- Anchor and slope: `V(grey_in) = 0.18` and the game's `x V'(x) / V(x)` there, the skill's
  output-midgray anchor and cone formula **[RenoDX]**; measured on the output: V = 0.18000, slope
  1.1657 for the game's 1.1656 (interiors), 1.0461 for 1.0459 (outdoors).
- Compression `h = 1`: test30's default and Order of the Sinking Star's **[RenoDX]** (Cyberpunk
  2077 uses the automatic h, 1.29 here: +11 % at x = 4). Not changed.
- BT.2020 target, full gamut compression, BT.709 source boundary: test30's defaults and the HDR
  mods' **[RenoDX]**. Negative BT.709 channels kept signed to the final pass, which converts to
  BT.2020 before dropping what is still negative.
- Gamma: the chain encodes with the game's gamma and decodes with 2.2, as RenoDX's Gamma
  Correction 2.2; the peak needs no pre-correction (RenoDX's mods correct it only because their
  output pass converts sRGB to 2.2) **[deduction]**.

## Vanilla+ against souperman9's addon

Kept as it is (the default, validated by players), but noted **[contract: the addon]**:

- the addon rolls off **after** the color table (in its LUT pass); Native+ before it (in the
  composite);
- its color table bridge compresses the max channel with `CInfinityRollOff` before the table and
  expands it after, in the encoded domain; Native+'s is Exact up to white;
- it decodes with the sRGB curve or 2.2 (its Gamma Correction setting); Native+ with 2.2.

These change saturated highlights through a strong table, not the brightness gap above
**[to measure]**.

## Tried and not kept

- **PsychoV-17** (RenoDX's `psychotm_test17`, ported and checked against RenoDX's HLSL within
  7e-6, set as RenoDX's Starfield mod sets it): on greys it gives PsychoV-30's curve exactly (the
  same Naka-Rushton response with these anchors), and its colors differ only in the brightest
  saturated lights (a little paler). Seen the same as PsychoV-30 in the game: removed before
  release.
- **DICE** (RenoDX `DICE.hlsl`) in place of Vanilla+'s roll-off: about as bright as Vanilla+,
  flat at the peak from x = 4 (no gradation above), saturated colors kept but their channels 2 to
  3 times the peak (clipped by the final pass).
- **The FromSoftware Engine mod's PsychoV** (Ritsu; Elden Ring, Nightreign, Sekiro, Armored Core
  VI), its code compiled unchanged on Vanilla+'s extended curve: brighter than Vanilla+ up to
  x = 4 (927 against 819 nits at x = 2), flat at the peak above it, and the brightest lights whiter
  (flame saturation 0.49 at x = 5 against Vanilla+'s 0.80).
- **PsychoV-30 on Vanilla+'s highlights**, two ways: PsychoV-30 as the display mapping of
  Vanilla+'s extended curve (that mod's structure), or PsychoV-30 driven to give Vanilla+'s
  luminance. Both reach Vanilla+'s brightness with Vanilla+'s small detail near the peak (+44 and
  +29 nits from x = 4 to 8) and whiter colors than Vanilla+ (flame saturation 0.37 and 0.35 at
  x = 5).

None reaches the peak more often *and* keeps more detail or color than the two kept; reaching the
peak more often was not taken as better.

## Checks run

- Engine build, settings tests, the host shader configurations compiled and validated
  (`shader_check.py`).
- `engine/docs/hdr-tools/psychov_check/run.sh`: the GLSL PsychoV-30 against RenoDX's HLSL compiled
  unchanged, on 791 colors (grey ramp 1e-4..1e4, 18 hues at 40 levels, out-of-gamut, extremes):
  max difference 2e-4 of the color's largest channel over 9 configurations (before and after the
  correction, interiors and outdoors, sliders moved, BT.709 cube, automatic compression, peaks 400
  and 2991); no NaN or infinite value; the grey ramp monotonic and continuous.

**Not run:** the brightness and color differences above come from the model and RenoDX's code;
in the game, PsychoV-17 was compared with PsychoV-30 only by eye, and the correction and the
Highlights slider have not been measured on the screen.

## Capture procedure

Same save, same place, same camera, the game's Brightness at 5, the same Native+ settings except
the tone mapper; no upscaler first, then the one you use.

1. Places: a lantern in a dark street (Central Yharnam), a fire, the moon (Hunter's Dream /
   Cathedral Ward), a lit interior.
2. For Vanilla+, PsychoV-30, and PsychoV-30 with Highlights 70, Bloom 50 then 0:
   - an HDR screenshot (Xbox Game Bar, Win+Alt+PrtScn: a JXR) for nits; read the luminance and the
     largest channel separately (they differ for colors: a red at 1000 nits in its red channel is
     about 260 nits of luminance);
   - Test probe 1 (the composite's HDR part), 2 (the final image above white), 6 (colors outside
     BT.709): a normal screenshot each.
3. One frame with RenderDoc (Vulkan) per tone mapper, for the values before and after each stage:
   the composite draw (`bb_composite_hdr`: its scene input `x` and bloom input `g` texels on the
   lantern, its RGBA16F target), the color table draw (input / output), the final pass (PQ
   output). Note the composite's constants 832, 833 (curve) and 840..851 (matrix) for that place.
4. Log the HDR chain once (Debug) in each place, and send `logs/last_session.log`.
