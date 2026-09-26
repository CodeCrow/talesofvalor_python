---
paths:
  - "**"
---

# Architecture/Layout Rules

- work performed on a single instance should happen in the model.py file
- work performed across multiple instances should happen in `<package>/services/**`