
\unset ON_ERROR_STOP
drop schema oscar cascade;
\set ON_ERROR_STOP 1

create schema oscar authorization "gm-dbo";

create table oscar.country (
	country varchar(2)
		primary key
);
insert into oscar.country values ('AU');

create table oscar.oscar_to_gnumed_types (
	oscar text,
	gnumed text,
	country varchar(2)
		references oscar.country
);
create unique index idx_oscar_to_gnumed_types on oscar.oscar_to_gnumed_types (oscar, gnumed, country);
insert into oscar.oscar_to_gnumed_types (oscar, gnumed, country) values ('hin', 'Medicare', 'AU');
insert into oscar.oscar_to_gnumed_types (oscar, gnumed, country) values ('chart_no', 'ur_no', 'AU');

create view oscar.demographic as 
select 
	pk_identity as demographic_no , 
	lastnames as last_name, 
	firstnames as first_name , 
	gender as sex, 
	to_char(dob, 'YYYY') as year_of_birth  , 
	to_char(dob, 'MM') as month_of_birth, 
	to_char(dob, 'DD') as date_of_birth  , 
	number || ', '|| street as address,
	urb as city, 
	state as province, 
	postcode as postal,
	phone,
	phone2,
	hin,
	chart_no,
	''::text as roster_status,
	''::text as patient_status,
	''::text as provider_no
from 
	(select *
	from 
		dem.v_basic_person p, 
		dem.v_basic_address a , 
		dem.lnk_person2address lpa 
		where 
			p.pk_identity = lpa.id_identity and
			a.id = lpa.id_address
	) i1   

		left outer join 

	(select 
		url as phone, id_identity  
	from 
		dem.lnk_identity2comm c2a 
	where 
		c2a.id_type = 
			(select id from dem.enum_comm_types ect1 where ect1.description='homephone') 
	) c2 on c2.id_identity = i1.pk_identity 

		left outer join 

	(select 
		url as phone2, id_identity 
	from 
	dem.lnk_identity2comm c2b 
		where 
			c2b.id_type = 
				(select id from dem.enum_comm_types ect where ect.description ='mobile') 
	) c3 on c3.id_identity = i1.pk_identity 

	left outer join 

	(select 
		external_id as hin, id_identity 
	from 
		dem.lnk_identity2ext_id  li1 
	where 
		li1.fk_origin = ( 
			select pk
			from dem.enum_ext_id_types 
			where name = (
				select gnumed
				from oscar.oscar_to_gnumed_types t1 
				where
					t1.oscar = 'hin' and 
					t1.country = (select country from oscar.country limit 1) 
				)
		)
	) li2 on li2.id_identity = i1.pk_identity
	
	left outer join

	(select external_id as chart_no , id_identity
	from 
		dem.lnk_identity2ext_id li3
	where
		li3.fk_origin = ( 
			select pk
			from dem.enum_ext_id_types
			where
				name = (
					select gnumed
					from oscar.oscar_to_gnumed_types t1
					where
						t1.oscar = 'chart_no' and t1.country = (select country from oscar.country limit 1)
				)
		)
	) li3 on li3.id_identity = i1.pk_identity

;

grant select on oscar.demographic to group "gm-doctors";
