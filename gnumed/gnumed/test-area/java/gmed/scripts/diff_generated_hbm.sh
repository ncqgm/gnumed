
for f in `find  build/class -name "*.hbm.xml"`;
 do 
  e=${f##*/}
  echo _________________________________________
  echo $e
  diff $f generated_hbm/$e ; done
