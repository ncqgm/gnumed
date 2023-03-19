 CREATE index ix_pat_episodes on clin.episode using hash(fk_patient) where fk_patient <> null;
--this next one will take some time
create index ix_hash_pk_item_clin_narrative on clin.clin_narrative using hash(pk_item);

create index ix_hash_health_issue_episode on clin.episode using hash( fk_health_issue);

CREATE index ix_hash_id_patient_health_issue on clin.health_issue using hash( id_patient);

CREATE index idx_hash_episode_issue on clin.episode using hash(fk_health_issue);

