#!/usr/bin/zsh

# Necessary to expose conda to this script, but a bit of a lazy and bad
# solution because it loads all plugins and such as well
source ~/.zshrc

conda activate andybot && python ./bot.py 1>> python.output.log 2>> python.errors.log
