#!/bin/bash
# Authors: Weiqun Peng
#
# Comments and/or additions are welcome (send e-mail to:
# wpeng@gwu.edu).


##############################################################
# ##### Please replace PATHTO with your own directory ###### #
##############################################################

SICER=/home/data/SICER1.1/SICER
PYTHONPATH=$SICER/lib
export PYTHONPATH

LIBA=72h_EM_K27
UCSCDIR=/home/data/hg18/CD8
UCSCFILE=hg18-Agilent-19554-genes.ucsc

READDIR=/home/data/hg18/CD8/2010data/processed
READFILE=$LIBA-W200-G600-E500-islandfiltered.bed 

EXEDIR=/home/data/SICER1.1/SICER/extra
EXE=GenerateProfileAroundLocations.py

TYPE=TSS
NORMALIZATION=1
SPECIES=hg18
UPSTREAM=5000
DOWNSTREAM=5000
RESOLUTION=5
WINDOWSIZE=100
OUTFILE=${LIBA}_on_${TYPE}_R${RESOLUTION}_W$WINDOWSIZE.txt

echo "python $EXEDIR/$EXE  -k $UCSCDIR/$UCSCFILE -b $READDIR/$READFILE -c $TYPE -o $OUTFILE -n $NORMALIZATION -s $SPECIES -u $UPSTREAM -d $DOWNSTREAM -r $RESOLUTION -w $WINDOWSIZE"

python $EXEDIR/$EXE  -k $UCSCDIR/$UCSCFILE -b $READDIR/$READFILE -c $TYPE -o $OUTFILE -n $NORMALIZATION -s $SPECIES -u $UPSTREAM -d $DOWNSTREAM -r $RESOLUTION -w $WINDOWSIZE


OURFILECZ=${LIBA}_on_${TYPE}_CZ.txt


