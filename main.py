#!/usr/bin/env python3
"EdgeVoice -- Microsoft Edge TTS desktop GUI built with Flet."

import os
import sys
import certifi

import flet as ft

from app.app import main

# Point SSL to the bundled certifi bundle when frozen
if getattr(sys, "frozen", False):
    os.environ["SSL_CERT_FILE"] = os.path.join(sys._MEIPASS, "certifi", "cacert.pem")
    os.environ["REQUESTS_CA_BUNDLE"] = os.environ["SSL_CERT_FILE"]

if __name__ == "__main__":
    ft.run(main)
