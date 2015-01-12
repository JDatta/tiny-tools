#!/bin/bash

#
# Given a top lavel lib directory containing many java jar files,
# This script interactively searches the jar files within it for a
# particular class. Both class name and FQDN can be used.
#
 
ECHO="echo"
FIND="find"
EXIT="exit"
GREP=grep

function _GREEN {
  ${ECHO} -en "\e[1m\e[32m${1}\e[0m"
}

JAR=`which jar`
if [ -z ${JAR} ]; then
  if [ ! -z ${JAVA_HOME} ]; then
    JAR=${JAVA_HOME}/bin/jar
  else
    ${ECHO} "Could not find JAR utility in path and JAVA_HOME is not set. Exiting."
    ${EXIT} 1
  fi
fi

if [ ! -x ${JAR} ]; then
  ${ECHO} "Could not execute JAR command. Exiting."
  ${EXIT} 1
fi

if [ $# != 2 ]; then
  ${ECHO} "Usage: find-jar.sh <top-level-dir> <Class name>"
  ${EXIT} 1
fi

IFS=$(${ECHO} -en "\n\b") # Set the field separator newline

for f in `find ${1} -iname *.jar`; do
  ${JAR} -tf ${f}| ${GREP} --color $2
  if [ $? == 0 ]; then
    _GREEN "Match found: "
    ${ECHO} -e "${f}\n"
  fi
done


