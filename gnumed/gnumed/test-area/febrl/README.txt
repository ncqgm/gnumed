scripts for connecting gnumed to febrl to run the deduplication test case on gnumed !!
What for? fun . Also shows febrl does work with other projects (after debugging), and vici versa gnumed.


These files conveniently run in a subdirectory of the febrl root directory ( e.g. gnumed-febrl),
except for dataset.py and datasetTest.py , which replace the febrl 0.2.2 versions of those files
in the febrl root directory. Do a diff before replacing, to see the difference .


clean-gnumed-demo.sql  - cleans the gnumed demo schema, don't use on live database.
correct_postcode.py - run a febrl/dbgen  csv test dataset file to output a csv file compatible with gnumed
csv_to_gnumed.py  -  loads a compatible csv file into gnumed
dataset.py  -  modified febrl/dataset.py script that has a postgres dataset, and fixes a next_record_num bug


reclink.sql - script to set up a test case postgres database
datasetTest.py - test case which includes a postgres dataset test.

v_febrl_demo_read_au.sql - a gnumed postgres view which is nearer to the dbgen/csv format.
read_v_febrl_demo_au.py  - reads a gnumed demographics via the view v_febrl_demo_au and outputs a csv file.

gnumed-file-project-deduplicate.py - runs a dedup on a csv file output from read_v_febrl_demo_au.py

gnumed-pgdb-project-deduplicate.py - runs a dedup on a gnumed schema that has a view v_febrl_demo_read_au.



