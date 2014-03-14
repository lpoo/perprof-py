#!/bin/bash

[ -x perprof ] && echo "perprof not installed or I could not find it" && exit 1

lang=en
case $1 in
  -l | --lang )
    case $2 in
      en | pt_BR )
        lang=$2
        ;;
      *)
        echo "Unrecognized language $2. Choose from {en, pt_BR}."
        exit 1
        ;;
    esac
    ;;
  *)
    ;;
esac

rm -rf plots
mkdir -p plots

args="-l $lang"

for backend in --tikz --mp
do
  perprof $backend $args alpha.table beta.table -o plots/ab
  perprof $backend $args *.table -o plots/abc
  perprof $backend $args alpha.table beta.table --semilog -o plots/ab-semilog
  perprof $backend $args *.table --semilog -o plots/abc-semilog
done