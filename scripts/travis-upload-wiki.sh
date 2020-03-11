#!/usr/bin/env bash

set -e # Exit with nonzero exit code if anything fails

# Exit safely when this build is a pull request
if [ $TRAVIS_PULL_REQUEST != false ]; then
	echo "Do not upload a pull request to wikies"
	exit 0
fi

PROJECT_TITLE=`basename $(readlink -f .)`
TARGET="/var/www/html/wiki/$PROJECT_TITLE/$TRAVIS_BRANCH"
SCP_TARGET="wiki@carrene.com:$TARGET"

SSH_ARGS="-itravis-wiki_rsa -oStrictHostKeyChecking=no"
SSH="ssh -p7346 $SSH_ARGS wiki@carrene.com"
SCP="scp -P7346 $SSH_ARGS"


$SSH "rm -rf $TARGET"
$SSH "mkdir -p $TARGET"
$SCP -r data/markdown/*.md "$SCP_TARGET"

