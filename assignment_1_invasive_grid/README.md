# The Invasive Grid

> **The bookmark was the most obedient object in the library. Now it has teeth.**

A physical book colonized by 3D-printed parametric bookmarks that have mutated beyond recognition. Fifteen specimens — placed at prime-numbered pages — progress through three evolutionary stages: infection, colonization, and structural transformation. The book becomes a forensic anomaly.

**Course**: Object of Thought · Bezalel Academy of Arts and Design  
**Assignment**: 1 — Experimentalize a mundane object  
**Timeline**: 24 hours  
**Year**: 2026

---

## Concept

The **bookmark** is the most submissive object in a reader's ecology: thin, flat, silent. It exists to disappear between pages.

This project mutates the bookmark into an **aggressive architectural parasite**. Three "species" of mutant bookmarks are generated via parametric Blender Python scripts, 3D-printed on a Bambu Lab A1 mini, and inserted at prime-numbered pages. The result looks like a forensic specimen — as if the bookmarks have evolved, consumed their host, and restructured the book's anatomy from within.

### Three Species

| Species | Behavior | Phase |
|---------|----------|-------|
| 🦔 **The Piercer** | Jagged spikes erupt past margins, destroying the rectangular silhouette | Infection |
| 🦴 **The Bone-Grinder** | Dense calcified mass adds geological weight; the book sags | Colonization |
| 🕸️ **The Structural Parasite** | Lattice skeleton forces pages apart at 20°–60° angles | Transformation |

All species share a **vestigial base tongue** (40 × 130 × 2 mm) — the bookmark's original flat form, preserved as evolutionary memory.

---

## Running the Generator

### Prerequisites
- [Blender 5.0+](https://www.blender.org/download/) installed at `/Applications/Blender.app/`

### Generate all 15 STLs
```bash
cd assignment_1_invasive_grid
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/generate_all.py
```

### Generate a single species
```bash
# Piercers only
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/generate_piercers.py

# Bone-Grinders only
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/generate_bone_grinders.py

# Structural Parasites only
/Applications/Blender.app/Contents/MacOS/Blender --background --python src/generate_structural_parasites.py
```

Output: STL files in `models/` + colonization map in `data/prime_colonization.json`

---

## File Structure

```
assignment_1_invasive_grid/
├── README.md
├── .gitignore
├── src/
│   ├── config.py                          # Shared parameters & prime logic
│   ├── utils.py                           # Blender helpers (export, boolean, etc.)
│   ├── bookmark_base.py                   # Vestigial tongue generator
│   ├── generate_piercers.py               # Species 1: spiked bookmarks
│   ├── generate_bone_grinders.py          # Species 2: calcified mass bookmarks
│   ├── generate_structural_parasites.py   # Species 3: lattice skeleton bookmarks
│   └── generate_all.py                    # Master runner
├── models/
│   ├── piercers/          (5 STLs)
│   ├── bone_grinders/     (5 STLs)
│   └── structural_parasites/ (5 STLs)
├── spec/
│   ├── conceptual_framework.md            # The parasitological frame
│   ├── technical_spec.md                  # Slicer settings per species
│   └── colonization_protocol.md           # Prime placement + assembly guide
├── media/                                 # Photos & documentation images
└── data/
    └── prime_colonization.json            # Page → species → variation mapping
```

---

## Print Settings (Bambu Lab A1 mini)

| Species | Infill | Fuzzy Skin | Est. Time |
|---------|--------|------------|-----------|
| Piercer | 15% gyroid | 0.4mm / 0.5mm dist | ~30 min |
| Bone-Grinder | **50% gyroid** | **0.5mm / 0.3mm dist** | ~50 min |
| Structural Parasite | 20% gyroid | 0.2mm / 1.0mm dist | ~35 min |
| **Total** | | | **~115 min** |

**Material**: PLA Matte Black · **Layer height**: 0.28mm · **Nozzle**: 215°C

See [spec/technical_spec.md](spec/technical_spec.md) for full slicer profiles.

---

## Colonization Protocol

Inserts placed at **prime-numbered pages** (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79).

The evolutionary sequence creates a narrative arc:
1. **Infection** (pp. 2–17): Piercers bristle the silhouette
2. **Colonization** (pp. 19–43): Bone-Grinders add geological weight
3. **Transformation** (pp. 47–79): Structural Parasites splay the ribcage

See [spec/colonization_protocol.md](spec/colonization_protocol.md) for the full assembly guide.

---

## Gallery Label

> **The Invasive Grid** (2026)  
> PLA, paper, spine tension, prime numbers  
> Fifteen 3D-printed bookmarks — mutated beyond recognition — colonize a paperback at prime-numbered pages. Piercers erupt past the margins. Bone-Grinders add geological weight. Structural Parasites force the spine into involuntary architecture.

---

## Discussion Prompts

1. *Is a book still a book if its primary function (opening/reading) is physically denied?*
2. *At what point does the bookmark — the most submissive object in the library — become the dominant form?*
3. *If the bookmark has "evolved" to consume its host, what does this say about the tools we design as servants?*

---

## License
Academic project — Bezalel Academy of Arts and Design, 2026.
