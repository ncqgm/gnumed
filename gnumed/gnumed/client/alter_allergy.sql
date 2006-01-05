 alter table clin.allergy add severe boolean default false;
 alter table clin.allergy add clin_coding integer[];
 alter table clin.allergy add clin_coding_scheme text default null;
 alter table clin.allergy add sensitivity boolean default false;

