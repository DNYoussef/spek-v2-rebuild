#!/bin/bash
# Resume DSPy Training After Groq Rate Limit Reset
# Wait for rate limit to reset, then retry training

echo "========================================"
echo "Waiting for Groq Rate Limit Reset"
echo "========================================"
echo ""
echo "Current time: $(date)"
echo "Groq resets at: ~22:08 PST (17 minutes from 21:50)"
echo ""
echo "Sleeping for 20 minutes to ensure reset..."
sleep 1200  # 20 minutes

echo ""
echo "========================================"
echo "Resuming Training..."
echo "========================================"
echo ""

cd "C:\Users\17175\Desktop\spek-v2-rebuild"
python scripts/train_missing_with_groq.py

echo ""
echo "Training complete!"
echo "Check models/dspy/ for trained optimizers"
