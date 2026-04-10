#!/usr/bin/env python3
"""Generate an isometric 3D SVG floor plan of Igor's home.

Layout is inferred from the entities in Home Assistant:
  - Balcony (cover.balcony_curtain_none, light.balcony_lights)
  - Living room (light.living_room_lights, climate.living_room, cover.living_room_shade_none)
  - Kitchen (light.kitchen_switch, light.kitchen_torch, cover.curtains)
  - Dining (light.dining_room_lights, cover.dining_shade_none)
  - Corridor (light.corridor)
  - Master bedroom (light.mysh_bedroom_lights)
  - Master bath, Office (cover.office_shade_none)
  - Foyer (light.foyer_light, light.top)
"""
import base64
import json
import math
from collections import Counter

# ------------------------------------------------------------------
# Geometry: top-down grid, then isometric projection.
#
# Projection angle was 30° (the classic isometric). We pull it down to
# 26° so the resulting image is roughly 16:9 — which matches landscape
# tablet / desktop viewports and lets the floor plan fill a full-screen
# panel view with minimal letterbox. A bigger displayed image means
# bigger pixel distance between icons at the same grid positions.
# ------------------------------------------------------------------
ISO_ANGLE_DEG = 26
cos_a = math.cos(math.radians(ISO_ANGLE_DEG))
sin_a = math.sin(math.radians(ISO_ANGLE_DEG))

SCALE = 64
WALL_H = 1.4  # extrusion height in grid units

ROOMS = [
    {"name": "Balcony",     "x": 0, "y": 0, "w": 3, "h": 2,
     "fill_top": "#2b4a6b", "fill_edge": "#1e334a", "accent": "#6fa8e0"},
    {"name": "Kitchen",     "x": 3, "y": 0, "w": 4, "h": 3,
     "fill_top": "#7a5230", "fill_edge": "#4e341e", "accent": "#f0b57a"},
    {"name": "Master BR",   "x": 7, "y": 0, "w": 4, "h": 5,
     "fill_top": "#35504a", "fill_edge": "#20302c", "accent": "#9fd7c5"},
    {"name": "Dining",      "x": 3, "y": 3, "w": 4, "h": 2,
     "fill_top": "#7a3a3a", "fill_edge": "#4a2323", "accent": "#ff9a8c"},
    {"name": "Living",      "x": 0, "y": 2, "w": 3, "h": 5,
     "fill_top": "#3a4d75", "fill_edge": "#232f4a", "accent": "#8cb2ff"},
    {"name": "Corridor",    "x": 3, "y": 5, "w": 4, "h": 2,
     "fill_top": "#4a4a58", "fill_edge": "#2d2d38", "accent": "#c8c8d8"},
    {"name": "Bath",        "x": 7, "y": 5, "w": 2, "h": 2,
     "fill_top": "#2f5a6a", "fill_edge": "#1c3640", "accent": "#7edbf0"},
    {"name": "Office",      "x": 9, "y": 5, "w": 2, "h": 2,
     "fill_top": "#533070", "fill_edge": "#341f46", "accent": "#c89bff"},
    {"name": "Foyer",       "x": 0, "y": 7, "w": 11, "h": 2,
     "fill_top": "#5a4530", "fill_edge": "#392a1d", "accent": "#ffcf8e"},
]


def iso(x, y, z=0, ox=0, oy=0):
    sx = (x - y) * cos_a * SCALE + ox
    sy = ((x + y) * sin_a - z) * SCALE + oy
    return sx, sy


def compute_bounds():
    pts = []
    # include ground plane offset
    for r in ROOMS:
        for dx in (0, r["w"]):
            for dy in (0, r["h"]):
                for dz in (0, WALL_H):
                    pts.append(iso(r["x"] + dx, r["y"] + dy, dz))
    # ground halo
    pts.append(iso(-1.5, -1.5, -0.2))
    pts.append(iso(12.5, -1.5, -0.2))
    pts.append(iso(12.5, 10.5, -0.2))
    pts.append(iso(-1.5, 10.5, -0.2))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


MINX, MAXX, MINY, MAXY = compute_bounds()
PAD = 60
WIDTH = (MAXX - MINX) + 2 * PAD
HEIGHT = (MAXY - MINY) + 2 * PAD
OX = -MINX + PAD
OY = -MINY + PAD


def p(x, y, z=0):
    return iso(x, y, z, OX, OY)


def fmt(points):
    return " ".join(f"{pt[0]:.1f},{pt[1]:.1f}" for pt in points)


# ------------------------------------------------------------------
# Perimeter detection: unit-edge sharing
# ------------------------------------------------------------------
def unit_edges(r):
    x, y, w, h = r["x"], r["y"], r["w"], r["h"]
    edges = []
    for i in range(w):
        edges.append(((x + i, y), (x + i + 1, y)))             # N
        edges.append(((x + i, y + h), (x + i + 1, y + h)))      # S
    for j in range(h):
        edges.append(((x + w, y + j), (x + w, y + j + 1)))      # E
        edges.append(((x, y + j), (x, y + j + 1)))              # W
    return edges


