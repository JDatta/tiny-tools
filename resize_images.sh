#!/bin/bash

#
# Given a top lavel lib directory containing many java jar files,
# This script interactively searches the jar files within it for a
# particular class. Both class name and FQDN can be used.
#
 
function _GREEN {
  echo -en "\e[1m\e[32m${1}\e[0m"
}

function _BLUE {
  echo -en "\e[1m\e[34m${1}\e[0m"
}

if [ $# != 2 ]; then
  echo "Usage: $0 <top-level-dir> <target_dir>"
  exit 1
fi

mkdir $2

IFS=$(echo -en "\n\b") # Set the field separator newline

for f in `find  $1 -type f -iname '*.jpg'`; do
  DIR=`dirname $f`
  mkdir -p $2/$DIR
  _BLUE "Converting: "
  echo -en "${f}\n"

  convert -resize 1920x1080  $f $2/$f
  if [ $? == 0 ]; then
    _GREEN "Converted: "
    echo -en "${f}\n"
  fi
done


