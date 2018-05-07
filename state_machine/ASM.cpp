ASM

void Action:: avoidWall() {
	
	switch(goalStep) {
		case 1:
			dexter.comm='h';
			goalStep++;
			break;
		case 2:
			if(dexter.irDist > 15) {
				goalStep++;
				dexter.comm='h';
			}
			else(if(rand()%2==0)){
				dexter.comm='l';
			}
			else{
				dexter.comm='r';
			}
		break;
		case 3:
			if(interruptStatus==2)
					interruptStatus=3;
			scans=1;
			dexter.comm='h';
		break;
	}
}