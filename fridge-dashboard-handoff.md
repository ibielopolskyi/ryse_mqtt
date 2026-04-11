# Handoff: Fridge Dashboard + Fridge 3D Theme

## Mission

Ship the remaining 5% of a Home Assistant fridge-panel dashboard refresh: get
the pure-CSS "Fridge 3D" glassmorphism theme published in the
`ibielopolskyi/ha_fridge_theme` HACS repo, installed on HA via HACS, and
verified live on the fridge dashboard.

## Session scope required

When starting the new session, select BOTH repos in the repository picker:

- `ibielopolskyi/ryse_mqtt` (for history / reference, no changes needed)
- `ibielopolskyi/ha_fridge_theme` (where the theme must be pushed — currently
  empty, HACS is throwing 409 because of that)

If the picker only shows `ryse_mqtt`, go to:

    GitHub → Settings → Applications → Claude → Configure → Repository access

and add `ha_fridge_theme`, then start the session.

## HA credentials (reuse from previous session)

- Base URL: `https://rcnk01hkmjuexvkv6jnfmojs7f3mvwzd.ui.nabu.casa`
- Long-lived token:

      eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiNzRkNTE4YTY3ZDQ0Yjc4YmFiMjdkZGQwZjI1ZDM4OSIsImlhdCI6MTc3NTc4OTAwOCwiZXhwIjoyMDkxMTQ5MDA4fQ.-Epwej3HJoAauY34Tm5fpAlpqsWZfVxkXMmZDIWDwI4

- WebSocket: `wss://rcnk01hkmjuexvkv6jnfmojs7f3mvwzd.ui.nabu.casa/api/websocket`
  (auth with the token above, then send commands with an `id` field — reuse
  the minimal helper in the "Helper script" section).

## Current state (verified April 11, 2026)

**Live HA `dashboard-fridge` (saved via `lovelace/config/save`):**

- Panel view, title "Home", `theme: "Fridge 3D"` set on the view (inert until
  the theme YAML is deployed).
- Background: radial + linear gradient (preserved inline at view level).
- Layout: `horizontal-stack` root:
  - **Left column** (`vertical-stack`): two `conditional` `picture-entity`
    cameras (`camera.birdeye` when `binary_sensor.wantspreset == off`,
    `camera.front_2` when `== on`) → native `button` card "Check Packages" →
    `media-control` for `media_player.my_tv` → `todo-list` for
    `todo.shopping_list`.
  - **Right column** (`vertical-stack`): 10 horizontal `tile` cards with
    `color: amber`, in this order:
    1. `light.kitchen_lights` — Kitchen — `mdi:countertop`
    2. `light.bar_7` — Bar — `mdi:glass-cocktail`
    3. `switch.kitchen_kitchen_torch_switch` — Kitchen Torch — `mdi:torch`
    4. `switch.foyer_light` — Foyer — `mdi:door`
    5. `light.living_room_lights` — Living Room — `mdi:sofa`
    6. `switch.living_room_plug` — Side Lamp — `mdi:floor-lamp`
    7. `light.dining_room_lights` — Dining — `mdi:silverware-fork-knife`
    8. `light.cupboard` — Cupboard — `mdi:cupboard`
    9. `switch.balcony_lights` — Balcony — `mdi:balcony`
    10. `switch.balcony_plug` — Xmas Lights — `mdi:string-lights`
- Zero `custom:*` cards, zero `card_mod`. Total config ~3 KB (down from the
  original 27 KB `custom:button-card`-heavy version that was crashing the
  low-resource fridge display).

**Git state of `ibielopolskyi/ryse_mqtt`:**

- `main` is clean: `f31f5cb Revert fridge dashboard reference and theme from
  ryse_mqtt`.
- Previous feature branch `claude/fridge-dashboard-camera-fix-JJZxB` can be
  ignored/deleted.
- No fridge artifacts remain in this repo (user explicitly did not want it
  polluted).

**`ibielopolskyi/ha_fridge_theme`:**

- Repo exists, main branch is empty → HACS 409.
- Needs one commit: `themes/fridge-3d/fridge-3d.yaml` (+ optional README at
  root).

## Your one concrete task

In the new session (with `ha_fridge_theme` now in scope), run **one**
`mcp__github__push_files` call:

    owner:   ibielopolskyi
    repo:    ha_fridge_theme
    branch:  main
    message: Add Fridge 3D theme — pure CSS glassmorphism for low-resource HA displays

with these two files (inlined below).

### File 1 — `themes/fridge-3d/fridge-3d.yaml`

