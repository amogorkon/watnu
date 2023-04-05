from Levenshtein import ratio, seqratio, setratio
import shlex

do = "mit sarah liebe machen"
test = "sari mach lieb"



print(setratio(shlex.split(test), (shlex.split(do))))