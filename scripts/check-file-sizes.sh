#!/bin/bash
# Check for god objects (files >500 LOC)

echo "=== Frontend Files >500 LOC ==="
find atlantis-ui/src -name "*.tsx" -o -name "*.ts" | while read file; do
  lines=$(wc -l < "$file")
  if [ "$lines" -gt 500 ]; then
    echo "$file: $lines LOC"
  fi
done

echo ""
echo "=== Backend Files >500 LOC ==="
find backend/src -name "*.ts" | while read file; do
  lines=$(wc -l < "$file")
  if [ "$lines" -gt 500 ]; then
    echo "$file: $lines LOC"
  fi
done
