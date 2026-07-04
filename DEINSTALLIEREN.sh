#!/bin/bash
set -e

rm -f "$HOME/.local/share/applications/KStickFix.desktop"
rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/kstickfix.png"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" || true
fi

echo "KStickFix wurde aus dem KDE-Anwendungsmenü entfernt."
