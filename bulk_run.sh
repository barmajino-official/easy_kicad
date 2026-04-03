#!/bin/bash

# Default categories to mirror if not provided via environment variable
CATEGORIES=${CATEGORIES:-"esp resistor transistor microcontroller can_bus regulator led optocoupler"}

echo "🚀 Starting Master Mirroring Engine..."
echo "📂 Target Categories: $CATEGORIES"

# Loop through each category
for cat in $CATEGORIES; do
    echo "------------------------------------------------------------"
    echo "⚡ Processing: $cat"
    echo "------------------------------------------------------------"
    
    # Run the module correctly using the package name from /opt/easy_kicad_app
    python3 -m easy_kicad --match="$cat" --full --db "/app/database/easy_kicad_catalog.db" --output "/app/outputFile"
done

echo "✅ All categories finished mirroring!"
