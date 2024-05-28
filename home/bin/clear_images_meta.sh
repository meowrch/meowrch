#!/bin/bash

for i in *; do mat2 --inplace "$i" && echo Delete MetaData [$i]; done
