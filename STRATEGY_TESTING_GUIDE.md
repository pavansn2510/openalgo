# OpenAlgo Strategy Testing & Integration Guide

Welcome to your dedicated **OpenAlgo** deployment, cloned directly from your fork:
`https://github.com/pavansn2510/openalgo.git`

This project is configured side-by-side with your existing systems without touching or modifying any of your existing strategy code or logs.

---

## 🏗️ Architecture & Setup Status

- **Project Location**: `/root/BatmanStrategy/openalgo` (also symlinked at `/root/openalgo`).
- **Isolation**: Added to `.gitignore` of `BatmanStrategy`. All existing Batman code, journals, and logs remain 100% untouched.
- **Python Environment**: Managed via `uv` on Python 3.12 (`openalgo/.venv`).
- **Security**: Cryptographically secure `APP_KEY` and `API_KEY_PEPPER` generated in `openalgo/.env`.
- **Broker Configuration**: Initialized with your FYERS API keys and `http://127.0.0.1:5000/fyers/callback`.
- **Frontend**: React 19 SPA built in `frontend/dist/`.
- **Test Verification**: 13/13 multi-leg option tests passed (`pytest test/test_options_multiorder_api.py`).

---

## 🚀 How to Start OpenAlgo

From your terminal:

```bash
cd /root/BatmanStrategy/openalgo
/root/.local/bin/uv run app.py
```

OpenAlgo will start and serve the following interfaces:
- **Web App / Dashboard**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **API Swagger Documentation**: [http://127.0.0.1:5000/api/docs](http://127.0.0.1:5000/api/docs)
- **Analyzer / Sandbox (Paper Trading)**: [http://127.0.0.1:5000/analyzer](http://127.0.0.1:5000/analyzer)
- **Python Strategy Manager**: [http://127.0.0.1:5000/python](http://127.0.0.1:5000/python)

---

## 🧪 Testing Your Strategies Without Risk (Sandbox / Analyzer Mode)

OpenAlgo includes a built-in virtual sandbox with **₹1 Crore simulated capital** that calculates realistic margins, fills, and PnL without placing real orders with your broker:

1. Open [http://127.0.0.1:5000/analyzer](http://127.0.0.1:5000/analyzer) in your browser.
2. Toggle **Analyzer Mode ON**.
3. Any order sent via API or webhooks is routed to `db/sandbox.db` instead of the live broker.

---

## 🦇 Testing the Batman Strategy on OpenAlgo

A dedicated testing script has been provided at:
`openalgo/strategies/test_batman_openalgo.py`

### 1. Test 4-Leg Classic Batman
```bash
cd /root/BatmanStrategy/openalgo
/root/.local/bin/uv run python strategies/test_batman_openalgo.py --sandbox --structure 4leg
```

### 2. Test 6-Leg Margin-Saver Batman (with Penny Hedges)
```bash
/root/.local/bin/uv run python strategies/test_batman_openalgo.py --sandbox --structure 6leg
```

### 3. Check Live / Virtual Position PnL
```bash
/root/.local/bin/uv run python strategies/test_batman_openalgo.py --status
```

---

## 🔄 How OpenAlgo Replaces Manual Trading

| Manual Step | Replaced by OpenAlgo |
| :--- | :--- |
| **Strike Calculation & Formatting** | OpenAlgo auto-resolves strikes by offset (`ATM`, `OTM3`, `OTM15`) |
| **Margin Sequencing (Rule 1)** | OpenAlgo's `optionsmultiorder` automatically submits **BUY legs first**, waits for margin relief, then submits SELL wings |
| **Broker Login Daily Friction** | Log in once daily on the OpenAlgo Web UI between 8:00–9:00 AM |
| **Emergency Exits** | 1-click square-off available directly on the web dashboard |
| **Multi-Broker Switching** | Switch between FYERS, Zerodha, Dhan, Angel One with zero strategy code changes |

---

## 📂 Git & Version Control

Your forked repository is actively connected to your GitHub remote:
```bash
cd /root/BatmanStrategy/openalgo
git remote -v
# origin  https://github.com/pavansn2510/openalgo.git
```
You can commit and push your custom strategy files and configurations to your fork at any time.