```yaml
##
## Fridge 3D — pure-CSS glassmorphism theme for Home Assistant.
##
## Install via HACS:
##   1. HACS > Frontend > three-dots menu > Custom repositories
##   2. Repository: ibielopolskyi/ha_fridge_theme, Category: Theme
##   3. Install "Fridge 3D Theme"
##   4. Call service frontend.reload_themes (or restart HA)
##
## The fridge dashboard view already requests `theme: "Fridge 3D"`,
## so it activates automatically once the theme is installed.
##
## Pure CSS variables — no JavaScript, no custom cards, no card_mod.
##

Fridge 3D:
  # ---------- Palette ----------
  primary-color: "#ffd479"
  accent-color: "#ffd479"
  primary-background-color: "#0a0d1c"
  secondary-background-color: "#10152b"
  primary-text-color: "#f3f6ff"
  secondary-text-color: "rgba(243, 246, 255, 0.72)"
  disabled-text-color: "rgba(243, 246, 255, 0.38)"
  divider-color: "rgba(255, 255, 255, 0.08)"
  app-header-background-color: "transparent"
  app-header-text-color: "#f3f6ff"

  # ---------- ha-card (3D glass base) ----------
  ha-card-background: "linear-gradient(145deg, rgba(255, 255, 255, 0.10) 0%, rgba(255, 255, 255, 0.02) 100%), linear-gradient(145deg, #1a1f3a 0%, #0a0d1c 100%)"
  card-background-color: "rgba(20, 25, 50, 0.85)"
  ha-card-border-radius: "20px"
  ha-card-border-width: "1px"
  ha-card-border-color: "rgba(255, 255, 255, 0.12)"
  ha-card-box-shadow: >-
    0 10px 22px rgba(0, 0, 0, 0.55),
    -5px -5px 12px rgba(255, 255, 255, 0.05),
    5px 5px 12px rgba(0, 0, 0, 0.55),
    inset 0 1px 0 rgba(255, 255, 255, 0.22),
    inset 0 -1px 0 rgba(0, 0, 0, 0.35)
  ha-card-header-color: "#f3f6ff"

  # ---------- Tile card ----------
  tile-color: "#ffd479"
  tile-icon-color: "#cfe2ff"
  tile-icon-hover-color: "#fff4c2"

  # ---------- Icon colors ----------
  state-icon-color: "#cfe2ff"
  state-icon-active-color: "#ffd479"
  paper-item-icon-color: "#cfe2ff"
  paper-item-icon-active-color: "#ffd479"

  # ---------- Toggles / switches ----------
  switch-checked-color: "#ffd479"
  switch-checked-track-color: "rgba(255, 212, 121, 0.5)"
  switch-unchecked-button-color: "#cfd5e0"
  switch-unchecked-track-color: "rgba(207, 213, 224, 0.4)"

  # ---------- Sliders ----------
  paper-slider-active-color: "#ffd479"
  paper-slider-knob-color: "#ffd479"
  paper-slider-knob-start-color: "#ffd479"
  paper-slider-pin-color: "#ffd479"
  paper-slider-secondary-color: "rgba(255, 212, 121, 0.3)"

  # ---------- Buttons ----------
  mdc-theme-primary: "#ffd479"
  mdc-text-button-label-text-color: "#f3f6ff"

  # ---------- Scrollbars ----------
  scrollbar-thumb-color: "rgba(255, 255, 255, 0.15)"
```

### File 2 — `README.md`

```markdown
# Fridge 3D — Home Assistant Theme

Pure-CSS glassmorphism theme for Home Assistant dashboards. Zero custom
JavaScript, zero `custom:*` cards, zero `card_mod` — just native CSS
variables consumed by HA's frontend.

## Install via HACS

[![Open your Home Assistant instance and add this repository to HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ibielopolskyi&repository=ha_fridge_theme&category=theme)

1. HACS → **Frontend** → ⋮ → **Custom repositories**
2. Repository: `ibielopolskyi/ha_fridge_theme`, Category: **Theme**
3. Install "Fridge 3D Theme"
4. Call `frontend.reload_themes` (or restart HA)
5. On any view config add `theme: "Fridge 3D"`

## Why pure CSS?

`custom:button-card` and `card_mod` ship JS runtimes that re-render or
MutationObserve the DOM on every state update. On low-resource displays
(older tablets, fridge panels) they hitch or crash the frontend. HA
themes are a single CSS-variable table the frontend reads once — no JS.

## License

MIT
```

## Verification steps after the push

1. Install via HACS on HA (user action — or they may have it auto-installing
   now that the repo has content).
2. Call `POST /api/services/frontend/reload_themes` on HA.
3. Call WebSocket `{"type":"frontend/get_themes"}`, confirm `"Fridge 3D"` is
   in `result.themes`.
4. Open the fridge dashboard on the device, visually confirm the 3D
   glassmorphism is applied (rounded corners, layered gradient backgrounds,
   outer drop shadow + inner rim highlight on every card). The view already
   has `theme: "Fridge 3D"` set, so no dashboard change is needed.
5. Report success to the user.

If step 3 shows `"Fridge 3D"` NOT present, the theme file path/format was
wrong. Double-check HACS put it at `/config/themes/fridge-3d/fridge-3d.yaml`
on the HA host and that the top-level YAML key is exactly `Fridge 3D:` (with
the capital F and 3D).

## Helper script (drop at `/tmp/ha_ws.py` in the new session)

