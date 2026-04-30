# Technical Specification: Bambu Lab A1 mini Print Settings

## Printer: Bambu Lab A1 mini
- Build volume: 180 × 180 × 180 mm
- All specimens fit within build volume

## Material: PLA Matte Black
- Maximum contrast against white/cream paper
- Fuzzy skin on matte PLA creates mineral/organic texture
- Optional: One Bone-Grinder in PLA White (ghostly calcification)

---

## Per-Species Slicer Profiles

### Species 1: The Piercer

| Setting | Value | Rationale |
|---------|-------|-----------|
| Layer height | 0.28 mm | Fast, visible striations = growth rings |
| Perimeters | 2 | Thin spikes need minimal walls |
| Infill | 15% gyroid | Light — aggression is in silhouette |
| Print speed | 100 mm/s | Reliable on complex overhangs |
| Fuzzy Skin | ON | Thickness 0.4mm, Point Dist 0.5mm |
| Supports | Tree supports for spikes > 60° overhang |

**Est. print time**: ~30 min for 5 pieces (batch on single plate)

### Species 2: The Bone-Grinder

| Setting | Value | Rationale |
|---------|-------|-----------|
| Layer height | 0.28 mm | Fast, raw character |
| Perimeters | 3 | Mass needs structural walls |
| Infill | **50% gyroid** | **Heavy** — weight is the point |
| Print speed | 100 mm/s | |
| Fuzzy Skin | ON | Thickness **0.5mm**, Point Dist **0.3mm** — maximum roughness |
| Supports | None (no overhangs) |

**Est. print time**: ~50 min for 5 pieces (high infill = more time)

### Species 3: The Structural Parasite

| Setting | Value | Rationale |
|---------|-------|-----------|
| Layer height | 0.28 mm | |
| Perimeters | 2 | Thin struts |
| Infill | 20% gyroid | Balance of rigidity and speed |
| Print speed | 80 mm/s | Slower for thin strut reliability |
| Fuzzy Skin | ON | Thickness 0.2mm, Point Dist 1.0mm — subtle |
| Supports | Minimal (lattice is self-supporting) |
| First layer speed | 20 mm/s | Critical for thin strut adhesion |

**Est. print time**: ~35 min for 5 pieces

---

## Total Print Budget

| Phase | Pieces | Time |
|-------|--------|------|
| Piercers | 5 | ~30 min |
| Bone-Grinders | 5 | ~50 min |
| Structural Parasites | 5 | ~35 min |
| **Total** | **15** | **~115 min** |

Well within the 2-hour print budget.

## General Settings (All Species)

| Setting | Value |
|---------|-------|
| Nozzle temp | 215°C (extra hot for fuzzy skin adhesion at speed) |
| Bed temp | 60°C |
| Cooling | 100% fan from layer 3 |
| Retraction | 1mm @ 35mm/s |
| Travel speed | 200 mm/s |
| Z-hop | 0.4mm (avoid spike tip collisions) |

## Print Orientation Notes
- **Piercers**: Print flat (base tongue on bed), spikes pointing up
- **Bone-Grinders**: Print flat (base tongue on bed), mass body on top
- **Structural Parasites**: Print flat (base tongue on bed), lattice/wings above
- All functional surfaces (base tongue) face the build plate for best finish
