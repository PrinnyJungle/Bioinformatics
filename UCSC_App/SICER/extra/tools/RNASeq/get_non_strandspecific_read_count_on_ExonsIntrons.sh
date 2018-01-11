#!/bin/bash

EXEDIR=/home/data/SICER1.1/SICER/extra/tools/RNASeq

#READSDIR=/home/data/hg19/JunZhu/raw/CD4/Round2
READSDIR=/home/data/hg19/JunZhu/new_K36
READS=test
READFILE=$READS.bed

FRAGMENTSIZE=150

ANNOTATIONDIR=/home/data/hg19/Annotation/NewVersion
ANNOTATION=hg19_EntrezID_filtered_samestrand_collisonremoved.pkl 

OUTFILE=$READS-on-EligibleEntrezGenes.dat

echo "python $EXEDIR/get_non_strandspecific_read_count_on_ExonsIntrons.py -r $READSDIR/$READFILE -g $FRAGMENTSIZE -u $ANNOTATIONDIR/$ANNOTATION -o $OUTFILE -s hg19 "
python $EXEDIR/get_non_strandspecific_read_count_on_ExonsIntrons.py -r $READSDIR/$READFILE -g $FRAGMENTSIZE -u $ANNOTATIONDIR/$ANNOTATION -o $OUTFILE -s hg19 


echo "sort -g -k1 $OUTFILE > $READS-on-EligibleEntrezGenes_sorted.dat"
sort -g -k1 $OUTFILE > $READS-on-EligibleEntrezGenes_sorted.dat
echo "mv $READS-on-EligibleEntrezGenes_sorted.dat  $OUTFILE"
mv $READS-on-EligibleEntrezGenes_sorted.dat  $OUTFILE

echo ""
echo ""


