#!/bin/bash

EXEDIR=/home/data/hg19/JunZhu/modules

READSDIR=/home/data/SICER1.1/SICER/extra/tools/RNASeq/test

for READS in Rest_R1_n100000_unique 
do
READFILEF=${READS}_P.bed
READFILER=${READS}_N.bed
FRAGMENTSIZE=0

ANNOTATIONDIR=/home/data/hg19/Annotation
# old choice: lost many ids because of the 3UTR requirement
#ANNOTATION=refFlat_hg19_EntrezID_filtered.pkl
# new choice:
#ANNOTATION=refFlat_hg19_EntrezID_filtered_samestrand_collisonremoved.pkl
ANNOTATION=hg19_EntrezID_filtered_samestrand_collisonremoved.pkl


OUTFILE=$READS-on-EligibleEntrezGenes_old.dat

echo "python $EXEDIR/get_read_count_on_ExonsIntrons.py -f $READSDIR/$READFILEF -r $READSDIR/$READFILER -g $FRAGMENTSIZE -u $ANNOTATIONDIR/$ANNOTATION -o $OUTFILE -s hg19 "
python $EXEDIR/get_read_count_on_ExonsIntrons.py -f $READSDIR/$READFILEF -r $READSDIR/$READFILER -g $FRAGMENTSIZE -u $ANNOTATIONDIR/$ANNOTATION -o $OUTFILE -s hg19


# echo "sort -g -k1 $OUTFILE > $READS-on-EligibleEntrezGenes_sorted.dat"
# sort -g -k1 $OUTFILE > $READS-on-EligibleEntrezGenes_sorted.dat
# echo "mv $READS-on-EligibleEntrezGenes_sorted.dat > $OUTFILE"
# mv $READS-on-EligibleEntrezGenes_sorted.dat > $OUTFILE
# 
# echo ""
# echo ""
# 
done
# 
# # join resting and activated
# exedir=/home/data/SICER1.1/SICER/extra
# python $exedir/join.py -a Rest_R1_unique-on-EligibleEntrezGenes.dat -b Active_R1_unique-on-EligibleEntrezGenes.dat -c 0 -d 0 -o RNASeq-RestingCD4-ActivatedCD4-on-EligibleUniqEntrezGenes_raw.dat 
# 
# 
# # sort according to entrez_id
# sort -g -k 1 RNASeq-RestingCD4-ActivatedCD4-on-EligibleUniqEntrezGenes_raw.dat > RNASeq-RestingCD4-ActivatedCD4-on-EligibleUniqEntrezGenes_raw_sorted.dat
# mv RNASeq-RestingCD4-ActivatedCD4-on-EligibleUniqEntrezGenes_raw_sorted.dat RNASeq-RestingCD4-ActivatedCD4-on-EligibleUniqEntrezGenes_raw.dat

# select and reorder the columns
# Previous: 
# Entrez ID	 Merged Exon Read Count 	 Merged Exon Length 	 Merged Exon RPKM 	 Shared Exon Read Count 	  Shared Exon Length 	 Shared Exon RPKM 	 Shared Intron Read Count 	 Share Intron Length 	 Shared Intron RPKM 	 RefSeq IDs 	 Gene Symbols 
# Merged Exon Read Count 	 Merged Exon Length 	 Merged Exon RPKM 	 Shared Exon Read Count 	  Shared Exon Length 	 Shared Exon RPKM 	 Shared Intron Read Count 	 Share Intron Length 	 Shared Intron RPKM 	 RefSeq IDs 	 Gene Symbols

# New: Entrez ID 	 R Merged Exon Read Count	 A Merged Exon Read Count	R Merged Exon RPKM	A Merged Exon RPKM	Merged Exon Length	R Shared Exon Read Count	 A Shared Exon Read Count	R Shared Exon RPKM	A Shared Exon RPKM	Shared Exon Length	R Shared Intron Read Count	R Shared Intron Read Count	R Shared Intron RPKM	A Shared Intron RPKM	Share Intron Length 	 RefSeq IDs 	 Gene Symbols

awk ' { print $1 "\t" $2 "\t" $13 "\t" $4 "\t" $15 "\t" $3 "\t" $5 "\t" $16 "\t" $7 "\t" $18 "\t" $6 "\t" $8 "\t" $19 "\t" $10 "\t" $21 "\t" $9  "\t" $11 "\t" $12 ;}'  RNASeq-RestingCD4-ActivatedCD4-on-EligibleUniqEntrezGenes_raw.dat > RNASeq-RestingCD4-ActivatedCD4-on-EligibleUniqEntrezGenes.dat