#!/usr/bin/env bash
#
# Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

myshuf() {
  perl -MList::Util=shuffle -e 'print shuffle(<>);' "$@";
}

normalize_text() {
  tr '[:upper:]' '[:lower:]' | \
    sed -e "s/'/ ' /g" -e 's/"//g' -e 's/\./ \. /g' -e 's/<br \/>/ /g' \
        -e 's/,/ , /g' -e 's/(/ ( /g' -e 's/)/ ) /g' -e 's/\!/ \! /g' \
        -e 's/\?/ \? /g' -e 's/\;/ /g' -e 's/\:/ /g' | tr -s " " | myshuf
}

# modify these
BINDIR=/Users/udi/Documents/dev/learn/fastText/fastText
DATAFILE=tagged_web_pages
TRAIN_SIZE=50000
VALID_SIZE=9212

RESULTDIR=result
DATADIR=data

mkdir -p "${RESULTDIR}"
mkdir -p "${DATADIR}"

if [ ! -f "${DATADIR}/${DATAFILE}.train" ]
then
  # modify these lines obtaining the source dataset
  #wget -c "https://github.com/le-scientifique/torchDatasets/raw/master/dbpedia_csv.tar.gz" -O "${DATADIR}/dbpedia_csv.tar.gz"
  #tar -xzvf "${DATADIR}/dbpedia_csv.tar.gz" -C "${DATADIR}"

  head -n ${TRAIN_SIZE} ${DATAFILE}.train > ${DATADIR}/${DATAFILE}-train.csv
  tail -n ${VALID_SIZE} ${DATAFILE}.train > ${DATADIR}/${DATAFILE}-test.csv
  cat "${DATADIR}/${DATAFILE}-train.csv" | normalize_text > "${DATADIR}/${DATAFILE}.train"
  cat "${DATADIR}/${DATAFILE}-test.csv" | normalize_text > "${DATADIR}/${DATAFILE}.test"
fi

#make

${BINDIR}/fasttext supervised -input "${DATADIR}/${DATAFILE}.train" -output "${RESULTDIR}/${DATAFILE}" -dim 300 -lr 1.0 -wordNgrams 3 -minCount 1 -bucket 10000000 -epoch 100 -thread 4

${BINDIR}/fasttext test "${RESULTDIR}/${DATAFILE}.bin" "${DATADIR}/${DATAFILE}.test"

${BINDIR}/fasttext predict "${RESULTDIR}/${DATAFILE}.bin" "${DATADIR}/${DATAFILE}.test" > "${RESULTDIR}/${DATAFILE}.test.predict"
