# Bloomhash

##Introduction
Bloomhash allows you to instantly check if a hash can _not_ be created using a specific wordlist. The chance of false positives is about 1/3'rd, but the chance for false negatives is zero. The purpose of bloomhash is providing information about wordlists that can be skipped when cracking hashes.

What does this mean? It means that if the lookup tells you that a word might be contained in the wordlist, it's useless. But if the result is negative (hash cannot be created), it's not possible that the wordlist can create the hash. This lookup can be done instantly. 

[bloomhash.com link](http://www.bloomhash.com)

Bloomhash is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License.