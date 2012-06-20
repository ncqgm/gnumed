-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- Data contributed by: vbanait@gmail.com
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
begin;
-- --------------------------------------------------------------

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acetylsalicylic Acid'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acetylsalicylic Acid'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acyclovir'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acyclovir'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Albendazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Albendazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amlodipine'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amlodipine'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amlodipine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amlodipine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amodiaquin'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amodiaquin'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amoxycillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amoxycillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ampicillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ampicillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artemether'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artemether'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artesunate'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artesunate'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Atenolol'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Atenolol'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Azithromycin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Azithromycin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Calcium Lactate'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Calcium Lactate'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbamazepine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbamazepine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cetirizine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cetirizine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorampenicol'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorampenicol'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chloroquine'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chloroquine'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorphineramine'::text,
		'4'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorphineramine'
				AND
			amount = '4'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cimetidine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cimetidine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciprofloxacin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciprofloxacin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cyprheptadine'::text,
		'4'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cyprheptadine'
				AND
			amount = '4'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Dexamethasone'::text,
		'0.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Dexamethasone'
				AND
			amount = '0.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diazepam'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diazepam'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Enalpril Maleate'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Enalpril Maleate'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ephedrine'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ephedrine'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Erythromycin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Erythromycin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Folic Acid'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Folic Acid'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Furosemide'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Furosemide'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Glibenclamide'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Glibenclamide'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Griseofulvin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Griseofulvin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hyoscine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hyoscine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ibuprofen'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ibuprofen'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Indomethacin'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Indomethacin'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ketoconazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ketoconazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lansoprazol'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lansoprazol'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Levamisole'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Levamisole'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Loperamide'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Loperamide'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Loratidine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Loratidine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Losartan'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Losartan'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Losartan'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Losartan'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mebendazole'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mebendazole'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Meloxicam'::text,
		'7.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Meloxicam'
				AND
			amount = '7.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metronidazole Coated'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metronidazole Coated'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metronidazole Uncoated'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metronidazole Uncoated'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nimesulide'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nimesulide'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Norfloxacin'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Norfloxacin'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nystatin Lozenge'::text,
		'100000'::numeric,
		'iu'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nystatin Lozenge'
				AND
			amount = '100000'
				AND
			unit = 'iu'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Omeprazole'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Omeprazole'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Paracetamol'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Paracetamol'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Phenoxymethylpenicillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Phenoxymethylpenicillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Piroxicam'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Piroxicam'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Primaquin'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Primaquin'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Promethazine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Promethazine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pyrimethamine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pyrimethamine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sulfadoxine'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sulfadoxine'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Salbutamol'::text,
		'4'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Salbutamol'
				AND
			amount = '4'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sparfloxacin'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sparfloxacin'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sulfadimidine'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sulfadimidine'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tetracycline'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tetracycline'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tinidazole'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tinidazole'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tramadol'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tramadol'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acabose'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acabose'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acabose'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acabose'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acetaminophen'::text,
		'325'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acetaminophen'
				AND
			amount = '325'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acetazolamide'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acetazolamide'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acetylsalicylic Acid Ent.Coated'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acetylsalicylic Acid Ent.Coated'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acetylsalicylic Acid Ent.Coated'::text,
		'75'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acetylsalicylic Acid Ent.Coated'
				AND
			amount = '75'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acyclovir'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acyclovir'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acyclovir'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acyclovir'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acyclovir'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acyclovir'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acyclovir'::text,
		'800'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acyclovir'
				AND
			amount = '800'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acyclovir'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acyclovir'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Acyclovir'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Acyclovir'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Alh'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Alh'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mg Trisilicate'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mg Trisilicate'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Albendazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Albendazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Albendazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Albendazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Albendazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Albendazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Albendazole'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Albendazole'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Alfacalcidol'::text,
		'0.25'::numeric,
		'mcg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Alfacalcidol'
				AND
			amount = '0.25'
				AND
			unit = 'mcg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Allopurinol'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Allopurinol'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Allopurinol'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Allopurinol'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Allopurinol'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Allopurinol'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Alprazolam'::text,
		'0.25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Alprazolam'
				AND
			amount = '0.25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amiloride'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amiloride'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hydrochlorthiazide'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hydrochlorthiazide'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Aminophylline Hydrate'::text,
		'225'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Aminophylline Hydrate'
				AND
			amount = '225'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Aminophylline'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Aminophylline'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Aminosidine'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Aminosidine'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amiodarone'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amiodarone'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amitriptyline'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amitriptyline'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amlodipine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amlodipine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amlodipine'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amlodipine'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amlodipine'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amlodipine'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amoxyl'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amoxyl'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clavulanic Acid'::text,
		'125'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clavulanic Acid'
				AND
			amount = '125'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amoxyl'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amoxyl'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clavulanic Acid'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clavulanic Acid'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amoxycillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amoxycillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amoxycillin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amoxycillin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ampicillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ampicillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cloxacillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cloxacillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Anastrazole'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Anastrazole'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artemether'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artemether'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lumefantrine'::text,
		'120'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lumefantrine'
				AND
			amount = '120'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artemether'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artemether'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artemether'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artemether'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artesunate'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artesunate'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artesunate'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artesunate'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artesunate'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artesunate'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artesunate'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artesunate'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artesunate'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artesunate'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artovaquone'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artovaquone'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Proguanil'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Proguanil'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artovastatin'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artovastatin'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artovastatin'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artovastatin'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artovastatin'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artovastatin'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artovastatin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artovastatin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artovastatin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artovastatin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Artovastatin'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Artovastatin'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Aspartame'::text,
		'18'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Aspartame'
				AND
			amount = '18'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Aspartame'::text,
		'18'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Aspartame'
				AND
			amount = '18'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Aspirin-Soluble'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Aspirin-Soluble'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Atenolol'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Atenolol'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorthalidone'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorthalidone'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Atenolol'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Atenolol'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorthalidone'::text,
		'12.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorthalidone'
				AND
			amount = '12.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Azathioprine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Azathioprine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Azathioprine'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Azathioprine'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Azithromycin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Azithromycin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Azithromycin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Azithromycin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Azithromycin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Azithromycin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Azithromycin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Azithromycin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Baclofen'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Baclofen'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'B-Artemether'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'B-Artemether'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Belladona'::text,
		'0.25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Belladona'
				AND
			amount = '0.25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Benazapril'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Benazapril'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bendrofluazide'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bendrofluazide'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Benzexhol'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Benzexhol'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Benzexhol'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Benzexhol'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Betahistine HCL'::text,
		'8'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Betahistine HCL'
				AND
			amount = '8'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bicalutamide'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bicalutamide'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bicalutamide'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bicalutamide'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bisacodyl'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bisacodyl'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bismuth Subsalicylate'::text,
		'256'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bismuth Subsalicylate'
				AND
			amount = '256'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bromazepam'::text,
		'1.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bromazepam'
				AND
			amount = '1.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bromocriptin'::text,
		'2.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bromocriptin'
				AND
			amount = '2.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bromocriptin'::text,
		'2.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bromocriptin'
				AND
			amount = '2.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Bromohexine'::text,
		'8'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Bromohexine'
				AND
			amount = '8'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Busulphan'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Busulphan'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cabergoline'::text,
		'0.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cabergoline'
				AND
			amount = '0.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Calcium Folinate'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Calcium Folinate'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Calcium Gluconate Effervescent'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Calcium Gluconate Effervescent'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Calcium Gluconate'::text,
		'600'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Calcium Gluconate'
				AND
			amount = '600'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Capitopril'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Capitopril'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Capitopril'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Capitopril'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbamazepine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbamazepine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbamazepine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbamazepine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbamazepine'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbamazepine'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbamazepine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbamazepine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbamazepine CR'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbamazepine CR'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbamezapine'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbamezapine'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbamezapine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbamezapine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbimazole'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbimazole'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbimazole'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbimazole'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carvedilol'::text,
		'6.25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carvedilol'
				AND
			amount = '6.25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carvidilol'::text,
		'12.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carvidilol'
				AND
			amount = '12.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carvidilol'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carvidilol'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carvidilol'::text,
		'6.25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carvidilol'
				AND
			amount = '6.25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefaclor MR'::text,
		'375'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefaclor MR'
				AND
			amount = '375'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefaclor MR'::text,
		'650'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefaclor MR'
				AND
			amount = '650'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefadroxil'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefadroxil'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefadroxil Dispersible'::text,
		'125'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefadroxil Dispersible'
				AND
			amount = '125'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefadroxil Dispersible'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefadroxil Dispersible'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefixime'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefixime'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefopoxime'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefopoxime'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefuroxime'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefuroxime'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cefuroxime'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cefuroxime'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Celecoxib'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Celecoxib'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Celecoxib'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Celecoxib'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cephalexin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cephalexin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cephalexin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cephalexin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cephradine'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cephradine'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cetirizine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cetirizine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cetirizine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cetirizine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cetirizine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cetirizine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorambucil'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorambucil'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlodiazepoxide'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlodiazepoxide'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlodiazepoxide'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlodiazepoxide'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlodiazepoxide'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlodiazepoxide'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chloroquine'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chloroquine'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorthalidone'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorthalidone'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorpromazine'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorpromazine'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorpromazine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorpromazine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorpropamide'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorpropamide'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cholestyramine'::text,
		'4'::numeric,
		'g'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cholestyramine'
				AND
			amount = '4'
				AND
			unit = 'g'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cilazapril'::text,
		'2.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cilazapril'
				AND
			amount = '2.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cilazapril'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cilazapril'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cimetidine'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cimetidine'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cimetidine'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cimetidine'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cinnarazine'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cinnarazine'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cinnarazine'::text,
		'75'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cinnarazine'
				AND
			amount = '75'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cinnarazine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cinnarazine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciprofloxacin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciprofloxacin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciprofloxacin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciprofloxacin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciprofloxacin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciprofloxacin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciprofloxacin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciprofloxacin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciprofloxacin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciprofloxacin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciprofloxacin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciprofloxacin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciproxacin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciproxacin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ciproxacin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ciproxacin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Citalopram'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Citalopram'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clarithromycin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clarithromycin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clindamycin'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clindamycin'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clindamycin'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clindamycin'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clofazimine'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clofazimine'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clomiphene'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clomiphene'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clomiphene'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clomiphene'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clomipramine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clomipramine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clonazepam'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clonazepam'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clopidogrel'::text,
		'75'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clopidogrel'
				AND
			amount = '75'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clopidogrel'::text,
		'75'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clopidogrel'
				AND
			amount = '75'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cloxacillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cloxacillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Codeine Phosphate'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Codeine Phosphate'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cod liver Oil'::text,
		'15'::numeric,
		'g'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cod liver Oil'
				AND
			amount = '15'
				AND
			unit = 'g'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Colchicine'::text,
		'500'::numeric,
		'mcg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Colchicine'
				AND
			amount = '500'
				AND
			unit = 'mcg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cotrimoxazole'::text,
		'800'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cotrimoxazole'
				AND
			amount = '800'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cyclphosphamide'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cyclphosphamide'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cyprheptadine'::text,
		'4'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cyprheptadine'
				AND
			amount = '4'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Cyproterone'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Cyproterone'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ethinylestradiol'::text,
		'0.035'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ethinylestradiol'
				AND
			amount = '0.035'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Daflon'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Daflon'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Danazol'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Danazol'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Danazol'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Danazol'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Dapsone'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Dapsone'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Dexamethasone'::text,
		'0.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Dexamethasone'
				AND
			amount = '0.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Dexamethasone'::text,
		'0.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Dexamethasone'
				AND
			amount = '0.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Dispersible'::text,
		'46.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Dispersible'
				AND
			amount = '46.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Potassium'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Potassium'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Potassiumtab'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Potassiumtab'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na Retard'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na Retard'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na Retard'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na Retard'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na Sr'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na Sr'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na Sr'::text,
		'75'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na Sr'
				AND
			amount = '75'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diclofenac Na'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diclofenac Na'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Didanosine'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Didanosine'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Didanosine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Didanosine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diethylcarbamazine'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diethylcarbamazine'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Digoxin'::text,
		'250'::numeric,
		'mcg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Digoxin'
				AND
			amount = '250'
				AND
			unit = 'mcg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Dihydroartemisinin'::text,
		'60'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Dihydroartemisinin'
				AND
			amount = '60'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Dihydrocodein'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Dihydrocodein'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Dihydrogesteron'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Dihydrogesteron'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diltiazem Cr'::text,
		'120'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diltiazem Cr'
				AND
			amount = '120'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Diltiazem'::text,
		'60'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Diltiazem'
				AND
			amount = '60'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Dimenhydrinate'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Dimenhydrinate'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Domperidon'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Domperidon'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Donazepril'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Donazepril'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Doxaepin HCL'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Doxaepin HCL'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Doxazosin'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Doxazosin'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Doxazosin'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Doxazosin'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Doxycycline'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Doxycycline'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Doxycycline'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Doxycycline'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Doxycycline'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Doxycycline'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Drotaverine HCL'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Drotaverine HCL'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Efavirenz'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Efavirenz'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Efavirenz'::text,
		'600'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Efavirenz'
				AND
			amount = '600'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Efavirenz'::text,
		'600'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Efavirenz'
				AND
			amount = '600'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Enalpril'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Enalpril'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Enalpril'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Enalpril'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Enalpril'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Enalpril'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Enalpril'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Enalpril'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Enalpril'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Enalpril'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ergotamine'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ergotamine'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Esomeprazole'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Esomeprazole'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Esomeprazole'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Esomeprazole'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Esomeprazole'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Esomeprazole'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Esomeprazole'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Esomeprazole'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ethambutol'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ethambutol'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ethosuxamide'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ethosuxamide'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Evening Primrose'::text,
		'1000'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Evening Primrose'
				AND
			amount = '1000'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Evening Primrose'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Evening Primrose'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Famciclovir'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Famciclovir'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Famotidine'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Famotidine'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Famotidine'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Famotidine'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fenofibrate'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fenofibrate'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Felodipine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Felodipine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Felodipine'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Felodipine'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ferrous Sulphate'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ferrous Sulphate'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Flucloxacillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Flucloxacillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Flucloxacillin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Flucloxacillin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluconazole'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluconazole'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Flunitrazepam'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Flunitrazepam'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluoxetin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluoxetin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluoxetin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluoxetin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluoxetin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluoxetin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluoxetin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluoxetin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Folic Acid'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Folic Acid'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Folic Acid'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Folic Acid'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Folinic Acid'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Folinic Acid'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Furosemide'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Furosemide'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Furosemide'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Furosemide'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Gamolenic Acid'::text,
		'80'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Gamolenic Acid'
				AND
			amount = '80'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ganciclovir'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ganciclovir'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Gatifloxacin'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Gatifloxacin'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Gatifloxacin'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Gatifloxacin'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Gatifloxacin'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Gatifloxacin'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Gemfibrozil'::text,
		'600'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Gemfibrozil'
				AND
			amount = '600'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Glibenclamide'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Glibenclamide'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Glibenclamide'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Glibenclamide'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Gliclazide'::text,
		'80'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Gliclazide'
				AND
			amount = '80'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Gliclazide'::text,
		'80'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Gliclazide'
				AND
			amount = '80'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Gliclazide'::text,
		'80'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Gliclazide'
				AND
			amount = '80'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Glimepride'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Glimepride'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Glipizide'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Glipizide'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Glipizide'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Glipizide'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Griseofulvin'::text,
		'125'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Griseofulvin'
				AND
			amount = '125'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Griseofulvin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Griseofulvin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Griseofulvin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Griseofulvin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Halofantrin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Halofantrin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Haloperidol'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Haloperidol'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Haloperidol'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Haloperidol'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Haloperidol'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Haloperidol'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Haloperidol'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Haloperidol'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hydralazine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hydralazine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hydralazine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hydralazine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hydrochlothiazide'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hydrochlothiazide'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hydrochlothiazide'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hydrochlothiazide'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hydrocortisone'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hydrocortisone'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hyoscine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hyoscine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hyroxyzine Hcl'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hyroxyzine Hcl'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ibuprofen'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ibuprofen'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Paracetamol'::text,
		'325'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Paracetamol'
				AND
			amount = '325'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ibuprofen'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ibuprofen'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Imipramine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Imipramine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Imipramine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Imipramine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Indapamide'::text,
		'2.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Indapamide'
				AND
			amount = '2.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Indinavir'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Indinavir'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Indomethacin'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Indomethacin'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Iron Sulphate'::text,
		'34'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Iron Sulphate'
				AND
			amount = '34'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isoniazid'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isoniazid'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rifampicin'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rifampicin'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isoniazid'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isoniazid'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isosorbide Dinitrate'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isosorbide Dinitrate'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isosorbide Dinitrate'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isosorbide Dinitrate'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isosorbide Mononitrate'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isosorbide Mononitrate'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isosorbide Mononitrate'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isosorbide Mononitrate'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isotrenitoin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isotrenitoin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isotrenitoin'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isotrenitoin'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ispagula Hask Powder'::text,
		'3.5'::numeric,
		'g'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ispagula Hask Powder'
				AND
			amount = '3.5'
				AND
			unit = 'g'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Itraconazole'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Itraconazole'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Itraconazole'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Itraconazole'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ivermectin'::text,
		'3'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ivermectin'
				AND
			amount = '3'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ketoconazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ketoconazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ketoconazole'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ketoconazole'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ketoprofen'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ketoprofen'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ketotifen'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ketotifen'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ketotifen'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ketotifen'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lamivudine'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lamivudine'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Zidovudine'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Zidovudine'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lamivudine'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lamivudine'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lamivudine'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lamivudine'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lamotriagen'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lamotriagen'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lamotriagen'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lamotriagen'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lamotriagen'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lamotriagen'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lansoprazol'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lansoprazol'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lansoprazol'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lansoprazol'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lansoprazol'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lansoprazol'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tinidazol'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tinidazol'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Clathromycin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Clathromycin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lecithin'::text,
		'1200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lecithin'
				AND
			amount = '1200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lethicin'::text,
		'1200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lethicin'
				AND
			amount = '1200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Levodopa'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Levodopa'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbidopa'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbidopa'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Levodopa'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Levodopa'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Carbidopa'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Carbidopa'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Levofloxacin'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Levofloxacin'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Levofloxacin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Levofloxacin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Levonegestrol'::text,
		'0.75'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Levonegestrol'
				AND
			amount = '0.75'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Levonorgestrel'::text,
		'0.15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Levonorgestrel'
				AND
			amount = '0.15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lincomycin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lincomycin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lisinopril'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lisinopril'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lisinopril'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lisinopril'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lisinopril'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lisinopril'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lisinopril'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lisinopril'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lisinopril'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lisinopril'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hydrochlothiazide'::text,
		'12.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hydrochlothiazide'
				AND
			amount = '12.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lisinopril'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lisinopril'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lisinopril'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lisinopril'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lithium Carbonate'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lithium Carbonate'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lithium Carbonate'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lithium Carbonate'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Loperamide'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Loperamide'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Loperamide'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Loperamide'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Loratidine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Loratidine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lorazepam'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lorazepam'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lorazepam'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lorazepam'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lorazepam'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lorazepam'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'L-Ornithine L-Aspartate Granules'::text,
		'3'::numeric,
		'g'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'L-Ornithine L-Aspartate Granules'
				AND
			amount = '3'
				AND
			unit = 'g'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'L-Ornithine Laspartate'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'L-Ornithine Laspartate'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Losartan'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Losartan'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Losartan'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Losartan'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Hydrochlothiazide'::text,
		'12.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Hydrochlothiazide'
				AND
			amount = '12.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Maprotiline'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Maprotiline'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Maprotiline'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Maprotiline'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Maprotiline'::text,
		'75'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Maprotiline'
				AND
			amount = '75'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mebendazole'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mebendazole'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mebendazole'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mebendazole'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Meclizine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Meclizine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Caffein'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Caffein'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Medroxyprogesterone'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Medroxyprogesterone'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Medroxyprogesterone'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Medroxyprogesterone'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Medroxyprogesterone'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Medroxyprogesterone'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mefenamic Acid'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mefenamic Acid'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mefenamic Acid'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mefenamic Acid'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mefenamic Acid'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mefenamic Acid'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mefloquine HCL Lactab'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mefloquine HCL Lactab'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Melphalan'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Melphalan'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Melatonine'::text,
		'3'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Melatonine'
				AND
			amount = '3'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Meloxicam'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Meloxicam'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Mestrolone'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Mestrolone'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metformin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metformin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metformin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metformin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metformin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metformin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metformin'::text,
		'850'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metformin'
				AND
			amount = '850'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metformin'::text,
		'850'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metformin'
				AND
			amount = '850'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Methotrexate'::text,
		'2.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Methotrexate'
				AND
			amount = '2.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Methylergometrine'::text,
		'0.125'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Methylergometrine'
				AND
			amount = '0.125'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Methyldopa'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Methyldopa'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Methylphenidate'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Methylphenidate'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Methylprednisolone'::text,
		'16'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Methylprednisolone'
				AND
			amount = '16'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metoclopramide'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metoclopramide'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metoprolol'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metoprolol'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metoprolol'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metoprolol'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Metronidazole Uncoated'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Metronidazole Uncoated'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Midazolam'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Midazolam'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Midazolam'::text,
		'7.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Midazolam'
				AND
			amount = '7.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Minocycline'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Minocycline'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Misoprostol'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Misoprostol'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Moxifloxacin'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Moxifloxacin'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nalidixic Acid'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nalidixic Acid'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Naproxane'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Naproxane'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Naproxane'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Naproxane'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Neomycin'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Neomycin'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nevirapine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nevirapine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nevirapine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nevirapine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nevirapine'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nevirapine'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Lamiv'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Lamiv'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Niclosamide'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Niclosamide'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nicotine Gum'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nicotine Gum'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nifedipine Depocaps'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nifedipine Depocaps'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nifedipine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nifedipine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nifedipine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nifedipine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nifedipine R'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nifedipine R'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nifedipine'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nifedipine'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Atenolol'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Atenolol'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nifuroxazide'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nifuroxazide'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nimesulide'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nimesulide'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nimesulide'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nimesulide'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nitofurantoin'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nitofurantoin'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nitrazepam'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nitrazepam'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nootropil'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nootropil'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nootropil'::text,
		'800'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nootropil'
				AND
			amount = '800'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Norethisterone'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Norethisterone'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Norfloxacin'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Norfloxacin'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nortriptyline'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nortriptyline'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Fluphenazzine'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Fluphenazzine'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Nystatin'::text,
		'50000'::numeric,
		'iu'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Nystatin'
				AND
			amount = '50000'
				AND
			unit = 'iu'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Oestrogen Conjugated'::text,
		'0.625'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Oestrogen Conjugated'
				AND
			amount = '0.625'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Oestrogen Conjugated'::text,
		'0.625'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Oestrogen Conjugated'
				AND
			amount = '0.625'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Oestrogen Conjugated'::text,
		'1.25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Oestrogen Conjugated'
				AND
			amount = '1.25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Oestrogen Congugated'::text,
		'1.25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Oestrogen Congugated'
				AND
			amount = '1.25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ofloxacin Sr'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ofloxacin Sr'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ofloxacin'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ofloxacin'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ofloxacin'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ofloxacin'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ofloxacin'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ofloxacin'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Olanzepine'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Olanzepine'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Olanzepine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Olanzepine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Olanzepine'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Olanzepine'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Olanzepine'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Olanzepine'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Omeprazole'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Omeprazole'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Omeprazole'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Omeprazole'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Omeprazole'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Omeprazole'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Orlistat'::text,
		'120'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Orlistat'
				AND
			amount = '120'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Oxybutinin'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Oxybutinin'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pantoprazole'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pantoprazole'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Paracetamol'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Paracetamol'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Caffein'::text,
		'65'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Caffein'
				AND
			amount = '65'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Paracetamol'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Paracetamol'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Codain'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Codain'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Paracetamol'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Paracetamol'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Codein'::text,
		'8'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Codein'
				AND
			amount = '8'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Paracetamol'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Paracetamol'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Paroaxetin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Paroaxetin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Paroaxetin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Paroaxetin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Passiflora Incarnata'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Passiflora Incarnata'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pefloxacin'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pefloxacin'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pefloxacin'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pefloxacin'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pentoxiphylline'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pentoxiphylline'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Phenolpthaline'::text,
		'125'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Phenolpthaline'
				AND
			amount = '125'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Phenytoin'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Phenytoin'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pioglitazone'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pioglitazone'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pioglitazone'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pioglitazone'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pioglitazone'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pioglitazone'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Piperazine Citrate'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Piperazine Citrate'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Piracetam'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Piracetam'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Piroxicam'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Piroxicam'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Piroxicam'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Piroxicam'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pizotifen'::text,
		'0.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pizotifen'
				AND
			amount = '0.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Praziquantel'::text,
		'600'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Praziquantel'
				AND
			amount = '600'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Praziquantel'::text,
		'600'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Praziquantel'
				AND
			amount = '600'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Prazocin'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Prazocin'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Prazocin'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Prazocin'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Prednisolon'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Prednisolon'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Primaquin'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Primaquin'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Probenecid'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Probenecid'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Procarbazine cap'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Procarbazine cap'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Prochlorperazine'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Prochlorperazine'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Proguanil'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Proguanil'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Propatheline'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Propatheline'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Propranolol'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Propranolol'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Propranolol'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Propranolol'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Propranolol'::text,
		'80'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Propranolol'
				AND
			amount = '80'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Propylthiouracil'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Propylthiouracil'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Provastatin'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Provastatin'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pseudoephedrine Hclcap'::text,
		'120'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pseudoephedrine Hclcap'
				AND
			amount = '120'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pyrazinamide'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pyrazinamide'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pyridostigmine'::text,
		'60'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pyridostigmine'
				AND
			amount = '60'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pyridoxine'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pyridoxine'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pyrimethamine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pyrimethamine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pyrimethamine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pyrimethamine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Pyrimethamine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Pyrimethamine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sulfadoxine'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sulfadoxine'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Quinapril'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Quinapril'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Quinapril'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Quinapril'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Quinapril'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Quinapril'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Chlorthiazide'::text,
		'12.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Chlorthiazide'
				AND
			amount = '12.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Quinine'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Quinine'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Raberaprazole'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Raberaprazole'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ramipril'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ramipril'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ramipril'::text,
		'2.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ramipril'
				AND
			amount = '2.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ramipril'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ramipril'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ranitidine'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ranitidine'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ranitidine'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ranitidine'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ranitidine'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ranitidine'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ranitidine'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ranitidine'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rifampicin'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rifampicin'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Isoniazide'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Isoniazide'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rifampicin'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rifampicin'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rifampicin'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rifampicin'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Resperidone'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Resperidone'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Resperidone'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Resperidone'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Resperidone'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Resperidone'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Resperidone'::text,
		'2'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Resperidone'
				AND
			amount = '2'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rofecoxib Meltab'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rofecoxib Meltab'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rofecoxib'::text,
		'12.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rofecoxib'
				AND
			amount = '12.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rofecoxib'::text,
		'12.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rofecoxib'
				AND
			amount = '12.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rofecoxib'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rofecoxib'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Rofecoxib'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Rofecoxib'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Roxithromycin'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Roxithromycin'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Royal Jell'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Royal Jell'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Saquinavir Softcap'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Saquinavir Softcap'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Secnidazole'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Secnidazole'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Secnidazole'::text,
		'1000'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Secnidazole'
				AND
			amount = '1000'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sertraline'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sertraline'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sildenafil'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sildenafil'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sildenafil'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sildenafil'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sildenafil'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sildenafil'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sildenafil'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sildenafil'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sildenafil'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sildenafil'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sildenafil'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sildenafil'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sildenafil'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sildenafil'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Silymarin'::text,
		'70'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Silymarin'
				AND
			amount = '70'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Simvaststin'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Simvaststin'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Simvaststin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Simvaststin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Simvastatin'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Simvastatin'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Simvastatin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Simvastatin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Simvastatin'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Simvastatin'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sodium Valproate'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sodium Valproate'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sodium Valproate'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sodium Valproate'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sotolol'::text,
		'80'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sotolol'
				AND
			amount = '80'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sparfloxacin'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sparfloxacin'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Spirinolactone'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Spirinolactone'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Spirinolactone'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Spirinolactone'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Spirinolactone'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Spirinolactone'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Spirinolactone'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Spirinolactone'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Stavudine'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Stavudine'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Stavudine'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Stavudine'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Stilboestrol'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Stilboestrol'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sulfasalzine'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sulfasalzine'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Sulphadiazine'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Sulphadiazine'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tadafil'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tadafil'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tamoxifen'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tamoxifen'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tamoxifen'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tamoxifen'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tenoxicam'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tenoxicam'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Terbinafine'::text,
		'125'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Terbinafine'
				AND
			amount = '125'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Terbinafine'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Terbinafine'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Terbinafine'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Terbinafine'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Testosterone'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Testosterone'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Theophyllin'::text,
		'300'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Theophyllin'
				AND
			amount = '300'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Theophyllin'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Theophyllin'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Thiabendazole'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Thiabendazole'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Thiampenicol'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Thiampenicol'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Thiampenicol'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Thiampenicol'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Thioridazine'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Thioridazine'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Thioridazine'::text,
		'25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Thioridazine'
				AND
			amount = '25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Thioridazine'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Thioridazine'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Thyroxine'::text,
		'100'::numeric,
		'mcg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Thyroxine'
				AND
			amount = '100'
				AND
			unit = 'mcg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Thyroxine'::text,
		'50'::numeric,
		'mcg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Thyroxine'
				AND
			amount = '50'
				AND
			unit = 'mcg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Timolol'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Timolol'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Amiloride'::text,
		'2.5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Amiloride'
				AND
			amount = '2.5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tinidazole'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tinidazole'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tolbutamide'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tolbutamide'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tramadol'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tramadol'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tramadol'::text,
		'50'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tramadol'
				AND
			amount = '50'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tranexamic Acid'::text,
		'250'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tranexamic Acid'
				AND
			amount = '250'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tranexamic Acid'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tranexamic Acid'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Tranexamic Acid'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Tranexamic Acid'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Triazolam'::text,
		'0.25'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Triazolam'
				AND
			amount = '0.25'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Trifluroperazine'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Trifluroperazine'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Trypsin-Chymotrypsin'::text,
		'100000'::numeric,
		'iu'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Trypsin-Chymotrypsin'
				AND
			amount = '100000'
				AND
			unit = 'iu'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Ursodeoxycholic Acid'::text,
		'150'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Ursodeoxycholic Acid'
				AND
			amount = '150'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Valciclovir'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Valciclovir'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Valdecoxib'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Valdecoxib'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Verapamil'::text,
		'40'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Verapamil'
				AND
			amount = '40'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Verapamil'::text,
		'80'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Verapamil'
				AND
			amount = '80'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vincamine Sr'::text,
		'30'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vincamine Sr'
				AND
			amount = '30'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin A'::text,
		'100000'::numeric,
		'iu'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin A'
				AND
			amount = '100000'
				AND
			unit = 'iu'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin A'::text,
		'200000'::numeric,
		'iu'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin A'
				AND
			amount = '200000'
				AND
			unit = 'iu'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin B12'::text,
		'1000'::numeric,
		'mcg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin B12'
				AND
			amount = '1000'
				AND
			unit = 'mcg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin C Effevacent'::text,
		'1000'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin C Effevacent'
				AND
			amount = '1000'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin C'::text,
		'500'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin C'
				AND
			amount = '500'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin E Antioxidant'::text,
		'400'::numeric,
		'iu'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin E Antioxidant'
				AND
			amount = '400'
				AND
			unit = 'iu'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin E'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin E'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin E'::text,
		'400'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin E'
				AND
			amount = '400'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Vitamin K'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Vitamin K'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Warfarin'::text,
		'3'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Warfarin'
				AND
			amount = '3'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Warfarin'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Warfarin'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Zafirlucast'::text,
		'20'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Zafirlucast'
				AND
			amount = '20'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Zinc'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Zinc'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Copper'::text,
		'1'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Copper'
				AND
			amount = '1'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Zinc Gluconate'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Zinc Gluconate'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Zinc Gluconate'::text,
		'70'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Zinc Gluconate'
				AND
			amount = '70'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Zinc Sulphate'::text,
		'200'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Zinc Sulphate'
				AND
			amount = '200'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Zinc'::text,
		'15'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Zinc'
				AND
			amount = '15'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Zolpidem'::text,
		'10'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Zolpidem'
				AND
			amount = '10'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Phenytoin'::text,
		'100'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Phenytoin'
				AND
			amount = '100'
				AND
			unit = 'mg'
	);

INSERT INTO ref.consumable_substance (
	description,
	amount,
	unit
)	SELECT
		'Prednisolon'::text,
		'5'::numeric,
		'mg'::text
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.consumable_substance
		WHERE
			description = 'Prednisolon'
				AND
			amount = '5'
				AND
			unit = 'mg'
	);

-- --------------------------------------------------------------
commit;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-consumable_substance-data-vbanait.sql', 'Revision: 1.0');

-- ==============================================================
