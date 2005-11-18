-- Project: GnuMed - service "configuration" -- Australian specific stuff
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/gmconfiguration.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- author: Ian Haywood

-- Populates configuration tables for AU values

insert into cfg.cfg_template (name, type, description) values ('main.comms.print', 'string', 'Print command');
insert into cfg.cfg_item (fk_template, owner) values (currval ('cfg.cfg_template_pk_seq'), 'xxxDEFAULTxxx');
insert into cfg.cfg_string (fk_item, value) values (currval ('cfg.cfg_item_pk_seq'), 'lpr');

insert into cfg.cfg_template (name, type, description) values ('main.comms.paper_referral', 'string', 'Name of standard referral form');
insert into cfg.cfg_item (fk_template, owner) values (currval ('cfg.cfg_template_pk_seq'), 'xxxDEFAULTxxx');
insert into cfg.cfg_string (fk_item, value) values (currval ('cfg.cfg_item_pk_seq'), 'Standard Referral');

insert into cfg.cfg_template (name, type, description) values ('main.comms.fax', 'string', 'Fax sending command');
insert into cfg.cfg_item (fk_template, owner) values (currval ('cfg.cfg_template_pk_seq'), 'xxxDEFAULTxxx');
insert into cfg.cfg_string (fk_item, value) values (currval ('cfg.cfg_item_pk_seq'), 'lpr -P fax -J %N');

insert into cfg.cfg_template (name, type, description) values ('main.comms.email_referral', 'string', 'Form template for e-mail referral');
insert into cfg.cfg_item (fk_template, owner) values (currval ('cfg.cfg_template_pk_seq'), 'xxxDEFAULTxxx');
insert into cfg.cfg_string (fk_item, value) values (currval ('cfg.cfg_item_pk_seq'), 'Email Referral');

insert into cfg.cfg_template (name, type, description) values ('main.comms.email', 'string', 'E-mail sending command');
insert into cfg.cfg_item (fk_template, owner) values (currval ('cfg.cfg_template_pk_seq'), 'xxxDEFAULTxxx');
insert into cfg.cfg_string (fk_item, value) values (currval ('cfg.cfg_item_pk_seq'), 'kmail --to %R --from %S --attach %F --subject Referral'); -- FIXME
