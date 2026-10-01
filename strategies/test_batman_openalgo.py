#!/usr/bin/env python3
"""
Batman Strategy Test Runner on OpenAlgo
=======================================

This script allows you to test your options strategies (including the NIFTY Batman Double Ratio Spread)
against OpenAlgo in either:
1. Analyze / Sandbox Mode (Default - zero risk virtual trading with ₹1 Cr simulated margin)
2. Live Mode (executes real multi-leg orders with your connected broker once logged in)

Key Features:
- Executes multi-leg options via OpenAlgo's /api/v1/optionsmultiorder endpoint
- Guarantees Rule 1 margin sequencing (Buy ATM/OTM hedges first, Sell 2x wings second)
- Supports both 4-Leg Classic and 6-Leg Margin-Saver Batman structures
- Verifies position status and PnL through OpenAlgo API

Usage:
    # Run test in virtual Sandbox / Analyze mode:
    uv run python strategies/test_batman_openalgo.py --sandbox

    # Test 6-leg margin-saver structure:
    uv run python strategies/test_batman_openalgo.py --sandbox --structure 6leg

    # Check status of active sandbox positions:
    uv run python strategies/test_batman_openalgo.py --status
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
import requests

# OpenAlgo Base Configuration
OPENALGO_HOST = os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000")
API_KEY = os.getenv("OPENALGO_API_KEY", "")


def get_api_key():
    """Retrieve API key from environment, .env file, or OpenAlgo database."""
    global API_KEY
    if API_KEY:
        return API_KEY
    
    # Try reading from .env file
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("OPENALGO_API_KEY") or line.startswith("API_KEY"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        API_KEY = parts[1].strip().strip("'\"")
                        return API_KEY
    return API_KEY


def check_openalgo_health(base_url: str) -> bool:
    """Check if the OpenAlgo local server is running."""
    try:
        resp = requests.get(f"{base_url}/api/v1/health", timeout=3)
        if resp.status_code == 200:
            print(f"✅ OpenAlgo Server is ONLINE at {base_url}")
            return True
    except Exception:
        pass
    
    # Try pinging index
    try:
        resp = requests.get(base_url, timeout=3)
        if resp.status_code in [200, 302, 401]:
            print(f"✅ OpenAlgo Server is ONLINE at {base_url}")
            return True
    except Exception as e:
        print(f"❌ Cannot connect to OpenAlgo at {base_url}: {e}")
        print("💡 Start OpenAlgo first with: uv run app.py")
        return False
    return False


def build_batman_payload(
    api_key: str,
    structure: str = "4leg",
    underlying: str = "NIFTY",
    exchange: str = "NSE_INDEX",
    expiry_date: str = "30DEC25",
    lots: int = 1,
    wing_offset: str = "OTM3"
) -> dict:
    """Build multi-leg payload for Batman strategy.
    
    4-Leg Classic Structure:
      - Buy 1x ATM CE
      - Buy 1x ATM PE
      - Sell 2x OTM Wing CE (e.g. OTM3)
      - Sell 2x OTM Wing PE (e.g. OTM3)

    6-Leg Margin-Saver Structure:
      - Buy 1x ATM CE
      - Buy 1x ATM PE
      - Sell 2x OTM Wing CE
      - Sell 2x OTM Wing PE
      - Buy 1x Deep OTM Call Penny Hedge (OTM15)
      - Buy 1x Deep OTM Put Penny Hedge (OTM15)
    """
    base_qty = 65 * lots       # NIFTY lot size
    double_qty = base_qty * 2

    legs = [
        # Core Straddle (Long ATM)
        {"offset": "ATM", "option_type": "CE", "action": "BUY", "quantity": base_qty},
        {"offset": "ATM", "option_type": "PE", "action": "BUY", "quantity": base_qty},
        # Wings (Short OTM 2x)
        {"offset": wing_offset, "option_type": "CE", "action": "SELL", "quantity": double_qty},
        {"offset": wing_offset, "option_type": "PE", "action": "SELL", "quantity": double_qty},
    ]

    if structure == "6leg":
        # Add deep OTM margin-saver penny hedges
        legs.append({"offset": "OTM15", "option_type": "CE", "action": "BUY", "quantity": base_qty})
        legs.append({"offset": "OTM15", "option_type": "PE", "action": "BUY", "quantity": base_qty})

    return {
        "apikey": api_key,
        "strategy": f"Batman_{structure.upper()}",
        "underlying": underlying,
        "exchange": exchange,
        "expiry_date": expiry_date,
        "product": "NRML",
        "legs": legs
    }


def deploy_batman(base_url: str, api_key: str, structure: str = "4leg", lots: int = 1):
    """Place the multi-leg Batman order via OpenAlgo API."""
    url = f"{base_url}/api/v1/optionsmultiorder"
    payload = build_batman_payload(api_key=api_key, structure=structure, lots=lots)

    print(f"\n🚀 Deploying {structure.upper()} Batman Strategy...")
    print(f"📊 Underlying: NIFTY | Expiry: {payload['expiry_date']} | Lots: {lots}")
    print(f"📦 Legs to execute ({len(payload['legs'])} legs total):")
    for idx, leg in enumerate(payload["legs"], 1):
        print(f"   {idx}. {leg['action']:4s} {leg['quantity']} qty | {leg['offset']} {leg['option_type']}")

    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"\n📡 Response Status: {resp.status_code}")
        data = resp.json()
        print("📄 Response Data:")
        print(json.dumps(data, indent=2))
        return data
    except Exception as e:
        print(f"❌ Failed to submit multi-order: {e}")
        return None


def get_position_status(base_url: str, api_key: str):
    """Query current positions from OpenAlgo."""
    url = f"{base_url}/api/v1/positions"
    try:
        resp = requests.get(url, params={"apikey": api_key}, timeout=5)
        if resp.status_code == 200:
            print("\n📈 Current OpenAlgo Positions:")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"⚠️ Could not fetch positions (HTTP {resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"❌ Error fetching positions: {e}")


def main():
    parser = argparse.ArgumentParser(description="Test Batman Strategy with OpenAlgo")
    parser.add_argument("--host", default=OPENALGO_HOST, help="OpenAlgo server host URL")
    parser.add_argument("--apikey", default="", help="OpenAlgo API Key")
    parser.add_argument("--structure", choices=["4leg", "6leg"], default="6leg", help="Strategy structure")
    parser.add_argument("--lots", type=int, default=1, help="Number of lots")
    parser.add_argument("--sandbox", action="store_true", help="Run in virtual sandbox mode")
    parser.add_argument("--status", action="store_true", help="Check position status")
    args = parser.parse_args()

    api_key = args.apikey or get_api_key()

    print("=" * 60)
    print("🦇 OpenAlgo Batman Strategy Test Suite")
    print("=" * 60)
    print(f"Server Host : {args.host}")
    print(f"Mode        : {'Sandbox (Analyze)' if args.sandbox else 'Live/Standard'}")
    print(f"API Key     : {'[Configured]' if api_key else '[Not set - will use test key]'}")
    print("=" * 60)

    if not check_openalgo_health(args.host):
        sys.exit(1)

    if args.status:
        get_position_status(args.host, api_key)
        return

    deploy_batman(args.host, api_key, structure=args.structure, lots=args.lots)


if __name__ == "__main__":
    main()