all_edges = []
for r in ROOMS:
    for e in unit_edges(r):
        all_edges.append(e)
edge_count = Counter()
for a, b in all_edges:
    key = tuple(sorted([a, b]))
    edge_count[key] += 1
perimeter = [k for k, c in edge_count.items() if c == 1]

# ------------------------------------------------------------------
# SVG assembly
# ------------------------------------------------------------------
svg_body = []

# <defs>: gradients per room + common filters
defs = ['<defs>']
defs.append('''
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="2" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="drop" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="6"/>
  <feOffset dx="0" dy="18" result="off"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.55"/></feComponentTransfer>
  <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<radialGradient id="halo" cx="50%" cy="50%" r="60%">
  <stop offset="0%" stop-color="#1a2a4a" stop-opacity="0.9"/>
  <stop offset="60%" stop-color="#0a1020" stop-opacity="0.6"/>
  <stop offset="100%" stop-color="#05070f" stop-opacity="0"/>
</radialGradient>''')
for r in ROOMS:
    gid = f"g_{r['name'].lower().replace(' ','_')}"
    defs.append(f'''
<linearGradient id="{gid}" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="{r['fill_top']}" stop-opacity="0.95"/>
  <stop offset="55%" stop-color="{r['fill_top']}" stop-opacity="0.82"/>
  <stop offset="100%" stop-color="{r['fill_edge']}" stop-opacity="0.92"/>
</linearGradient>''')
defs.append('</defs>')
svg_body.append("\n".join(defs))

# Ground halo (soft glow under house)
halo_pts = [p(-1.5, -1.5), p(12.5, -1.5), p(12.5, 10.5), p(-1.5, 10.5)]
svg_body.append(
    f'<polygon points="{fmt(halo_pts)}" fill="url(#halo)" filter="url(#soft)"/>'
)

# Floors — painter's order (sort by x+y ascending so furthest first)
sorted_rooms = sorted(ROOMS, key=lambda r: r["x"] + r["y"])
for r in sorted_rooms:
    x, y, w, h = r["x"], r["y"], r["w"], r["h"]
    floor = [p(x, y, 0), p(x + w, y, 0), p(x + w, y + h, 0), p(x, y + h, 0)]
    gid = f"g_{r['name'].lower().replace(' ','_')}"
    svg_body.append(
        f'<polygon points="{fmt(floor)}" fill="url(#{gid})" '
        f'stroke="#0a0d1c" stroke-width="0.6" opacity="0.95"/>'
    )

# Walls (perimeter only) — painter's order sorted by back-most endpoint
wall_segments = []
for a, b in perimeter:
    depth = (a[0] + a[1] + b[0] + b[1]) / 2
    wall_segments.append((depth, a, b))
wall_segments.sort(key=lambda s: s[0])

for _, a, b in wall_segments:
    ax, ay = a
    bx, by = b
    p1 = p(ax, ay, 0)
    p2 = p(bx, by, 0)
    p3 = p(bx, by, WALL_H)
    p4 = p(ax, ay, WALL_H)
    # distinct shading for N/S (vertical in world) vs E/W walls
    if ax == bx:
        face = "#2a3348"
        top = "#475274"
    else:
        face = "#1d2435"
        top = "#374260"
    svg_body.append(
        f'<polygon points="{fmt([p1, p2, p3, p4])}" fill="{face}" '
        f'stroke="#0a0d1c" stroke-width="0.8"/>'
    )
    # thin top highlight line
    svg_body.append(
        f'<line x1="{p4[0]:.1f}" y1="{p4[1]:.1f}" x2="{p3[0]:.1f}" y2="{p3[1]:.1f}" '
        f'stroke="{top}" stroke-width="1.4" stroke-linecap="round"/>'
    )

# Interior wall hints: draw very short (0.35) bumps on shared interior edges
# to imply room separation without blocking sight
interior_keys = [k for k, c in edge_count.items() if c > 1]
interior_h = 0.35
# Dedupe: k is already sorted tuple
for a, b in interior_keys:
    p1 = p(a[0], a[1], 0)
    p2 = p(b[0], b[1], 0)
    p3 = p(b[0], b[1], interior_h)
    p4 = p(a[0], a[1], interior_h)
    svg_body.append(
        f'<polygon points="{fmt([p1, p2, p3, p4])}" fill="#131826" '
        f'stroke="#0a0d1c" stroke-width="0.4" opacity="0.85"/>'
    )

# Accent strips (highlight edge along each room)
for r in ROOMS:
    cx = r["x"] + r["w"] / 2
    cy = r["y"] + r["h"] / 2
    lx, ly = p(cx, cy, 0.03)
    svg_body.append(
        f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#ffffff" '
        f'font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" '
        f'font-weight="700" letter-spacing="1.2" text-anchor="middle" '
        f'opacity="0.88" filter="url(#soft)">{r["name"].upper()}</text>'
    )

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'viewBox="0 0 {WIDTH:.0f} {HEIGHT:.0f}" '
    f'width="{WIDTH:.0f}" height="{HEIGHT:.0f}">\n'
    + "\n".join(svg_body)
    + "\n</svg>"
)

