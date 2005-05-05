PYTHONPATH=$PYTHONPATH:./py
export PYTHONPATH
python py/driver.py 2001-09-21\ 17-56.HL7
read -p "Parse ba xml file as well?"  x
echo "x = $x"
if [[ $x == "y" ]];then python py/driver.py oscar-ba.xml;
fi
	
