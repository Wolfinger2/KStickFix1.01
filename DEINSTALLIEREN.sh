#!/bin/bash
set -e

DESKTOP_FILE="$HOME/.local/share/applications/KStickFix.desktop"
ICON_FILE="$HOME/.local/share/icons/hicolor/256x256/apps/kstickfix.png"

rm -f "$DESKTOP_FILE"
rm -f "$ICON_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" || true
fi

echo "KStickFix wurde aus dem KDE-Anwendungsmenü entfernt."
echo "Der Projektordner selbst wurde nicht gelöscht."
