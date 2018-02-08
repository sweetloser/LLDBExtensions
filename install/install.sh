#!/bin/sh

USERNAME="${SUDO_USER-$USER}"
USERPATH=`eval echo ~$USERNAME`

LLDBINIT_PATH="${USERPATH}/.lldbinit"

INSTALL_PATH="${USERPATH}/SL_lldbExtensions"

PROJECT_PATH="../"

PYFILE_PATH="${PROJECT_PATH}/SL_lldbExtensions"

echo "用户目录：$USERPATH"

echo "copy file to ${INSTALL_PATH}"

rm -rf "${INSTALL_PATH}" || true

mkdir "${INSTALL_PATH}" || true

cp -rf "${PYFILE_PATH}/" "${INSTALL_PATH}"

echo "write import command to \`${LLDBINIT_PATH}\` file"

importStr="\n\n###\tSL_lldbExtensions\t###\n\ncommand script import "
echo "${importStr}${INSTALL_PATH}/lldbExtension.py" >> "${LLDBINIT_PATH}"