with open("/tmp/floorplan_3d.svg", "w") as f:
    f.write(svg)

# ------------------------------------------------------------------
# Compute percentage positions for interactive entity icons
# ------------------------------------------------------------------
def pct(x, y, z=0):
    sx, sy = p(x, y, z)
    return (sx / WIDTH * 100, sy / HEIGHT * 100)


# z offsets per domain so icons at the same floor-grid position still
# separate vertically in the iso projection (lights hang high, curtains
# and thermostats sit lower on the wall).
Z_BY_DOMAIN = {
    "light":   WALL_H + 0.45,
    "cover":   WALL_H + 0.05,
    "climate": WALL_H - 0.30,
}


def room_pct(name, dx=0.5, dy=0.5, z=None, domain=None):
    r = next(r for r in ROOMS if r["name"] == name)
    if z is None:
        z = Z_BY_DOMAIN.get(domain, WALL_H + 0.1)
    return pct(r["x"] + r["w"] * dx, r["y"] + r["h"] * dy, z)


# Entities we want to pin to rooms.
#
# Multi-icon rooms (Kitchen, Living, Dining, Balcony, Foyer) use opposite
# edges/corners so touchable areas are maximally spread while keeping every
# icon inside its room.
def _rp(room, dx, dy, entity, icon):
    domain = entity.split(".")[0]
    x, y = room_pct(room, dx, dy, domain=domain)
    return (x, y, icon)


icon_positions = {
    # Balcony (3x2)
    "light.balcony_lights":        _rp("Balcony",  0.22, 0.55, "light.balcony_lights",        "mdi:lightbulb"),
    "cover.balcony_curtain_none":  _rp("Balcony",  0.78, 0.55, "cover.balcony_curtain_none",  "mdi:blinds-horizontal"),
    # Kitchen (4x3)
    "light.kitchen_switch":        _rp("Kitchen",  0.15, 0.20, "light.kitchen_switch",        "mdi:countertop"),
    "light.kitchen_torch":         _rp("Kitchen",  0.85, 0.20, "light.kitchen_torch",         "mdi:lightbulb-on"),
    "cover.curtains":              _rp("Kitchen",  0.50, 0.85, "cover.curtains",              "mdi:curtains"),
    # Dining (4x2)
    "light.dining_room_lights":    _rp("Dining",   0.22, 0.50, "light.dining_room_lights",    "mdi:silverware-fork-knife"),
    "cover.dining_shade_none":     _rp("Dining",   0.78, 0.50, "cover.dining_shade_none",     "mdi:blinds-horizontal"),
    # Living (3x5)
    "light.living_room_lights":    _rp("Living",   0.50, 0.18, "light.living_room_lights",    "mdi:sofa"),
    "cover.living_room_shade_none":_rp("Living",   0.50, 0.52, "cover.living_room_shade_none","mdi:blinds-horizontal"),
    "climate.living_room":         _rp("Living",   0.50, 0.86, "climate.living_room",         "mdi:thermostat"),
    # Single-icon rooms
    "light.corridor":              _rp("Corridor", 0.50, 0.50, "light.corridor",              "mdi:lightbulb"),
    "cover.office_shade_none":     _rp("Office",   0.50, 0.50, "cover.office_shade_none",     "mdi:blinds-horizontal"),
    "light.mysh_bedroom_lights":   _rp("Master BR",0.50, 0.50, "light.mysh_bedroom_lights",   "mdi:bed"),
    # Foyer (11x2) — stretched along the wide hall
    "light.foyer_light":           _rp("Foyer",    0.10, 0.55, "light.foyer_light",           "mdi:door"),
    "light.top":                   _rp("Foyer",    0.90, 0.55, "light.top",                   "mdi:ceiling-light"),
}

with open("/tmp/floorplan_icons.json", "w") as f:
    json.dump(
        {
            "width": WIDTH,
            "height": HEIGHT,
            "icons": {
                k: {"top": round(v[1], 2), "left": round(v[0], 2), "icon": v[2]}
                for k, v in icon_positions.items()
            },
        },
        f,
        indent=2,
    )

# Base64 data URL
b64 = base64.b64encode(svg.encode()).decode()
data_url = f"data:image/svg+xml;base64,{b64}"
with open("/tmp/floorplan_data_url.txt", "w") as f:
    f.write(data_url)

print(f"SVG: {len(svg)} bytes, data URL: {len(data_url)} bytes")
print(f"Canvas: {WIDTH:.0f} x {HEIGHT:.0f}")
print(f"Rooms: {len(ROOMS)}, perimeter walls: {len(wall_segments)}, interior hints: {len(interior_keys)}")
print(f"Icons: {len(icon_positions)}")
