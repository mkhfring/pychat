#!/usr/bin/env bash

# Use this to encrypt files
# $ tar -cf travis-keys.tar travis-wiki_rsa*
# $ travis encrypt-file travis-keys.tar


openssl aes-256-cbc \
    -K $encrypted_79c0f355d5ee_key \
    -iv $encrypted_79c0f355d5ee_iv \
    -in travis-keys.tar.enc \
    -out travis-keys.tar -d

tar -xf travis-keys.tar

chmod 600 travis-wiki_rsa

eval `ssh-agent -s`
ssh-add travis-wiki_rsa

pip3 install -U pip setuptools wheel
pip3 install -r requirements-ci.txt
pip3 install -e .

