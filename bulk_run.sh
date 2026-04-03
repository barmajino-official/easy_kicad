#!/bin/bash

# Default categories to mirror if not provided via environment variable
CATEGORIES=${CATEGORIES:-"esp resistor transistor microcontroller can_bus regulator led optocoupler"}

echo "🚀 Starting Master Mirroring Engine..."
echo "📂 Target Categories: $CATEGORIES"

for cat in $CATEGORIES; do
    echo "------------------------------------------------------------"
    echo "⚡ Processing: $cat"
    echo "------------------------------------------------------------"
    python3 -m easy_kicad --match="$cat" --full
done

echo "✅ All categories finished mirroring!"
