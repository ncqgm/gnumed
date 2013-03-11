-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
INSERT INTO dem.message_inbox (
	fk_staff,
	fk_inbox_item_type,
	comment,
	data
) VALUES (
	(select pk from dem.staff where db_user = 'any-doc'),
	(select pk_type from dem.v_inbox_item_type where type = 'memo' and category = 'administrative'),
	'Release Notes for GNUmed 1.3.0 (database v18.0)',
	'GNUmed 1.3.0 Release Notes:

	1.3.0

NEW: visualize the EMR using TheTimelineProject
NEW: placeholder $<patient_photo>$
NEW: DEGAM UTI 2012 guideline
NEW: status line in each edit area
NEW: Xe(La)TeX based forms engine
NEW: plain text based/generic postprocessing forms engine
NEW: placeholder $<text_snippet>$ operating on keyword expansions
NEW: encryptable placeholder $<data_snippet>$
NEW: look for installed plugins list in config files, too
NEW: medical staff vs non-medical staff permissions handling
NEW: generic gmTextCtrl supporting keyword expansion macros
NEW: current substances grid: generate Rx either from DB or from form template
NEW: GVK-Rezept prescription template (darf in D nicht verwendet werden)
NEW: revamped measurements handling including test panels
NEW: placeholder $<soap_by_issue>$, selecting SOAP via issues list
NEW: placeholder $<soap_by_episode>$, selecting SOAP via episodes list
NEW: progress notes can now be created from EMR tree
NEW: score: Bird Criteria for Polymyalgia rheumatica
NEW: score: prediction of bacterial conjunctivitis
NEW: placeholder $<documents>$, include/export documents
NEW: list placeholders from within client
NEW: show (e)GFR in substance intake EA
NEW: placeholder $<test_results>$, selecting test results from list
NEW: Epworth Sleepiness Scale
NEW: placeholder $<reminders>$ for messages with due date

IMPROVED: document tree: better labels, tooltips added
IMPROVED: measurement EA: show most recent value of test type
IMPROVED: measurement EA: plot adjacent results upon saving
IMPROVED: support a comment on bills
IMPROVED: EMR tree: load data when expanding nodes
IMPROVED: vaccinations list: print vaccinations via template
IMPROVED: better dynamic text expansion dialog
IMPROVED: drug component PRW: disambiguate which drug will be picked
IMPROVED: waiting list: filter by active patient
IMPROVED: report generator: be smarter about patient ID columns
IMPROVED: patient overview: display last modified of occupation
IMPROVED: substances grid: show preparation of items
IMPROVED: placeholder $<current_meds>$ can let user select entries
IMPROVED: measurements grid labels
IMPROVED: (Xe)(La)TeX forms engine recursively substitutes placeholders
IMPROVED: address: street/subunit level comment can now be removed
IMPROVED: do not loose has_allergy=True on merging patients
IMPROVED: health issue EA: safer workflow
IMPROVED: SOAP plugin: improved selection of most-recent information
IMPROVED: EMR tree browser: display entire EMR as journal
IMPROVED: placeholder handler: always properly escape data based on target form engine
IMPROVED: depreciate gmNotebookedProgressNoteInputPlugin from "GNUmed Default" workplace
IMPROVED: EMR Journal: order grouped by encounter or order by last modified of items
IMPROVED: SimpleSoap plugin: enable keyword based text expansions
IMPROVED: patient overview: show comment on contact in tooltip
IMPROVED: waiting list entry double-click workflow [thanks J.Busser]
IMPROVED: database translation contribution code
IMPROVED: login dialog help text [thanks J.Busser]
IMPROVED: patient searcher logic [thanks J.Busser]
IMPROVED: non-overdue recalls display in patient overview
IMPROVED: provider inbox: much improved workflow

	18.0

IMRPOVED: add missing PKs to cfg.cfg_* tables for Bucardo use [thanks Marc]
IMPROVED: include PK columns in schema version check
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.0');
