# W3LPL Station Architecture

This folder holds the spec and assets for the **W3LPL Station Architecture** diagram so that any agent or tool can reproduce a matching diagram (PNG, Draw.io, or Mermaid).

## Contents

- **`Docs/architecture-diagram-spec.md`** – Human- and agent-readable spec (layout, blocks, connections, styling). Give this to a new agent so it can generate a matching PNG.
- **`assets/architecture-diagram-spec.json`** – Machine-readable structure (sections, blocks, connections) for programmatic generation.
- **Reference image** – Copy or link `rf-system-architecture-cleaned.png` into `assets/` from the Contest-Log-Analyzer repo if you need a visual reference in this repo.

## Generating the diagram

1. **New agent (PNG / Mermaid / Draw.io):**  
   Tell the agent: “Read `Docs/architecture-diagram-spec.md` and generate a diagram (PNG, or Mermaid, or Draw.io) that matches that spec. Reference image: `assets/rf-system-architecture-cleaned.png` if present.”

2. **PowerPoint slide:**  
   Use the script in the main Contest-Log-Analyzer repo:  
   `assets/make_w3lpl_slide.py`  
   It builds `W3LPL_Station_Architecture.pptx` from the diagram image.

## Moving to a separate repo

If you open `Desktop\Repos\W3LPL_Architecture` as its own workspace, copy this folder’s contents there. The spec and JSON stay the same; only the reference image path may need to point to where you store the PNG.
