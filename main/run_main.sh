#!/bin/bash
#set -e	#### Terminating the script if any command exited with a nonzero exit status
set -u	#### prevents the error by aborting the script if a variable’s value is unset
set -o pipefail 	#### check on the p398 of book Bioinformatics Data Skills.

## 
#	nohup bash run_main.sh 1>default.log 2>default_err.log &
########################################################################
## 12/02/2017
## By Xiang Li,
## lux@gwu.edu
## Peng's Lab
## Version.beta
########################################################################

########################################################################
  #  means NEED MODIFICATION. "VERY IMPORTANT INFORMATION"
  ## means Title_level 1.
 ### means Title_level 2.
#### means comment.
########################################################################
echo "Start Date: `date` "
Start_Date=`date`
Process_NAME=${1}


source ./functions.sh
echo "Import functions.sh" 

#			NEED MODIFICATION FOR DIFFERENT PROJECT

########################################################################
## GLOBAL VARIABLES
########################################################################
__RAW_DATA_PATH_DIR=/home/lxiang/cloud_research/PengGroup/XLi/Data/Haihui/CD8-HP
#### Execution or Output directory
__EXE_PATH=/home/lxiang/cloud_research/PengGroup/XLi/Data/Haihui/CD8-HP/CuffDiff_Jun2018
########################################################################

__INPUT_SAMPLE_DIR_List=(
Sample_16708  #0 ctrl1-0h
Sample_16709  #1 ctrl2-0h
Sample_16710  #2 dKO1-0h
Sample_16711  #3 dKO2-0h
Sample_16712  #4 WT1_CD8_72h 
Sample_16713  #5 WT2_CD8_72h
Sample_16714  #6 DKO1_CD8_72h
Sample_16715  #7 DKO2_CD8_72h
#
Sample_20051  #8 Ctrl-3n
Sample_20052  #9 Ctrl-4n
Sample_20053  #10 dKO-3n
Sample_20054  #11 dKO-4n
Sample_20055  #12 Ctrl-3S
Sample_20056  #13 dKO-3s
#
Project_20395_index9  #14 Ctrl-5n
Project_20396_index10  #15 Ctrl-6n
Project_20397_index11  #16 Ctrl-7n
Project_20398_index12  #17 dKO-5n
Project_20399_index13  #18 dKO-6n
Project_20400_index14  #19 dKO-7n
)





echo "INPUT_SAMPLE_DIR_List= (${__INPUT_SAMPLE_DIR_List[*]})"


#__OUT_SAMPLE_NAME_List=(Unstim_Ctrl2_TCM Unstim_TKO1_TCM_bp Unstim_TKO2_TCM)
SAMPLE_NUM=${#__INPUT_SAMPLE_DIR_List[*]}
########################################################################

########################################################################
##	MAIN BODY
########################################################################

main() {
#### Saving DIR Check and Create
DIR_CHECK_CREATE $__RAW_DATA_PATH_DIR
DIR_CHECK_CREATE $__EXE_PATH

#### Email Alert
FUNC_CHOOSE_EMAIL_ALERT
Alert_email=$?

echo ""
#echo "__FASTQ_DIR_R1 __FASTQ_DIR_R2 are the READS_FULL_DIR FOR ANALYSIS"

for (( i = 0; i <= $(expr $SAMPLE_NUM - 1); i++ ))
do
	#RUN_Peaks_Distribution_Analysis ${__INPUT_SAMPLE_DIR_List[i]}
	
	#RUN_Peaks_Distribution_Analysis ${__INPUT_SAMPLE_DIR_List[i]} 'bed'
	#RUN_TOPHAT ${__INPUT_SAMPLE_DIR_List[i]}
	#FUNC_Download ${__INPUT_SAMPLE_DIR_List[i]}
	#PRE_READS_DIR ${__INPUT_SAMPLE_DIR_List[i]} "fastq.gz"
	#RUN_FAST_QC
	#RUN_BOWTIE2 ${__INPUT_SAMPLE_DIR_List[i]} "mm9"
	#RUN_RPKM ${__INPUT_SAMPLE_DIR_List[i]} 'bed'
	#RUN_TOPHAT ${__INPUT_SAMPLE_DIR_List[i]} "CD8-HP" "mm9" "Haihui"
	#RUN_BED2WIG ${__INPUT_SAMPLE_DIR_List[i]} ${SPECIES}
	
	#SPECIES="mm9"
	#Data_Provider="Ref_GSM46662"
	#RUN_Wig2BigWig ${__RAW_DATA_PATH_DIR} ${__INPUT_SAMPLE_DIR_List[i]} 'Tcf1' ${SPECIES} ${Data_Provider}
	
	RUN_CUFFDIFF ${__INPUT_SAMPLE_DIR_List[*]}
	break
#### FOR a full cycle, it must be clear its READS_DIR in the end.
	#echo "Unset DIR sets."
	#unset ${__FASTQ_DIR_R1} ${__FASTQ_DIR_R2}
done

## SECOND LOOP
	#RUN_Reads_Profile "TSS"
#RUN_SICER

	echo "End Date: `date`"
	echo -e "\a FINISHED ALERT !"
	
	if [ ${Alert_email} == 0 ];then
	EMAIL_ME "${Start_Date}" ${Process_NAME}
	fi
}

##### Following Line is very IMPORTANT 
main "$@"

