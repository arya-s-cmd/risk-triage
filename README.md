# Complaint Risk Scoring & Triage

[![Scale](https://img.shields.io/badge/scale-100k%2B%20events-informational.svg)](#)
[![Explainability](https://img.shields.io/badge/explainable-signals%20%2B%20weights-blue.svg)](#)
[![Deployment](https://img.shields.io/badge/deploy-Docker%20Compose-green.svg)](#)

A security-minded, ops-friendly system that **scores incoming complaints** and **auto-prioritizes** the analyst queue so high-risk items rise to the top. The model is **fully explainable** per record (no black boxes) and tuned for **low operational overhead**.

---

Operations teams drown in long *FIFO* queues. Critical items wait behind low-value noise, slowing responses and burning analyst time.

This project:
- Scores each complaint on **risk** using transparent signals.
- Pushes **urgent** items to the top of the queue.
- Shows **why** an item is ranked high (evidence, not vibes).

> Target impact (pilot assumption): **~20–30% faster time-to-first-action**. Validate by measuring queue latency before/after.

---

## What it does

- **Risk scoring** per complaint using:
  - Reuse of **phone / email / IP** across recent cases.
  - **Risk keywords** in text (e.g., *OTP, UPI, sextortion, loan app*).
  - **Recency** (near-real-time items score higher).
  - **Source trust** (noisier sources penalized less).
- **Explainable output** (JSON dict of signals & weights).
- **Prioritized queue API** (`GET /queue`) and UI list with filters.
- **Trust controls** per source (`GET/PUT /sources`) to adjust bias.
- **Seeded dataset** for instant demo; **Dockerized** for one-command run.

---


**Data model**
- `complaints(id, external_id, source, name, phone, email, ip, timestamp, text, score, risk_band, explanation_json)`
- `source_trust(id, source, trust)` — `0..1` (higher = more trusted ⇒ usually *lower* risk)

---

## How scoring works (explainable)

Let:
- `dup_signal = tanh(#recent phone/email/IP matches / 3)` (saturates after ~3)
- `kw_hits` = count of risk keywords in text
- `recency` = linear decay over 30 days (today = 1, 30d = 0)
- `trust` = `[0..1]` from `source_trust` (default `0.5`)

