#!/usr/bin/env bash

if [[ $# < 1 ]]; then
	echo "Usage: $0 <json file with data>"
	exit 1
fi

file="$1"

TP=$(cat "$file" | jq 'select(.verdict==1 and .isSpam == 1) | .verdict' | wc -l)
TN=$(cat "$file" | jq 'select(.verdict==0 and .isSpam == 0) | .verdict' | wc -l)
FP=$(cat "$file" | jq 'select(.verdict==0 and .isSpam == 1) | .verdict' | wc -l)
FN=$(cat "$file" | jq 'select(.verdict==1 and .isSpam == 0) | .verdict' | wc -l)


accuracy=$(python -c "print(($TP + $TN)/($TP + $TN + $FN + $FP))")
precision=$(python -c "print($TP/($TP + $TN))")
recall=$(python -c "print($TP/($TP + $FN))")
f1=$(python -c "print(2 * ($precision * $recall)/($precision + $recall))")

echo "accuracy: $accuracy"
echo "precision: $precision"
echo "recall: $recall"
echo "f1: $f1"

