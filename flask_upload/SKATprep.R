args <- commandArgs(trailingOnly = TRUE)
method=args[1]
filename=args[2]
func=args[3]

func_gene=args[4]
if(!is.na(func_gene)){
  func_gene=strsplit(func_gene,split=',')
  func_gene=func_gene[[1]]
}
exonic_func_gene=args[5]
if(!is.na(exonic_func_gene)){
  exonic_func_gene=strsplit(exonic_func_gene,split=',')
  exonic_func_gene=exonic_func_gene[[1]]
  for(k in 1:length(exonic_func_gene)){
	if(grepl('_',exonic_func_gene[k])){
		exonic_func_gene[k]=gsub('_',' ',exonic_func_gene[k])
	}	
  }
}

print(func_gene)
print(exonic_func_gene)

Annovar_output<-read.csv("annovar_output_example.csv")
	if(is.na(func)){
	  idx=which(Annovar_output$Func.refGene=='exonic' & Annovar_output$ExonicFunc.refGene %in% c('frameshift deletion', 'frameshift insertion','nonsynonymous SNV', 'startloss', 'stopgain', 'stoploss'))
	}else if(func=='All'){
	  idx=1:nrow(Annovar_output)
	}else if(func=='manual'){
	  idx=which(Annovar_output$Func.refGene %in% func_gene & Annovar_output$ExonicFunc.refGene %in% exonic_func_gene) 
	}else{
	  print('Fix the flag')
	  break
	}
	Annovar_output=Annovar_output[idx,1:ncol(Annovar_output)]
	if(length(idx)==0){
		print('No markers')
	}else{
		SetID = Annovar_output[c(7,16)]
		write.table(SetID,file='result.SetID',row.names=F,col.names=F,quote=F)
	}