#!/bin/bash

set -eo pipefail

NAME=$1

if [[ ! $NAME =~ ^mythril2/myth2(-dev)?$ ]]; then
    echo "Error: unknown image name: $NAME" >&2
    exit 1
fi

if [ -n "$CIRCLE_TAG" ]; then
    GIT_VERSION=${CIRCLE_TAG#?}
else
    GIT_VERSION=${CIRCLE_SHA1}
fi

export DOCKER_BUILDKIT=1
docker buildx create --use

# Build and test all versions of the image. (The result will stay in the cache,
# so the next build should be almost instant.)
docker buildx bake myth2-smoke-test

if [ -z "$DOCKERHUB_USERNAME" ]; then
    echo "Finishing without pushing to dockerhub"
    exit 0
fi

echo "$DOCKERHUB_PASSWORD" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

# strip mythril2/ from NAME, e.g. myth2 or myth2-dev
BAKE_TARGET="${NAME#mythril2/}"

VERSION="${GIT_VERSION:?},latest" docker buildx bake --push "${BAKE_TARGET:?}"
