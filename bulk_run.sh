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
    
    # Run the flattened script directly from the root
    python3 __main__.py --match="$cat" --full --db "/app/database/easy_kicad_catalog.db" --output "/app/outputFile"
done

echo "✅ All categories finished mirroring!"
