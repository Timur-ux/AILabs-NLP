#!/usr/bin/env bash

nGood=10
nBad=10
datasetFile="./dataset/spam_or_not_spam.csv"
outputFile="./processOutput.json"

usage() {
	echo "Usage: $0 <url> [OPTIONS]"
	echo "-h -- show this message and exit"
	echo "-g <number> -- set number of good(not spam) messages"
	echo -e "\tdefault: $nGood"
	echo "-b <number> -- set number of bad(spam) messages"
	echo -e "\tdefault: $nBad"
	echo "-f <filepath> -- set outputFile"
	echo -e "\tdefault: $outputFile"
}

if [[ $# < 1 ]]; then
	usage
	exit 1
fi

url=$1
shift

while [[ $# > 0 ]]; do
	case "$1" in
		-h) 
			usage
			exit 0
			;;
		-g)
			if [[ $# < 2 ]]; then
				echo "Argument required: -g"
				exit 1
			fi
			nGood=$2
			shift
			;;
		-b)
			if [[ $# < 2 ]]; then
				echo "Argument required: -b"
				exit 1
			fi
			nBad=$2
			shift
			;;
		-f)
			if [[ $# < 2 ]]; then
				echo "Argument required: -b"
				exit 1
			fi
			outputFile="$2"
			shift
			;;
		*)
			echo "Undefined option: $1"
			exit 1
			;;
	esac
	shift
done

if [[ ! -f "$datasetFile" ]]; then
	echo "Unzipped dataset not found, so i unzip it"
	unzip "$datasetFile".zip -d ./dataset/
	echo "Done"
fi

badMessages=$(grep -E ",1$" "$datasetFile" | head -n $nBad | sed 's/,1//')
goodMessages=$(grep -E ",0$" "$datasetFile" | head -n $nGood | sed 's/,0//')

messages="$(echo -e "$badMessages\n$goodMessages" | shuf)"

echo -e "$messages" | while read line; do
	if [[ -z "$line" ]]; then
		continue
	fi
	isSpam=0
	if [[ ! -z $(echo "$badMessages" | grep "$line") ]]; then
		isSpam=1
	fi

	requestBody="$(echo "$line" | jq -R '{message: .}')"
	responseBody="$(curl -X 'POST' -H 'Content-Type:application/json' "$url" -d "$requestBody" 2>/dev/null)"
	response="$(echo "$responseBody" | sed 's/.\(.*\)./\1/' | sed 's/\\"\(verdict\|reasoning\)\\"/"\1"/g' | sed 's/": \\"/": "/' | sed 's/\\"\}/"\}/' | sed 's/\[\\"/\["/g' | sed 's/\\"\]/"\]/g' | sed 's/\\", \\"/", "/g')"
	verdict=$(echo "$response" | jq '.verdict')
	if [[ "$?" != 0 ]]; then
		echo "Invalid response. Skip. Response: $response"
	fi
	isVerdictCorrect=0
	if [[ "$verdict" == "$isSpam" ]]; then
		isVerdictCorrect=1
	fi
	echo "$response" | jq -c "{ verdict: .verdict, isSpam: $isSpam, isVerdictCorrect: $isVerdictCorrect, message: \"$line\", reasoning: .reasoning}" >> "$outputFile"
done
