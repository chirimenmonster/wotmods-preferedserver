#! /bin/bash

MODBASE=scripts/client/gui/mods
MODNAME=chirimen.preferedserver_0.2

rm -r tmp

python2 -m compileall -d $MODBASE mods

mkdir -p tmp/res/$MODBASE
( cd mods; find . -name '*.pyc' -exec mv {} ../tmp/res/$MODBASE/{} \; )
( cd tmp; zip -0r $MODNAME.wotmod res )
