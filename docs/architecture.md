# Architecture Documentation

This document describes the runtime architecture of the `lab8-pygame` project based on the current source in `main.py`.

## Scope
- Entry point: `main()` in `main.py`
- Runtime model: one pygame loop driving a list of `MovingSquare` objects
- External libraries: `pygame`, `random`, `math`

## 1) Dependency Graph

```mermaid
flowchart LR
  subgraph "Project Module"
    p0["main.py"]
  end

  subgraph "External Dependencies"
    p1["pygame"]
    p2["random"]
    p3["math"]
  end

  p0 -->|"import"| p1
  p0 -->|"import"| p2
  p0 -->|"import"| p3
```

`main.py` is the only project module and imports the three runtime dependencies used for rendering, randomization, and geometry.

## 2) High-Level Runtime Flow

```mermaid
flowchart TD
  n0["Program Start"] --> n1["Enter main()"]
  n1 --> n2["Initialize pygame display and clock"]
  n2 --> n3["Create squares list"]
  n3 --> n4["Begin frame loop"]

  n4 --> n5["Compute dt from clock.tick(FPS)"]
  n5 --> n6["Read events"]
  n6 --> n7["Update each square"]
  n7 --> n8["Replace dead squares"]
  n8 --> n9["Clear screen and draw squares"]
  n9 --> n10["Draw FPS text"]
  n10 --> n11["Flip display"]
  n11 --> n4

  n6 --> n12["QUIT event"]
  n12 --> n13["Set running to False"]
  n13 --> n14["Exit loop"]
  n14 --> n15["Call pygame.quit()"]
```

The loop is frame-rate controlled by `clock.tick(FPS)` and uses `dt` for time-based motion.

## 3) Function-Level Call Graph

```mermaid
flowchart TD
  c0["main"] --> c1["MovingSquare.__init__"]
  c0 --> c2["MovingSquare.update"]
  c0 --> c3["MovingSquare.draw"]

  c2 --> c4["MovingSquare.apply_steering_and_jitter"]
  c4 --> c5["MovingSquare.find_nearest_larger_square"]
  c4 --> c6["MovingSquare.find_nearest_smaller_square"]
  c4 --> c7["MovingSquare.distance_between_centers"]
  c4 --> c8["MovingSquare.compute_flee_vector"]
  c4 --> c9["MovingSquare.compute_chase_vector"]

  c5 --> c7
  c6 --> c7
  c7 --> c10["MovingSquare.get_center"]
  c8 --> c10
  c9 --> c10
```

Square behavior is encapsulated inside class methods, while `main()` orchestrates lifecycle and rendering.

## 4) Primary Execution Sequence

```mermaid
sequenceDiagram
  participant R as "Python Runtime"
  participant M as "main()"
  participant C as "pygame.time.Clock"
  participant E as "pygame.event"
  participant S as "MovingSquare"
  participant D as "pygame.display"

  R->>M: "Invoke main()"
  M->>D: "set_mode and set_caption"
  M->>C: "Create clock"
  M->>S: "Create initial squares"

  loop "Each frame while running"
    M->>C: "tick(FPS)"
    C-->>M: "Return dt"

    M->>E: "get()"
    E-->>M: "Return events"

    alt "Event type is QUIT"
      M->>M: "Set running = False"
    else "No QUIT event"
      loop "For each square"
        M->>S: "update(squares, dt)"
        S->>S: "apply_steering_and_jitter(squares)"
        S->>S: "find nearest larger and smaller"
        S->>S: "compute flee or chase vector"
        S->>S: "integrate x, y, angle"
        S->>S: "check lifespan and bounds"
      end

      loop "For each index"
        M->>M: "Replace dead square with new MovingSquare()"
      end

      loop "For each square"
        M->>S: "draw(surface)"
      end

      M->>D: "flip()"
    end
  end

  M->>D: "quit()"
```

This sequence captures the primary control loop, branch on `QUIT`, and nested loops for update/rebirth/draw.

## Notes and Assumptions
- The architecture is inferred strictly from `main.py`.
- No additional project modules were found under this project root.
- There is no separate service or persistence layer; all state is in-process in memory.
