#!/bin/bash

youtube-dl --add-metadata -i -o '%(title)s.%(ext)s' -x -f bestaudio/best $1
