-- Project: GnuMed - service "configuration" -- Australian specific stuff
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/gmconfiguration.sql,v $
-- $Revision: 1.1 $
-- license: GPL
-- author: Ian Haywood

-- Populates configuration tables for AU values

insert into cfg_template (name, type, description) values ('main.comms.print', 'string', 'Print command');
insert into cfg_item (id_template, owner) values (currval ('cfg_template_id_seq'), 'xxxDEFAULTxxx');
insert into cfg_string (id_item, value) values (currval ('cfg_item_id_seq'), 'lpr');

insert into cfg_template (name, type, description) values ('main.comms.paper_referral', 'string', 'Name of standard referral form');
insert into cfg_item (id_template, owner) values (currval ('cfg_template_id_seq'), 'xxxDEFAULTxxx');
insert into cfg_string (id_item, value) values (currval ('cfg_item_id_seq'), 'Standard Referral');

insert into cfg_template (name, type, description) values ('main.comms.fax', 'string', 'Fax sending command');
insert into cfg_item (id_template, owner) values (currval ('cfg_template_id_seq'), 'xxxDEFAULTxxx');
insert into cfg_string (id_item, value) values (currval ('cfg_item_id_seq'), 'lpr -P fax -J %N');

insert into cfg_template (name, type, description) values ('main.comms.email_referral', 'string', 'Form template for e-mail referral');
insert into cfg_item (id_template, owner) values (currval ('cfg_template_id_seq'), 'xxxDEFAULTxxx');
insert into cfg_string (id_item, value) values (currval ('cfg_item_id_seq'), 'Email Referral');

insert into cfg_template (name, type, description) values ('main.comms.email', 'string', 'E-mail sending command');
insert into cfg_item (id_template, owner) values (currval ('cfg_template_id_seq'), 'xxxDEFAULTxxx');
insert into cfg_string (id_item, value) values (currval ('cfg_item_id_seq'), 'kmail --to %R --from %S --attach %F --subject Referral'); -- FIXME
