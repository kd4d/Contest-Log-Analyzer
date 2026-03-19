# RF System Architecture (from sketch)

```mermaid
flowchart LR
    subgraph TX["TX side"]
        TXA[TX Antennas]
        ROT[ROTORS]
        TXC[Control / Status]
        ROT -->|RF| TXA
        TXC --> ROT
    end

    subgraph CENTER["Cable Interconnects & Operating Positions"]
        CI[Cable Interconnects]
        OP[Operating Positions]
        DRF[DRF]
        RCS[Rotor Control / Status]
        PWR1[Power]
        OP --> DRF
        OP --> RCS
        OP --> PWR1
        RCS --> DRF
    end

    subgraph RX["RX side"]
        RXA[RX Antennas]
        RXC[Control]
        RXC --> RXA
    end

    subgraph INFRA["Facility & Internet"]
        FAC[Facility]
        PWR2[Power]
        IF[Internet Functions]
        LAN[Wired LAN]
        WIFI[WiFi]
        FAC --> PWR2
        PWR2 --> IF
        LAN --> IF
        WIFI --> IF
    end

    TXA -->|AF| CI
    TXC --> CI
    CI --> OP
    CI -->|RF| RXA
    OP -->|RX and RF| IF
```

## Blocks

| Area | Blocks |
|------|--------|
| **TX** | TX Antennas, ROTORS (RF to antennas), Control/Status (to ROTORS) |
| **Center** | Cable Interconnects, Operating Positions, DRF, Rotor Control/Status, Power |
| **Infra** | Facility → Power → Internet Functions (inputs: RX and RF from OP, Wired LAN, WiFi); Internet Functions to the right of Facility |
| **RX** | RX Antennas (RF from Cable Interconnects), Control (to RX Antennas) |