```python
#!/usr/bin/env python3
import asyncio, json, sys, websockets

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiNzRkNTE4YTY3ZDQ0Yjc4YmFiMjdkZGQwZjI1ZDM4OSIsImlhdCI6MTc3NTc4OTAwOCwiZXhwIjoyMDkxMTQ5MDA4fQ.-Epwej3HJoAauY34Tm5fpAlpqsWZfVxkXMmZDIWDwI4"
WS_URL = "wss://rcnk01hkmjuexvkv6jnfmojs7f3mvwzd.ui.nabu.casa/api/websocket"

async def call(commands):
    results = []
    async with websockets.connect(WS_URL, max_size=20 * 1024 * 1024) as ws:
        assert json.loads(await ws.recv())["type"] == "auth_required"
        await ws.send(json.dumps({"type": "auth", "access_token": TOKEN}))
        assert json.loads(await ws.recv())["type"] == "auth_ok"
        for i, cmd in enumerate(commands, start=1):
            await ws.send(json.dumps({"id": i, **cmd}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == i and resp.get("type") == "result":
                    results.append(resp); break
    return results

async def main():
    commands = json.loads(sys.stdin.read())
    if isinstance(commands, dict): commands = [commands]
    print(json.dumps(await call(commands), indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
```

`pip install websockets` first, then:

```bash
TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiNzRkNTE4YTY3ZDQ0Yjc4YmFiMjdkZGQwZjI1ZDM4OSIsImlhdCI6MTc3NTc4OTAwOCwiZXhwIjoyMDkxMTQ5MDA4fQ.-Epwej3HJoAauY34Tm5fpAlpqsWZfVxkXMmZDIWDwI4'
BASE='https://rcnk01hkmjuexvkv6jnfmojs7f3mvwzd.ui.nabu.casa'

# Reload themes
curl -sS -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/services/frontend/reload_themes" \
  -X POST -H "Content-Type: application/json" -d '{}'

# Verify Fridge 3D is loaded
echo '[{"type":"frontend/get_themes"}]' | python3 /tmp/ha_ws.py

# Re-read the live dashboard (shouldn't need to change it)
echo '[{"type":"lovelace/config","url_path":"dashboard-fridge"}]' \
  | python3 /tmp/ha_ws.py
```

## Key facts — don't re-investigate these

- **`binary_sensor.wantspreset` template IS correct as-is**
  (`> timedelta(seconds=30)`). Do NOT flip it to `<`. The user confirmed this
  explicitly. The dashboard shows `camera.front_2` as the default and
  temporarily swaps to `camera.birdeye` in the 30-second window after the
  button is pressed.
- **The "Check Packages" service call is fixed by the user** — it now
  correctly calls `input_button.press` on `input_button.preset` from the
  native `button` card. Do not touch the tap_action.
- **Do NOT pollute `ryse_mqtt`** with fridge/dashboard/theme artifacts. That
  repo is the Ryse SmartShade HA integration only.
- **`custom:button-card`, `custom:mini-media-player`, `card_mod` are
  forbidden** — they're what was crashing the low-resource display. Native
  cards only: `tile`, `button`, `picture-entity`, `media-control`,
  `todo-list`, `grid`, `vertical-stack`, `horizontal-stack`, `conditional`,
  `panel`.
- **HA has no file-write API reachable from the MCP token**
  (`file.read_file` is read-only, no `file.write_file`, no writable
  `shell_command.*`, no `frontend/save_theme` WS command, the `hassio/*`
  supervisor API is blocked because the token user `igor` is
  admin-but-not-owner). The only way to get files onto `/config/` on this HA
  instance is HACS or manual (file editor add-on, Samba, etc.).
- **HACS is the delivery mechanism** for anything that has to land on
  `/config/`. Hence the dedicated theme repo.
- The PTZ camera for "Check Packages" is `camera.birdeye` per the user; the
  exact preset argument was never finalized but is moot now because the
  service call works.

## Status checklist

- [x] Dashboard rebuilt with zero custom cards (live, saved via WS)
- [x] Layout: all lights moved to right column as single vertical stack of
      horizontal tiles
- [x] Original tile labels restored (Kitchen Torch, Living Room, Side Lamp,
      Xmas Lights)
- [x] `theme: "Fridge 3D"` set on the fridge view
- [x] Check Packages button service call working (user-fixed)
- [x] `ryse_mqtt` cleaned of all fridge artifacts
- [x] `ha_fridge_theme` repo created on GitHub (empty)
- [ ] **Theme YAML pushed to `ha_fridge_theme/main`** ← YOU ARE HERE
- [ ] HACS custom-repo installed on HA
- [ ] `frontend.reload_themes` called and `"Fridge 3D"` present in
      `frontend/get_themes`
- [ ] Visual verification on the fridge device

Start by confirming `mcp__github__get_file_contents` on
`ibielopolskyi/ha_fridge_theme` returns something other than the scope-denied
error. If it works, push the two files and carry out the verification steps
above. If it doesn't, the repo still isn't in the session allowlist — ask the
user to fix the repo selection before proceeding.
