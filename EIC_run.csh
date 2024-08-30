#!/bin/tcsh

# Set up conda and gurobi environment

conda activate /usr/local/usrapps/infews/group_env
module load gurobi
source /usr/local/apps/gurobi/gurobi810/linux64/bin/gurobi.sh

# Submit multiple jobs at once

set folNameBase = Exp

#foreach NN ( 500 525 550 575 600 625 650 675 700 )
foreach NN ( 500 )
#foreach NN ( 525 550 575 600 625 650 675 700 )

	#foreach SC ( _1 _2 )
	foreach SC ( _1 _2 _3 _4 )

		#foreach UC ( _simple_ _coal_ )
		foreach UC ( _simple_ )

			foreach TC ( 25 50 75 100 200 300 400 500 )
			#foreach TC ( 0 50 100 300 500 )

				set dirName = ${folNameBase}${NN}${UC}${TC}${SC}
	   			cd $dirName
				
				if ($UC == _simple_) then

					# Submit LSF job for the directory $dirName
	   				#bsub -n 8 -q shared_memory -R "span[hosts=1]" -R "rusage[mem=100GB]" -W 14400 -o out.%J -e err.%J "python wrapper_simple${SC}.py"
	   				bsub -n 8 -R "span[hosts=1]" -R "rusage[mem=60GB]" -W 5760 -o out.%J -e err.%J "python wrapper_simple${SC}.py"
	   				# Go back to upper level directory
	    				cd ..

				else if ($UC == _coal_) then

					# Submit LSF job for the directory $dirName
	   				#bsub -n 32 -q shared_memory -R "span[hosts=1]" -R "rusage[mem=60GB]" -W 14400 -o out.%J -e err.%J "python wrapper_coal.py"
	   				bsub -n 8 -R "span[hosts=1]" -R "rusage[mem=60GB]" -W 5760 -o out.%J -e err.%J "python wrapper_coal.py"
					# Go back to upper level directory
	    				cd ..

				endif

			end
		end
	end
end

conda deactivate
