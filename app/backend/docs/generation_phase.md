# Generation Phase

## Phase 3 of the End-to-End AI Personalization Engine

This document outlines the Generation Phase responsible for producing model outputs conditioned on the prioritized segment and context. (Placeholder — expand with design notes, safety, and rewriting subcomponents.)

- Entry: reads prioritized segment from graph state
- Components: `aimessage`, `safety_agent`, `rewrite`
- Outputs: generated text, safety flags, alternative variants
