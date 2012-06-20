-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .atcs_single_indication
comment on column clin.vacc_indication.atcs_single_indication is
	'The ATC codes for single-indication vaccines for this indication.';

alter table clin.vacc_indication
	add constraint vacc_indication_sane_single_atcs check (
		(atcs_single_indication is null)
			or
		array_upper(atcs_single_indication, 1) > 0
	);

-- --------------------------------------------------------------
-- .atcs_combi_indication
comment on column clin.vacc_indication.atcs_combi_indication is
	'The ATC codes for poly-indication vaccines including this indication.';

alter table clin.vacc_indication
	add constraint vacc_indication_sane_combi_atcs check (
		(atcs_combi_indication is null)
			or
		(array_upper(atcs_combi_indication, 1) > 0)
	);

-- --------------------------------------------------------------
-- rename a few indications
update clin.vacc_indication set
	description = 'coxiella burnetii (Q fever)',
	atcs_single_indication = array['J07AX']
where
	description = 'Coxiella burnetii';

update clin.vacc_indication set
	description = 'salmonella typhi (typhoid)',
	atcs_single_indication = array['J07AP01','J07AP02','J07AP03', 'J07AP10']
where
	description = 'salmonella typhi';

update clin.vacc_indication set
	description = 'varicella (chickenpox, shingles)',
	atcs_single_indication = array['J07BK01','J07BK02']
where
	description = 'varicella';

update clin.vacc_indication set
	description = 'influenza (seasonal)',
	atcs_single_indication = array['J07BB01','J07BB02','J07BB03']
where
	description = 'influenza';


-- add new ones
delete from clin.vacc_indication
where description in (
	'bacillus anthracis (Anthrax)',
 	'human papillomavirus',
	'rotavirus',
	'tuberculosis',
	'variola virus (smallpox)',
	'influenza (H1N1)'
);


insert into clin.vacc_indication (
	description,
	atcs_single_indication
) values (
	'bacillus anthracis (Anthrax)',
	array['J07AC01']
);

insert into clin.vacc_indication (
	description,
	atcs_single_indication
) values (
	'human papillomavirus',
	array['J07BM01','J07BM02']
);

insert into clin.vacc_indication (
	description,
	atcs_single_indication
) values (
	'rotavirus',
	array['J07BH01','J07BH02']
);

insert into clin.vacc_indication (
	description,
	atcs_single_indication
) values (
	'tuberculosis',
	array['J07AN01']
);

-- no ATC code available
insert into clin.vacc_indication (
	description
) values (
	'variola virus (smallpox)'
);

insert into clin.vacc_indication (
	description,
	atcs_single_indication
) values (
	'influenza (H1N1)',
	array['J07BB']
);


-- update existing ones
update clin.vacc_indication set
	atcs_single_indication = array['J07AE01', 'J07AE02'],
	atcs_combi_indication = array['J07AE51']
where
	description = 'cholera';

update clin.vacc_indication set
	atcs_single_indication = array['J07AF01']
where
	description = 'diphtheria';

update clin.vacc_indication set
	atcs_single_indication = array['J07AG01'],
	atcs_combi_indication = array['J07AG51','J07AG52','J07AG53']
where
	description = 'haemophilus influenzae b';

update clin.vacc_indication set
	atcs_single_indication = array['J07BC02'],
	atcs_combi_indication = array['J07BC20']
where
	description = 'hepatitis A';

update clin.vacc_indication set
	atcs_single_indication = array['J07BC01'],
	atcs_combi_indication = array['J07BC20']
where
	description = 'hepatitis B';

update clin.vacc_indication set
	atcs_single_indication = array['J07BA02']
where
	description = 'japanese B encephalitis';

update clin.vacc_indication set
	atcs_single_indication = array['J07BD01'],
	atcs_combi_indication = array['J07BD51','J07BD52','J07BD53','J07BD54']
where
	description = 'measles';

update clin.vacc_indication set
	atcs_single_indication = array['J07AH01']
where
	description = 'meningococcus A';

update clin.vacc_indication set
	atcs_single_indication = array['J07AH07']
where
	description = 'meningococcus C';

update clin.vacc_indication set
	atcs_single_indication = array['J07AH02']
where
	description = 'meningococcus W';

update clin.vacc_indication set
	atcs_single_indication = array['J07AH02']
where
	description = 'meningococcus Y';

update clin.vacc_indication set
	atcs_single_indication = array['J07BE01'],
	atcs_combi_indication = array['J07BJ51']
where
	description = 'mumps';

update clin.vacc_indication set
	atcs_single_indication = array['J07AJ01','J07AJ02'],
	atcs_combi_indication = array['J07AJ51','J07AJ52']
where
	description = 'pertussis';

update clin.vacc_indication set
	atcs_single_indication = array['J07AL01','J07AL02'],
	atcs_combi_indication = array['J07AL52']
where
	description = 'pneumococcus';

update clin.vacc_indication set
	atcs_single_indication = array['J07BF01','J07BF02','J07BF03']
where
	description = 'poliomyelitis';

update clin.vacc_indication set
	atcs_single_indication = array['J07BG01']
where
	description = 'rabies';

update clin.vacc_indication set
	atcs_single_indication = array['J07BJ01'],
	atcs_combi_indication = array['J07BJ51']
where
	description = 'rubella';

update clin.vacc_indication set
	atcs_single_indication = array['J07AM01'],
	atcs_combi_indication = array['J07AM51','J07AM52']
where
	description = 'tetanus';

update clin.vacc_indication set
	atcs_single_indication = array['J07BA01']
where
	description = 'tick-borne meningoencephalitis';

update clin.vacc_indication set
	atcs_single_indication = array['J07BL01']
where
	description = 'yellow fever';

update clin.vacc_indication set
	atcs_single_indication = array['J07AK01']
where
	description = 'yersinia pestis';

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-vacc_indication-dynamic.sql', 'Revision: 1.1');
