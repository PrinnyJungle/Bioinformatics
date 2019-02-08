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
echo "-----------------------------------------------------------------"
echo "Start Date: `date`"
echo "-----------------------------------------------------------------"
Start_Date=`date`

Process_NAME=${1}
source ./functions.sh
echo "Import functions.sh Completed!" 
#			NEED MODIFICATION FOR DIFFERENT PROJECT

########################################################################
## GLOBAL VARIABLES
########################################################################
__RAW_DATA_PATH_DIR=~/cloud_research/PengGroup/XLi/Data/Haihui/CD8-HP/ChIP_seq/histone_mark/SICER_Results/ctrl_CD8_K27Ac
#### Execution or Output directory
__EXE_PATH=~/cloud_research/PengGroup/XLi/Data/Haihui/CD8-HP/ChIP_seq/histone_mark/profile_on_DNase_sites
#__EXE_PATH=~/cloud_research/PengGroup/XLi/Data/Haihui/CD8-HP/DNase_seq
########################################################################
########################################################################
##	MAIN BODY
########################################################################
__INPUT_SAMPLE_List=(
ctrl_CD8_K27Ac
#dKO_CD8_K27Ac
)

main() {
#### Saving DIR Check and Create
DIR_CHECK_CREATE $__RAW_DATA_PATH_DIR
DIR_CHECK_CREATE $__EXE_PATH

#### Email Alert
FUNC_CHOOSE_EMAIL_ALERT
Alert_email=$?

echo "-----------------------------------------------------------------"
echo "$(date "+%Y-%m-%d %H:%M") Start Processing....."

###
SPECIES='mm9'
Data_Provider='Haihui'
####

#FUNC_Download "http://shang.phys.gwu.edu/Test_Data" "test_Pipeline"
### Loop Operation
# https://stackoverflow.com/questions/10909685/run-parallel-multiple-commands-at-once-in-the-same-terminal
#Num_Loop=$(expr $(expr ${#__INPUT_SAMPLE_List[*]} - 1) / 4)
for (( i = 0; i <= $(expr ${#__INPUT_SAMPLE_List[*]} - 1); i++ ))
do
	#PRE_READS_DIR ${__INPUT_SAMPLE_List[i]} 'fastq.gz' 'Pairs'
	#RUN_FAST_QC &
	#RUN_TOPHAT ${__INPUT_SAMPLE_List[i]} "TEST" ${SPECIES} ${Data_Provider} & pid=$!
	#RUN_Venn_Diagram ${__RAW_DATA_PATH_DIR} 'bed'
	#RUN_ROSE_SUPER_Enhancer ${__INPUT_SAMPLE_List[0]}
	RUN_Reads_Profile "GeneBody" ${__INPUT_SAMPLE_List[i]} ${SPECIES}
	#RUN_SICER ${__INPUT_SAMPLE_List[1]} ${__INPUT_SAMPLE_List[0]} 400 "CD8-K27Ac" ${SPECIES} ${Data_Provider} & pid=$!
	#PID_LIST+=" $pid";
	break
	#break
#### FOR a full cycle, it must be clear its READS_DIR in the end.
	#echo "Unset DIR sets."
	#unset ${__FASTQ_DIR_R1} ${__FASTQ_DIR_R2}
done
#trap "kill $PID_LIST" SIGINT

echo "Parallel processes have started";
echo "wait ${PID_LIST}}....................................."
wait ${PID_LIST}

### Loop Operation

### Single Operation
	
### Single Operation
	#RUN_CELLRANGER ${__INPUT_SAMPLE_DIR_List[15]} "Hdac" "mm10"
	
	echo "End Date: `date`"
	echo -e "\a FINISHED ALERT !"
	
	if [ ${Alert_email} == 0 ];then
	EMAIL_ME "${Start_Date}" ${Process_NAME}
	fi
}

##### Following Line is very IMPORTANT 
main "$@"

