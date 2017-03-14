#!/usr/bin/env python3
import rytdl

# Correct layout
print(rytdl.extract_song_details("Deodato - Keep It In The Family (1980)"))
# Em dash
print(rytdl.extract_song_details("Deodato — Keep It In The Family (1980)"))
# Year no parentheses
print(rytdl.extract_song_details("Deodato - Keep It In The Family 1980"))
# No year
print(rytdl.extract_song_details("Deodato - Keep It In The Family"))
# Missing Space
print(rytdl.extract_song_details("Deodato- Keep It In The Family (1980)"))
# Colon instead of hyphen
print(rytdl.extract_song_details("Cookie Monster: Me Lost Me Cookie at the Disco"))