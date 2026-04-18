"""
Script para registrar en cuentas_sociales_mkt los accounts conectados en Zernio.

Usa GET https://api.zernio.com/v1/accounts para obtener las cuentas
y las inserta en la DB asociadas a la marca activa.

Ejecutar desde backend/:
  source venv/bin/activate && python scripts/registrar_cuentas_zernio.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config.settings import get_settings
from integrations.database import SessionLocal
from models.cliente_models import MarcaMkt
from models.social_models import CuentasSocialesMkt


def main():
    settings = get_settings()

    if not settings.ZERNIO_API_KEY:
        print("ERROR: ZERNIO_API_KEY no configurada en .env")
        return

    # 1. Fetch accounts from Zernio
    url = f"{settings.ZERNIO_BASE_URL}/accounts"
    headers = {
        "Authorization": f"Bearer {settings.ZERNIO_API_KEY}",
        "Content-Type": "application/json",
    }

    print(f"Fetching accounts from {url}...")
    resp = requests.get(url, headers=headers, timeout=30)

    if resp.status_code != 200:
        print(f"ERROR: Zernio returned HTTP {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
        return

    data = resp.json()
    accounts = data.get("accounts", [])
    print(f"Found {len(accounts)} accounts in Zernio")

    if not accounts:
        print("No accounts to register.")
        return

    # 2. Get active marca
    db = SessionLocal()
    try:
        marca = db.query(MarcaMkt).filter(MarcaMkt.activa == True).first()  # noqa: E712
        if not marca:
            print("ERROR: No hay marca activa en la DB")
            return

        print(f"Using marca: {marca.nombre} (id={marca.id})")

        # 3. Register each account
        registered = 0
        for acc in accounts:
            platform = acc.get("platform", "unknown").lower()
            zernio_id = acc.get("_id", "")
            display_name = acc.get("displayName") or acc.get("username") or ""
            username = acc.get("username") or ""
            is_active = acc.get("isActive", True) and acc.get("enabled", True)

            # Try to get username from metadata
            meta = acc.get("metadata", {})
            if not username and meta.get("selectedPageUsername"):
                username = meta["selectedPageUsername"]
            if not display_name and meta.get("selectedPageName"):
                display_name = meta["selectedPageName"]

            nombre = username or display_name or f"{platform}-{zernio_id[:8]}"

            # Check if already exists
            existing = db.query(CuentasSocialesMkt).filter(
                CuentasSocialesMkt.marca_id == marca.id,
                CuentasSocialesMkt.red_social == platform,
            ).first()

            if existing:
                print(f"  SKIP: {platform} — {nombre} (ya existe, id={existing.id})")
                continue

            cuenta = CuentasSocialesMkt(
                marca_id=marca.id,
                red_social=platform,
                nombre_cuenta=nombre,
                account_id_externo=zernio_id,
                access_token_encrypted=None,
                activa=is_active,
            )
            db.add(cuenta)
            db.flush()
            registered += 1
            print(f"  OK: {platform} — {nombre} (zernio_id={zernio_id}, activa={is_active})")

        db.commit()
        print(f"\nDone: {registered} cuentas registradas, {len(accounts) - registered} omitidas")

    finally:
        db.close()


if __name__ == "__main__":
    main()
