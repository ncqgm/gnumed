# creates SQL to imports a list of mono-component drugs from a CSV file

import sys
import io


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmTools


field_names = ['substance', 'product', 'form', 'company', 'strength_1', 'strength_2', 'strength_3', 'always_empty', 'unit']
non_empty_fields = ['substance', 'product', 'form', 'company', 'strength_1', 'unit']
numeric_fields = ['strength_1', 'strength_2', 'strength_3']


SQL_start = """-- ---------------------------------------------------------
-- data pack install script example
--
-- add a description here: Mono-substance drugs as available in India
-- license: GPL v2 or later, manually transferred 3rd party data
-- provided by Vaibhav Banait
--
-- https://www.gnumed.de/bin/view/Gnumed/GmManualReferenceData
-- ---------------------------------------------------------
-- enable this if running locally via
-- psql -d gnumed_vXX -U gm-dbo -f install-data-pack.sql
--SET default_transaction_read_only TO OFF;

-- ---------------------------------------------------------
-- drop staging tables if needed
\\unset ON_ERROR_STOP
DROP TABLE staging.india_drugs CASCADE;
\set ON_ERROR_STOP 1

-- ---------------------------------------------------------
-- run everything else in one transaction
BEGIN;

-- create staging tables as needed --
CREATE TABLE staging.india_drugs (
	brand_name text,
	substance text,
	form text,
	strength numeric,
	unit text
);

-- ---------------------------------------------------------
-- insert data in staging table
"""


SQL_stage_drug = """INSERT INTO staging.india_drugs (brand_name, substance, form, strength, unit) SELECT
	'%(brand_name)s',
	'%(substance)s',
	'%(form)s',
	gm.nullify_empty_string('%(strength)s')::numeric,
	'%(unit)s'
WHERE NOT EXISTS (
	SELECT 1 FROM staging.india_drugs WHERE brand_name = '%(brand_name)s'
);
"""


SQL_end = """-- ---------------------------------------------------------
-- transfer data to real tables

-- substances
INSERT INTO ref.consumable_substance (description, amount, unit) SELECT
	DISTINCT ON (s_id.substance, s_id.strength, s_id.unit)
	s_id.substance, s_id.strength, s_id.unit
FROM 
	staging.india_drugs s_id
WHERE
	s_id.strength IS NOT NULL
		AND
	NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance r_cs WHERE
			r_cs.description = s_id.substance
				AND
			r_cs.amount = s_id.strength
				AND
			r_cs.unit = s_id.unit
	)
;

-- drug products
INSERT INTO ref.drug_product (description, preparation) SELECT
	s_id.brand_name, s_id.form
FROM
	staging.india_drugs s_id
WHERE NOT EXISTS (
	SELECT 1 FROM ref.drug_product r_bd WHERE
		r_bd.description = s_id.brand_name
			AND
		r_bd.preparation = s_id.form
);

-- link components
INSERT INTO ref.lnk_substance2brand (fk_drug_product, fk_substance) SELECT
	(SELECT pk FROM ref.drug_product r_bd
	 WHERE
		r_bd.description = s_id.brand_name
			AND
		r_bd.preparation = s_id.form
	),
	(SELECT pk FROM ref.consumable_substance r_cs WHERE
		r_cs.description = s_id.substance
			AND
		r_cs.amount = s_id.strength
			AND
		r_cs.unit = s_id.unit
	)
FROM
	staging.india_drugs s_id
WHERE NOT EXISTS (
	SELECT 1 FROM ref.lnk_substance2brand WHERE
		fk_drug_product = (
			SELECT pk FROM ref.drug_product WHERE
				description = s_id.brand_name
					AND
				preparation = s_id.form
		)
			AND
		fk_substance = (
			SELECT pk FROM ref.consumable_substance r_cs WHERE
				r_cs.description = s_id.substance
					AND
				r_cs.amount = s_id.strength
					AND
				r_cs.unit = s_id.unit
		)
);

-- ---------------------------------------------------------
-- drop staging tables again, if needed --
\\unset ON_ERROR_STOP
DROP TABLE staging.india_drugs CASCADE;
\set ON_ERROR_STOP 1

-- ---------------------------------------------------------

-- finalize transaction --
-- uncomment this once you are satisfied your script works:
COMMIT;
-- ---------------------------------------------------------
"""

#---------------------------------------------------------------------------------------------------
def create_sql(filename):

	csv_file = open(filename, mode = 'rt', encoding = 'utf-8-sig')

	csv_lines = gmTools.unicode_csv_reader (
		csv_file,
		fieldnames = field_names,
		delimiter = ';',
		quotechar = '"',
		dict = True
	)

	print(SQL_start)

	line_idx = 0
	skip_line = False
	for line in csv_lines:
		line_idx += 1
		print("-- line #%s" % line_idx)
		# normalize field content
		for field in field_names:
			try:
				line[field] = line[field].strip().strip(';,').strip().replace("'", "''")
			except AttributeError:		# trailing fields are a list
				pass
		# verify required fields
		for field in non_empty_fields:
			if line[field] == '':
				print("-- ignoring line: empty field [%s]" % field)
				print("--", line)
				print("")
				skip_line = True
				break
		if skip_line:
			skip_line = False
			continue
		# verify numeric fields
		for field in numeric_fields:
			if line[field] == '':
				continue
			success, num_val = gmTools.input2decimal(initial = line[field])
			if not success:
				print("-- ignoring line: field [%s] not numeric: >>>%s<<<" % (field, line[field]))
				print("--", line)
				print("")
				skip_line = True
				break
			line[field] = num_val
		if skip_line:
			skip_line = False
			continue

		# actually create SQL
		# loop over strengths
		for field in numeric_fields:
			if line[field] == '':
				continue
			line['brand_name'] = ('%%(product)s %%(%s)s (%%(company)s)' % field) % line
			line['strength'] = line[field]
			print(SQL_stage_drug % line)

	print(SQL_end)

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	create_sql(sys.argv[1])
