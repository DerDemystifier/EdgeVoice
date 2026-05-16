#!/usr/bin/env python3
"EdgeVoice -- Microsoft Edge TTS desktop GUI built with Flet."

import os
import sys
import certifi

import flet as ft

from app.app import main

# Point SSL to the bundled certifi bundle when frozen. Use getattr to avoid triggering Pylance warnings about undocumented attributes like sys._MEIPASS.
if getattr(sys, "frozen", False):
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidate = os.path.join(meipass, "certifi", "cacert.pem")
        if os.path.exists(candidate):
            os.environ["SSL_CERT_FILE"] = candidate
    # Fallback to certifi where() if we didn't locate a bundled bundle
    if not os.environ.get("SSL_CERT_FILE"):
        os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ["REQUESTS_CA_BUNDLE"] = os.environ["SSL_CERT_FILE"]
else:
    # Not frozen: prefer certifi's bundle for local runs to avoid SSL issues
    os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ.setdefault("REQUESTS_CA_BUNDLE", os.environ["SSL_CERT_FILE"])


if __name__ == "__main__":
    ft.run(main)
