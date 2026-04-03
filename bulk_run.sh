#!/bin/bash

# Default categories
CATEGORIES=${CATEGORIES:-"esp resistor transistor microcontroller can_bus regulator led optocoupler"}

echo "🚀 Starting Master Mirroring Engine..."
echo "📂 Target Categories: $CATEGORIES"

# Loop through each category
for cat in $CATEGORIES; do
    echo "------------------------------------------------------------"
    echo "⚡ Processing: $cat"
    echo "------------------------------------------------------------"
    
    # Run the installed package correctly
    python3 -m easy_kicad --match="$cat" --full --db "/app/database/easy_kicad_catalog.db" --output "/app/outputFile"
done

echo "✅ All categories finished mirroring!"
