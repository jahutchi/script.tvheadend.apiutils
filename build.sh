#!/bin/bash
OLDPWD=${PWD}
BASEDIR=$(dirname "$0")
OUTDIR=${BASEDIR}/releases
cd ${BASEDIR}

SRC=./script.tvheadend.apiutils
ADDONXML=${SRC}/addon.xml
VERSION=$(grep "<addon id=\"script.tvheadend.apiutils\" name=\"Tvheadend API Utilities\" version=" ${ADDONXML} | sed 's/.*version=\"\([[:digit:]\|\.]*\).*/\1/')
ZIPFILE=${OUTDIR}/script.tvheadend.apiutils-${VERSION}.zip
ZIPFILE_LATEST=${OUTDIR}/script.tvheadend.apiutils-latest.zip
mkdir ${OUTDIR} >/dev/null 2>&1
rm -f ${ZIPFILE}
zip -r ${ZIPFILE} ${SRC}
cp ${ZIPFILE} ${ZIPFILE_LATEST}

cd ${OLDPWD}

