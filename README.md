# Lantern Engine Native+ HDR (experimental)

HDR for Bloodborne on [Lantern Engine](https://github.com/Awakenchan/LanternEngine) by Awaken.
**Native+** keeps the light of the game's scene all the way to the screen and tone maps it to
your display's peak, with an in-game menu laid out like a RenoDX mod. Two tone mappers:

- **Vanilla+** (default), by **souperman9**, from his RenoDX Bloodborne mod: the game's own image,
  with brighter highlights up to your display's peak.
- **PsychoV**: RenoDX's PsychoV-30 with Vanilla+'s highlights, bloom and hues: deeper blacks and
  more detail near the peak.

Native+ works with Lantern's upscalers and with frame generation (DLSS and FSR 3.1). Lantern's
own README and credits are in [README-Lantern.md](README-Lantern.md).

> **Unofficial, AI-assisted.** This is not a RenoDX mod and is not affiliated with or endorsed by
> RenoDX or its authors. It reuses RenoDX's MIT-licensed code (PsychoV-30, its grading, hue
> correction, roll-off and gamut bridge) and souperman9's Vanilla+, but the HDR integration
> (where the scene is captured, the game's color table, the output) is this port's own and does not follow
> RenoDX's mod guidelines. It was written largely with an AI coding assistant (Claude) and is
> tested by a few players. Please do not report its issues to RenoDX or to souperman9. For RenoDX
> itself, see [clshortfuse/renodx](https://github.com/clshortfuse/renodx).

## Contents

- [Install](#install)
- [Quick start](#quick-start)
- [Settings](#settings)
- [Tone mappers](#tone-mappers)
- [Upscalers and frame generation](#upscalers-and-frame-generation)
- [Troubleshooting and known issues](#troubleshooting-and-known-issues)
- [Versions and updates](#versions-and-updates)
- [How it works](#how-it-works)
- [Build from source](#build-from-source)
- [Credits and licenses](#credits-and-licenses)

## Install

1. Download the package (`LanternEngine-NativePlusHDR-v<version>-win64.zip`) from this fork's
   [Releases](https://github.com/LRF17/LanternEngine-NativePlusHDR/releases) and extract it into a
   **new, empty folder**. It is a complete package: do not merge it into another Lantern release.
2. Start **Lantern Engine.exe** (or `Bloodborne.exe`, its shortcut). The window title is
   **Lantern Engine Native+ HDR**. Select your game dump (the folder with `eboot.bin`); game data
   is not included.
3. Your saves stay in your old installation: select your existing user folder in the launcher's
   profile settings, or copy the saves with the game closed (keep a backup). Do not copy an old
   engine, executables or a complete settings file into this package.

Where things are:

- The game's settings: `lantern.ini`, next to `Lantern Engine.exe`. Every setting of the in-game
  menu is saved there.
- The launcher's settings: `%APPDATA%\bbport-launcher-psychov30` (its name from before the
  rename, kept so that nobody loses their settings).
- The log of the last session: `logs/last_session.log`.

## Quick start

1. Turn on HDR in Windows: *Settings > System > Display > Use HDR*. Running the Windows **HDR
   Calibration** app once gives the game your display's real peak.
2. In the launcher's **Display** page, turn on **HDR output**. The **HDR source** is
   **Native+** by default in a new installation. Entering or leaving Native+ needs a game restart.
3. Start the game and keep its own **Brightness** option (in the game's settings) at **5**.
4. Open the in-game menu with **Insert** (or L3+R3). The HDR section's first line should say
   **Native+: active**. Every setting there applies live.

A good starting point: Preset #1, Vanilla+, Peak Brightness from your display, Game Brightness and
UI Brightness at 203 nits, everything else at its default.

## Settings

### In-game menu

The menu opens with **Insert** (or L3+R3). Every setting applies live and is saved in
`lantern.ini`. Each preset keeps its own settings, except Preset and Settings Mode themselves.
Settings marked *Intermediate* or *Advanced* are shown from that Settings Mode on.

| Setting | Values (default) | What it does |
|---|---|---|
| Preset | Off, #1 to #3 (#1) | Off is the game's own look in HDR10, without HDR highlights. Each numbered preset keeps its own settings. |
| Settings Mode | Simple, Intermediate, Advanced (Simple) | How many settings the menu shows. |
| **Tone Mapping** | | |
| Tone Mapper | Vanilla+, PsychoV (Vanilla+) | See [Tone mappers](#tone-mappers). |
| Peak Brightness | 400 to 4000 nits (your display's) | The brightest your display can show: the value Windows reports while not set by hand, 1000 if Windows reports none. The reset button goes back to the display's. |
| Game Brightness | 80 to 500 nits (203) | The brightness of the game's white (the launcher's Paper white). |
| UI Brightness | 48 to 500 nits (203) | The HUD and menus' white, whatever Game Brightness. |
| **Color Grading** | | |
| Exposure, Highlights, Shadows, Contrast, Saturation | 1.00, 50, 50, 50, 50 | Vanilla+: RenoDX's grading. PsychoV: PsychoV-30's own parameters. Neutral at these values. |
| Color Grade Strength *(Intermediate)* | 0 to 100 % (100) | The game's own color grading: 100 is the game's look, 0 the image before it. |
| Black Floor *(Intermediate)* | 0 to 2 nits (0) | Takes the game's darkest greys down to true black (OLED). |
| **Effects** | | |
| Bloom | 0 to 100 (50) | The glow around lights: 50 is the game's, 0 removes it. |
| Reset all | | Every setting of the preset back to its default. |
| **Debug** *(Advanced)* | | |
| Compare | HDR, SDR | The game's own SDR picture, to compare; **F9** switches it with the menu closed. Not saved. |
| Test probe | Off, 1 to 7 | Shows where the HDR chain works (7: the pixels taken as the HUD, in red). Not saved. |
| Log the HDR chain | | Writes one frame's HDR trace to the log. |

### Launcher

The launcher's **Display** page has HDR output, HDR source (Native+, Native, Expanded), Paper
white, Peak brightness from the display, Peak brightness, UI brightness and Tone mapper, with the
same defaults as the in-game menu. A new installation starts on Native+ (its shipped
`lantern.default.ini`, copied to `lantern.ini` once); HDR output stays off until you turn it on.
Native and Expanded are Lantern's own HDR modes; their
Highlight boost is hidden with Native+.

In Native+, the game's own Brightness, Contrast, Saturation and Bloom in the port's Picture
section (and the game's PC Colour menu) are left as the game draws them: the HDR settings above
replace them.

## Tone mappers

- **Vanilla+** (default), by **souperman9**, from his RenoDX Bloodborne mod: the game's own curve
  up to a scene value of 0.18, continued in a straight line above it, the bloom added, then rolled
  off smoothly to your display's peak (RenoDX's `CInfinityRollOff`). The game's shadows, brighter
  mid-highlights than the game's and the brightest highlights; the very brightest lights turn
  white.
- **PsychoV**: RenoDX's PsychoV-30 used as the FromSoftware Engine RenoDX mod uses its tone
  mapper, on a game curve continued above mid grey. Below mid grey, PsychoV-30's own shadows
  (anchored where the game's curve gives mid grey, with the game's contrast there). Above it,
  Vanilla+'s curve, its bloom (added before the game's color matrix) and its hues (RenoDX's hue
  correction), compressed to your display's peak by PsychoV-30. Every color stays within BT.2020
  and under the peak.

Against Vanilla+, PsychoV gives deeper blacks in most places, the same brightness for the
brightest lights (the sun reaches the peak), mid-bright sources such as the moon and lamps about
10 % lower, more gradation near the peak, and the same hues with softer colors near the peak (its
**Saturation** raises them). How each step was chosen and measured, in the game and on RenoDX's
own code: [docs/TONEMAPPERS.md](docs/TONEMAPPERS.md).

Preset **Off** shows the game's own SDR look in HDR10, as a reference.

## Upscalers and frame generation

- **Upscalers**: Lantern's upscalers work in Native+. The scene is upscaled in 16-bit, so its
  highlights survive the upscale.
- **Frame generation**: DLSS (NVIDIA RTX 40/50) and FSR 3.1 (any GPU) work in Native+ and
  interpolate its HDR frames as they are.
- With **FSR 3.1** frame generation, the HUD of the generated frames is shown at Game Brightness:
  keep **UI Brightness** at the same value as **Game Brightness** (both 203 nits by default), or
  the HUD flickers.
- Native+ uses Lantern's native shader compiler, its shader catalog and the same shader cache as
  the other modes: switching the HDR source does not rebuild the shaders.

## Troubleshooting and known issues

- **The menu says "Native+: not active here (shown in SDR)"**: check that HDR is on in Windows and
  in the launcher, and that the HDR source is Native+. If it stays in SDR, please open an
  [issue](https://github.com/LRF17/LanternEngine-NativePlusHDR/issues) with
  `logs/last_session.log`.
- **GPUs**: tested on NVIDIA and AMD (an RX 6800 XT). Intel GPUs should work but have not been
  tested. Native+ needs 176 bytes of Vulkan push constants (checked at startup).
- **The image looks washed out or too dark**: keep the game's own Brightness option at 5. It
  still changes the whole image, shadows first.
- **Known: the HUD over very bright areas** (the sun, a lamp) is brighter than UI Brightness. The
  HUD is told apart from the scene by comparing it with a copy taken just before it, and over
  highlights the two blend. RenoDX's mods show the same.
- **Known: a thin light line** on the right and bottom edges was reported on AMD with an upscaler.
  It is being looked into: a log and a screenshot help.

## Versions and updates

- Versions follow Lantern's: **0.9.38.1** is this fork's first release on Lantern 0.9.38,
  **0.9.38.2** the next one. Betas (`0.9.38.2-beta.1`) come from the `lantern-Native+HDR-beta`
  branch, releases from `lantern-Native+HDR`.
- The launcher updates itself from this fork's releases.
- **Updating from an earlier version**: your settings are kept. Settings that no longer exist
  (Target gamut, Gamut Compression, Compression, Color Table Bridge) are ignored, PsychoV-30
  reads as PsychoV (which replaced it), the old tone mappers (Vanilla, Hybrid, Neutwo) read as
  Vanilla+, and `hdr_mode=psychov30` reads as `nativeplus`. A `bbport.ini` from before Lantern 0.9.37 is copied to `lantern.ini` once.

## How it works

- **16-bit chain.** The game draws its final image in 8 bits, clipped at white. Native+ replaces
  the game's final composite: the scene is tone mapped there (Vanilla+ or PsychoV), and every
  pass after it (the color table, the upscaler, the display copy) runs in 16-bit float, so the
  light above white reaches the screen. The final pass converts to HDR10 (or scRGB with FSR frame
  generation).
- **Gamma.** The chain decodes the game's image with a pure 2.2 power (no sRGB curve), as RenoDX's
  Gamma Correction 2.2: the shadows look as on an SDR TV, not grey.
- **Color table.** The game's color table only covers SDR colors. Native+ applies it exactly as
  the game does up to white. Above white, and for colors outside BT.709 (RenoDX's gamut bridge),
  the color is brought inside the table's range, graded, then taken back out, so highlights and
  saturated colors keep their hue and are graded too.
- **HUD.** The HUD is told apart from the scene by comparing the frame with a copy taken just
  before the game draws its HUD. It is shown at UI Brightness, the scene in HDR.

## Build from source

This fork carries reproducible patches over Lantern 0.9.38: `ports/lantern/nativeplus-engine.patch`
on Lantern's `engine/` and `nativeplus-launcher.patch` on its launcher (this fork's `launcher/`
already holds it). The GitHub workflow (`.github/workflows/lantern-nativeplus.yml`) copies the
pinned Lantern's `engine/`, applies the patches, builds the engine, its settings tests and the
launcher, checks the HDR shaders (against RenoDX's own code for the gamut bridge) and assembles
the package with the official 0.9.38 runtime files (DLLs, models, shader catalogs). Pinned inputs:

- LanternEngine `4715bca355059b7bd981ca849412884059d4d0a7` (0.9.38).
- RenoDX `b6b32f47789ff9d0e640a0e0db6c9421b5397f34` (shader checks, and the source of the GLSL
  PsychoV-30).

The GLSL PsychoV-30 is checked against RenoDX's HLSL, compiled unchanged, by
`engine/docs/hdr-tools/psychov_check/run.sh` (in the engine patch), on the CPU; the same script
models PsychoV with that original (`psychov_model.cpp`).

Native+'s replacements of the game's composite, color table and copies are built for each way the
game shader can be compiled: inputs read per vertex (fragment-shader barycentrics, the
recompiler's exact interpolation on NVIDIA) or as the GPU interpolates them (hardware
interpolation, AMD, Intel), and for the composite the constant buffer as a storage buffer (legacy
compiler) or a uniform buffer (native compiler). The engine picks one per game shader and says
which in the log. The shader cache holds the game's own shaders; Native+ swaps its replacements in
when they load, so all modes, Lantern's shader catalog and its cache recompiles
(`bb-shader-lab.exe`) share it. With `BB_UBO_DWORDS=0` or `BB_UBO_EXACT=1`, Native+ keeps the
legacy compiler.

## Credits and licenses

- **Lantern Engine** by Awaken, on DarkIzuku's bloodborne_pc; GPL-3.0-or-later. Keep the
  package's licenses when sharing it.
- **Native+ HDR** by LRF17.
- **Vanilla+** by **souperman9** (RenoDX Bloodborne mod).
- **RenoDX** by Carlos Lopez (ShortFuse) and contributors, MIT (`licenses/RenoDX-MIT.txt`):
  PsychoV-30, the user color grading, the hue correction, `CInfinityRollOff`, the gamut and LUT
  bridge, ported to GLSL.
- No game data is included.
