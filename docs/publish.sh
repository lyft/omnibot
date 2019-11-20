#!/bin/bash

# This is run on every commit that travis picks up. It assumes that docs have already been built
# via docs/build.sh. The push behavior differs depending on the nature of the commit:
# * Tag commit (e.g. v1.6.0): pushes docs to versioned location, e.g.
#   https://lyft.github.io/omnibot/docs/v1.6.0/.
# * Master commit: pushes docs to https://lyft.github.io/omnibot/docs/latest/.
# * Otherwise: noop.
#
# This publish script is based on work from https://github.com/envoyproxy/envoy/blob/master/docs/publish.sh

set -e

CHECKOUT_DIR=../omnibot-docs
BUILD_SHA=`git rev-parse HEAD`

if [ -n "$TRAVIS_TAG" ]
then
  PUBLISH_DIR="$CHECKOUT_DIR"/docs/omnibot/"$TRAVIS_TAG"
elif [ -z "$TRAVIS_PULL_REQUEST" ] && [ "$TRAVIS_BRANCH" == "master" ]
then
  PUBLISH_DIR="$CHECKOUT_DIR"/docs/omnibot/latest
else
  echo "Ignoring docs push"
  exit 0
fi

git checkout -B gh-pages
git rm -r .
cp -r generated/docs/. .
rm -rf generated

git config user.name "omnibot-docs(travis)"
git config user.email omnibot-docs@users.noreply.github.com
echo 'add'
git add .
echo 'commit'
git commit -m "docs omnibot@$BUILD_SHA"
echo 'push'
git push origin gh-pages
git checkout master
