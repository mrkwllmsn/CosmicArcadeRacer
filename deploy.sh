# this script assumes you have pip installed pyminify and mpremote already... 

read -p "This will overwrite main.py on the Pico, Are you sure? " -n 1 -r
echo    
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Shrinking with pyminify..." && 
  pyminify ./cosmic_arcade_racer.py > outrun_min.py && 
  echo "Copying to Pico with mpremote" && 
  mpremote cp ./outrun_min.py :main.py && 
  mpremote reset
fi


