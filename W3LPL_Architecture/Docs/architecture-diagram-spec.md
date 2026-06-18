# W3LPL Station Architecture – Diagram Spec

Use this spec so an agent (or Draw.io/Mermaid) can generate a diagram that matches the reference PNG.

## Reference image
- **Path:** `assets/rf-system-architecture-cleaned.png`
- Use as layout reference when generating PNG, Draw.io, or Mermaid.

## Layout (left → right, then bottom)

### Row 1 – Main flow
| Section    | Blocks / elements |
|-----------|--------------------|
| **Left**  | TX Antennas (top) ← RF from ROTORS; ROTORS (middle); Control/Status (bottom) → to center. |
| **Center**| Cable Interconnects (top bar); Operating Positions below; DRF, Rotor Control/Status, Power stacked left of OP. AF from TX, control from TX into Cable Interconnects. Cable Interconnects → Operating Positions. RX and RF from OP to Internet Functions. |
| **Right** | RX Antennas (top) ← RF from Cable Interconnects; Control (bottom) → to RX Antennas. |

### Row 2 – Infrastructure (below center)
| Order | Block / connection |
|-------|-------------------|
| 1 | **Facility** (left) → Power |
| 2 | **Power** → Internet Functions |
| 3 | **Internet Functions** (center); inputs: RX and RF (from OP), Wired LAN, WiFi, Power (from Facility). |

## Connections (arrows, labeled)
- ROTORS --[RF]--> TX Antennas
- Control/Status (TX) --> ROTORS
- TX Antennas --[AF]--> Cable Interconnects
- Control/Status (TX) --> Cable Interconnects
- Cable Interconnects --> Operating Positions
- Operating Positions --> DRF, Rotor Control/Status, Power
- Cable Interconnects --[RF]--> RX Antennas
- Control (RX) --> RX Antennas
- Operating Positions --[RX and RF]--> Internet Functions
- Wired LAN --> Internet Functions
- WiFi --> Internet Functions
- Facility --> Power --> Internet Functions

## Styling
- **Title:** "W3LPL Station Architecture"; large, bold; dark blue (e.g. #1F4E79).
- **Blocks:** Rectangles, clear labels, consistent spacing.
- **Arrows:** Label key signals (RF, AF, Control, RX and RF).
- **Orientation:** Landscape; main flow left-to-right, then infrastructure row below center.

## Output
- PNG that matches the reference, or
- Draw.io XML, or
- Mermaid diagram code (flowchart LR with subgraphs for TX, center, RX, infra).
