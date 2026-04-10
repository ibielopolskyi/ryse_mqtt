# Lovelace Dashboards

This folder contains Lovelace dashboard definitions that have been pushed to the
running Home Assistant instance via the WebSocket API (`lovelace/config/save`).

## `overview_3d.yaml`

A modern, tablet-oriented "Overview 3D" dashboard inspired by the
[Best Tablet Dashboard 2022](https://community.home-assistant.io/t/best-tablet-dashboard-2022-lovelace/478691/2)
thread.

- **Dashboard URL path:** `/overview-3d`
- **Sidebar icon:** `mdi:cube-outline`
- **Visual style:** dark glassmorphism with perspective-tilted cards, neumorphic
  3D buttons, radial light gradients and subtle parallax on the floor plan.
- **Custom cards used** (already installed via HACS in this instance):
  - `custom:button-card` – 3D glass/neumorphic room buttons
  - `custom:mini-graph-card` – Temperature / humidity trend
  - `custom:mini-media-player` – Spotify control
  - `card-mod` – CSS styling for depth, shadows, and perspective
- **Sections in the view:**
  1. Hero greeting with live time + weather from `weather.forecast_home`
  2. Scene quick-actions (`scene.curtains_open`, `curtains_closed`, `dimmed_lights_for_tv`, `after_tv`)
  3. Floor plan (`/local/layout1.jpg`) rendered with 3D perspective tilt and interactive icons
  4. Thermostat (`climate.living_room`)
  5. Lights grid (kitchen, dining, living, foyer, top, corridor, balcony, bedroom, dreamview)
  6. Shades & doors grid (curtains, dining/living/office/balcony shades, garage door)
  7. Spotify mini media player (`media_player.spotify_1285970688`)
  8. Living-room temperature/humidity 24h mini-graph
  9. Presence row (`person.igor`, `person.mysh_2`, `person.lena_2`)
  10. Live camera grid (front, garage, birdeye, pet)
  11. Roborock S8 Pro Ultra button
  12. Entities summary (temps, humidities, forecast, sun)

### How this file is applied

The running HA instance stores the dashboard inside
`.storage/lovelace.overview_3d`. This YAML is the canonical source – re-apply it
with:

```bash
python3 scripts/push_dashboard.py dashboards/overview_3d.yaml overview-3d
```

(The push script uses the HA WebSocket API `lovelace/config/save` with
`url_path: overview-3d`.)
