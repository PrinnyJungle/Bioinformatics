#!/bin/bash
# 
PATHTO=/home/data/SICER1.1
SICER=$PATHTO/SICER
PYTHONPATH=$SICER/lib
export PYTHONPATH

SPECIES=$1
SAMPLEBED=$2
REDUNDANCYTHRESHOLD=$3
FILTEREDSAMPLEBED=$4

echo "python $SICER/src/remove_redundant_reads.py -s $SPECIES -b $SAMPLEBED -t $REDUNDANCYTHRESHOLD -o $FILTEREDSAMPLEBED"
python $SICER/src/remove_redundant_reads.py -s $SPECIES -b $SAMPLEBED -t $REDUNDANCYTHRESHOLD -o $FILTEREDSAMPLEBED