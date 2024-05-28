#!/bin/bash

youtube-dl --add-metadata --embed-subs -i -o '[%(uploader)s] %(title)s.%(ext)s' $1
