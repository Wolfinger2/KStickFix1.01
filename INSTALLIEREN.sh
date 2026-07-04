#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

DESKTOP_FILE="$HOME/.local/share/applications/KStickFix.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
ICON_FILE="$ICON_DIR/kstickfix.png"

mkdir -p "$HOME/.local/share/applications"
mkdir -p "$ICON_DIR"

chmod +x "$SCRIPT_DIR/start.sh"
chmod +x "$SCRIPT_DIR/DEINSTALLIEREN.sh" 2>/dev/null || true

if [ -f "$SCRIPT_DIR/icons/kstickfix.png" ]; then
    cp "$SCRIPT_DIR/icons/kstickfix.png" "$ICON_FILE"
fi

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=KStickFix
GenericName=USB-Werkzeugkasten
Comment=USB-Sticks analysieren und wiederherstellen
Exec=$SCRIPT_DIR/start.sh
Icon=kstickfix
Terminal=false
Categories=Utility;System;Filesystem;
Keywords=USB;Stick;ISO;Formatieren;KDE;Linux;
StartupNotify=true
EOF

chmod +x "$DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" || true
fi

echo "KStickFix wurde ins KDE-Anwendungsmenü eingetragen."
