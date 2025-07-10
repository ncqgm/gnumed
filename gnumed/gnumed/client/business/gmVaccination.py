"""GNUmed vaccination related business objects.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import sys
import locale
import logging
import functools


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmMedication


_log = logging.getLogger('gm.vacc')

#============================================================
URL_vaccination_plan = 'http://www.rki.de/DE/Content/Infekt/EpidBull/Archiv/2017/Ausgaben/34_17.pdf?__blob=publicationFile'

# http://www.pei.de/cln_042/SharedDocs/Downloads/fachkreise/uaw/meldeboegen/b-ifsg-meldebogen,templateId=raw,property=publicationFile.pdf/b-ifsg-meldebogen.pdf
URL_vaccine_ADR_german_default = 'https://nebenwirkungen.pei.de'

#============================================================
# vaccine related code
#------------------------------------------------------------
_SQL_get_vaccine_fields = """SELECT * FROM ref.v_vaccines WHERE %s"""

class cVaccine(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one vaccine."""

	_cmd_fetch_payload = _SQL_get_vaccine_fields % "pk_vaccine = %s"
	_cmds_store_payload = [
		"""UPDATE ref.vaccine SET
				is_live = %(is_live)s,
				min_age = %(min_age)s,
				max_age = %(max_age)s,
				comment = gm.nullify_empty_string(%(comment)s),
				fk_drug_product = %(pk_drug_product)s,
				atc = %(atc_vaccine)s
			WHERE
				pk = %(pk_vaccine)s
					AND
				xmin = %(xmin_vaccine)s
			RETURNING
				xmin as xmin_vaccine
		"""
	]
	_updatable_fields = [
		'is_live',
		'min_age',
		'max_age',
		'comment',
		'pk_drug_product',
		'atc_vaccine'
	]

	#--------------------------------------------------------
	def format(self, *args, **kwargs):
		lines = []
		live = gmTools.bool2subst(self._payload['is_live'], _(' (live)'), '', ' <liveness error in DB>')
		if self._payload['pk_drug_product']:
			lines.append(_('"%s" [#%s]%s -- #%s') % (
				self._payload['vaccine'],
				self._payload['pk_vaccine'],
				live,
				gmTools.coalesce(self._payload['pk_drug_product'], '', '#%s')
			))
		else:
			lines.append(_('Generic vaccine%s [#%s]%s') % (
				gmTools.coalesce(self._payload['atc_vaccine'], '', ' "ATC:%s"'),
				self._payload['pk_vaccine'],
				live
			))
		lines.append(_(' Targets:'))
		lines.extend([ '  %s [ATC:%s]' % (i['l10n_indication'], i['atc_indication']) for i in self._payload['indications'] ])
		if self._payload['pk_drug_product']:
			lines.append(' %s%s%s' % (
				self._payload['l10n_preparation'],
				gmTools.coalesce(self._payload['atc_product'], '', ' [ATC:%s]'),
				gmTools.coalesce(self._payload['external_code'], '', ' [%s:%%s]' % self._payload['external_code_type'])
			))
		lines.append(_(' Age range: %s - %s') % (
			gmDateTime.format_interval(interval = self._payload['min_age'], accuracy_wanted = gmDateTime.ACC_MONTHS, none_string = ''),
			gmDateTime.format_interval(interval = self._payload['max_age'], accuracy_wanted = gmDateTime.ACC_MONTHS, none_string = '')
		))
		if self._payload['comment'] is not None:
			lines.extend([ ' %s' % l for l in self._payload['comment'].split('\n')] )
		return lines

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_product(self):
		if self._payload['pk_drug_product']:
			return gmMedication.cDrugProduct(aPK_obj = self._payload['pk_drug_product'])

		return None

	product = property(_get_product)

	#--------------------------------------------------------
	def _get_is_in_use(self):
		cmd = 'SELECT EXISTS(SELECT 1 FROM clin.vaccination WHERE fk_vaccine = %(pk)s)'
		args = {'pk': self._payload['pk_vaccine']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows[0][0]

	is_in_use = property(_get_is_in_use)

	#--------------------------------------------------------
	# indications handling
	#--------------------------------------------------------
	@staticmethod
	def atcs2indication_pks(atcs:list[str]=None) -> list[int]:
		query = {
			'sql': 'SELECT pk FROM ref.vacc_indication WHERE atc = ANY(%(atcs)s)',
			'args': {'atcs': atcs}
		}
		rows = gmPG2.run_ro_queries(queries = [query])
		if len(atcs) != len(rows):		# all mapped ?
			_log.error('cannot map all ATCs to vaccine indications')
			_log.error('ATCs: %s', atcs)
			return None

		return [ r['pk'] for r in rows ]

	#--------------------------------------------------------
	@staticmethod
	def targets2indication_pks(targets:list[str]=None) -> list[int]:
		query = {
			'sql': 'SELECT pk FROM ref.vacc_indication WHERE atc = ANY(%(targets)s)',
			'args': {'targets': targets}
		}
		rows = gmPG2.run_ro_queries(queries = [query])
		if len(targets) != len(rows):
			return None

		return [ r['pk'] for r in rows ]

	#--------------------------------------------------------
	def add_indication(self, pk_indication:int=None, atc:str=None, indication:str=None):
		args:dict[str,str]|dict[str,int]
		if not pk_indication:
			args = {
				'atc': atc,
				'indication': indication
			}
			if atc:
				SQL = 'SELECT pk FROM ref.vacc_indication WHERE atc = %(atc)s'
			elif indication:
				SQL = 'SELECT pk FROM ref.vacc_indication WHERE target = %(indication)s'
			else:
				_log.error('neither <pk_indication>, nor <atc>, nor <indication> given')
				return False

			rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
			if not rows:
				_log.error('indication [%s: %s] does not exist', atc, indication)
				return False

			pk_indication = rows[0]['pk']

		args = {
			'pk_ind': pk_indication,
			'pk_vacc': self._payload['pk_vaccine']
		}
		SQL = """
		INSERT INTO ref.lnk_indic2vaccine (fk_indication, fk_vaccine)
			SELECT %(pk_ind)s, %(pk_vacc)s WHERE NOT EXISTS (
				SELECT 1 FROM ref.lnk_indic2vaccine WHERE fk_indication %(pk_ind)s = AND fk_vaccine = %(pk_vacc)s
			)
		"""
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])
		return True

	#--------------------------------------------------------
	def remove_indication(self, pk_indication:int=None):
		args = {
			'pk_ind': pk_indication,
			'pk_vacc': self._payload['pk_vaccine']
		}
		SQL = 'DELETE FROM ref.lnk_indic2vaccine WHERE fk_indication %(pk_ind)s = AND fk_vaccine = %(pk_vacc)s'
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])

	#--------------------------------------------------------
	def remove_indications(self):
		args = {'pk_vacc': self._payload['pk_vaccine']}
		SQL = 'DELETE FROM ref.lnk_indic2vaccine WHERE fk_vaccine = %(pk_vacc)s'
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])

	#--------------------------------------------------------
	def set_indications(self, pk_indications:list[int]=None) -> bool:
		if not pk_indications:
			return False

		if set(pk_indications) == set([ ind['pk_indication'] for ind in self._payload['indications'] ]):
			# already the same
			return True

		queries = [{
			'sql': 'DELETE FROM ref.lnk_indic2vaccine WHERE fk_vaccine = %(pk_vacc)s',
			'args': {'pk_vacc': self._payload['pk_vaccine']}
		}]
		for pk_ind in set(pk_indications):		# remove dupes
			queries.append ({
				'sql': 'INSERT INTO ref.lnk_indic2vaccine (fk_indication, fk_vaccine) VALUES (%(pk_ind)s, %(pk_vacc)s)',
				'args': {'pk_ind': pk_ind, 'pk_vacc': self._payload['pk_vaccine']}
			})
		gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()
		return True

#------------------------------------------------------------
def create_vaccine_dummy_dose(link_obj=None) -> int:
	# brands require a component, so:
	SQL = """-- INSERT dummy vaccine substance
	INSERT INTO ref.substance (description, atc)
		SELECT %(subst)s, %(atc)s
		WHERE NOT EXISTS (
			SELECT 1 FROM ref.substance WHERE description = %(subst)s AND atc = %(atc)s
		);
	-- INSERT dummy vaccine dose
	INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
		SELECT
			(SELECT pk FROM ref.substance WHERE description = %(subst)s AND atc = %(atc)s),
			1, %(unit)s, %(dose_unit)s
		WHERE NOT EXISTS (
			SELECT 1 FROM ref.dose WHERE fk_substance = (
				SELECT pk FROM ref.substance WHERE description = %(subst)s AND atc = %(atc)s
			)
		);
	SELECT pk FROM ref.dose WHERE fk_substance = (
		SELECT pk FROM ref.substance WHERE description = %(subst)s AND atc = %(atc)s
	);
	"""
	args = {
		'subst': 'vaccine',
		'atc': 'J07',
		'unit': 'dose',
		'dose_unit': 'shot'
	}
	rows = gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}], link_obj = link_obj, return_data = True)
	return rows[0]['pk']

#------------------------------------------------------------
def create_vaccine(pk_drug_product=None, product_name=None, is_live=None):
	# force caller to make a decision, which is hoped
	# to bubble up towards the end user ;-)
	assert (is_live is not None), '<is_live> must not be <None>'

	conn = gmPG2.get_connection(readonly = False)
	dose = create_vaccine_dummy_dose(link_obj = conn)
	if not pk_drug_product:
		if product_name:
			_log.debug('creating vaccine drug product [%s]', product_name)
			vacc_prod = gmMedication.create_drug_product (
				product_name = product_name,
				preparation = 'vaccine',
				return_existing = True,
				pk_doses = [dose],
				link_obj = conn
			)
			pk_drug_product = vacc_prod['pk_drug_product']
	if pk_drug_product:
		SQL = 'INSERT INTO ref.vaccine (fk_drug_product, is_live) values (%(pk_drug_product)s, %(live)s) RETURNING pk'
	else:
		SQL = 'INSERT INTO ref.vaccine (is_live) values (%(live)s) RETURNING pk'
	args = {
		'pk_drug_product': pk_drug_product,
		'live': is_live
	}
	queries = [{'sql': SQL, 'args': args}]
	rows = gmPG2.run_rw_queries(link_obj = conn, queries = queries, return_data = True, end_tx = True)
	return cVaccine(aPK_obj = rows[0]['pk'], link_obj = conn)

#------------------------------------------------------------
def delete_vaccine(pk_vaccine:int=None, also_delete_product:bool=False) -> bool:
	args = {'pk_vacc': pk_vaccine, 'pk_drug': None}
	if also_delete_product:
		SQL = 'SELECT fk_drug_product FROM ref.vaccine WHERE pk = %(pk_vacc)s'
		q = {'sql': SQL, 'args': args}
		rows = gmPG2.run_ro_queries(queries = [q])
		if rows:
			args['pk_drug'] = rows[0]['fk_drug_product']
	queries = []
	SQL = 'DELETE FROM ref.lnk_indic2vaccine WHERE fk_vaccine = %(pk_vacc)s'
	queries.append({'sql': SQL, 'args': args})
	SQL = 'DELETE FROM ref.vaccine WHERE pk = %(pk_vacc)s'
	queries.append({'sql': SQL, 'args': args})
	if args['pk_drug']:
		SQL = 'DELETE FROM ref.lnk_dose2drug WHERE fk_drug_product = %(pk_drug)s'
		queries.append({'sql': SQL, 'args': args})
		SQL = 'DELETE FROM ref.drug_product WHERE pk = %(pk_drug)s'
		queries.append({'sql': SQL, 'args': args})
	try:
		gmPG2.run_rw_queries(queries = queries)
	except gmPG2.dbapi.IntegrityError:
		_log.exception('cannot delete vaccine [#%s]', pk_vaccine)
		return False

	return True

#------------------------------------------------------------
def get_vaccines(order_by=None, return_pks=False):

	if order_by is None:
		cmd = _SQL_get_vaccine_fields % 'TRUE'
	else:
		cmd = _SQL_get_vaccine_fields % ('TRUE\nORDER BY %s' % order_by)

	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_vaccine'] for r in rows ]
	return [ cVaccine(row = {'data': r, 'pk_field': 'pk_vaccine'}) for r in rows ]

#------------------------------------------------------------
def get_vaccination_indications(order_by:str=None):
	SQL = 'SELECT * from ref.vacc_indication'
	if order_by:
		SQL += ' ORDER BY %s' % order_by
	rows = gmPG2.run_ro_query(sql = SQL)
	return rows

#============================================================
# vaccination related classes
#============================================================
_SQL_get_vaccination_fields = """SELECT * FROM clin.v_vaccinations WHERE %s"""

class cVaccination(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_vaccination_fields % "pk_vaccination = %s"

	_cmds_store_payload = [
		"""UPDATE clin.vaccination SET
				soap_cat = %(soap_cat)s,
				clin_when = %(date_given)s,
				site = gm.nullify_empty_string(%(site)s),
				batch_no = gm.nullify_empty_string(%(batch_no)s),
				reaction = gm.nullify_empty_string(%(reaction)s),
				narrative = gm.nullify_empty_string(%(comment)s),
				fk_vaccine = %(pk_vaccine)s,
				fk_provider = %(pk_provider)s,
				fk_encounter = %(pk_encounter)s,
				fk_episode = %(pk_episode)s
			WHERE
				pk = %(pk_vaccination)s
					AND
				xmin = %(xmin_vaccination)s
			RETURNING
				xmin as xmin_vaccination
		"""
	]

	_updatable_fields = [
		'soap_cat',
		'date_given',
		'site',
		'batch_no',
		'reaction',
		'comment',
		'pk_vaccine',
		'pk_provider',
		'pk_encounter',
		'pk_episode'
	]

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		return self.format (
			with_indications = True,
			with_comment = True,
			with_reaction = True,
			date_format = '%Y %b %d'
		)

	#--------------------------------------------------------
	def format(self, with_indications=False, with_comment=False, with_reaction=False, date_format='%Y-%m-%d'):

		lines = []

		lines.append (' %s: %s [%s]%s' % (
			self._payload['date_given'].strftime(date_format),
			self._payload['vaccine'],
			self._payload['batch_no'],
			gmTools.coalesce(self._payload['site'], '', ' (%s)')
		))

		if with_comment:
			if self._payload['comment'] is not None:
				lines.append('   %s' % self._payload['comment'])

		if with_reaction:
			if self._payload['reaction'] is not None:
				lines.append('   %s' % self._payload['reaction'])

		if with_indications:
			lines.append('   %s' % ' / '.join([ i['l10n_indication'] for i in self._payload['indications'] ]))

		return lines

	#--------------------------------------------------------
	def format_for_failsafe_output(self, max_width:int=80) -> list[str]:
		lines = []
		lines.append(gmTools.shorten_text(
			'%s: %s [%s]%s' % (
				self._payload['date_given'].strftime('%Y %b %d'),
				self._payload['vaccine'],
				self._payload['batch_no'],
				gmTools.coalesce(self._payload['site'], '', ' (%s)')
			),
			max_width
		))
		lines.append('  ' + _('Indications: %s') % ' / '.join([ i['l10n_indication'] for i in self._payload['indications'] ]))
		if self._payload['comment']:
			lines.append(gmTools.shorten_text('  ' + self._payload['comment'], max_width))
		if self._payload['reaction']:
			lines.append(gmTools.shorten_text('  ' + self._payload['reaction'], max_width))
		return lines

	#--------------------------------------------------------
	def _get_vaccine(self):
		return cVaccine(aPK_obj = self._payload['pk_vaccine'])

	vaccine = property(_get_vaccine)

#------------------------------------------------------------
def get_vaccinations(pk_identity=None, pk_episodes=None, pk_health_issues=None, pk_encounters=None, order_by=None, return_pks=False):

	args = {}
	where_parts = []

	if pk_identity is not None:
		args = {'pk_identity': pk_identity}
		where_parts.append('pk_patient = %(pk_identity)s')

	if (pk_episodes is not None) and (len(pk_episodes) > 0):
		where_parts.append('pk_episode = ANY(%(pk_epis)s)')
		args['pk_epis'] = pk_episodes

	if (pk_health_issues is not None) and (len(pk_health_issues) > 0):
		where_parts.append('pk_episode = ANY(SELECT pk FROM clin.episode WHERE fk_health_issue = ANY(%(pk_issues)s))')
		args['pk_issues'] = pk_health_issues

	if (pk_encounters is not None) and (len(pk_encounters) > 0):
		where_parts.append('pk_encounter = ANY(%(pk_encs)s)')
		args['pk_encs'] = pk_encounters

	ORDER_BY = gmTools.coalesce (
		value2test = order_by,
		return_instead = '',
		value2return = 'ORDER BY %s' % order_by
	)
	if len(where_parts) == 0:
		WHERE = 'True'
	else:
		WHERE = '\nAND '.join(where_parts)

	SQL = '%s %s' % (
		_SQL_get_vaccination_fields % WHERE,
		ORDER_BY
	)
	rows = gmPG2.run_ro_query(sql = SQL, args = args)
	if return_pks:
		return [ r['pk_vaccination'] for r in rows ]

	vaccs = [ cVaccination(row = {'data': r, 'pk_field': 'pk_vaccination'}) for r in rows ]
	return vaccs

#------------------------------------------------------------
def format_vaccinations_by_indication_for_failsafe_output(pk_patient:int, max_width:int=80) -> list[str]:
	shots = get_vaccinations(pk_identity = pk_patient)
	if not shots:
		return []

	shots_by_ind:dict[str, list[cVaccination]] = {}
	for shot in shots:
		inds = shot['indications']
		for ind in inds:
			try:
				shots_by_ind[ind['l10n_indication']]
			except KeyError:
				shots_by_ind[ind['l10n_indication']] = []
			shots_by_ind[ind['l10n_indication']].append(shot)
	lines = []
	l10n_inds_sorted = sorted(shots_by_ind.keys(), key = functools.cmp_to_key(locale.strcoll))
	for ind in l10n_inds_sorted:
		lines.append('')
		lines.append(_('Indication: %s') % ind)
		shots4ind = sorted(shots_by_ind[ind], key = lambda d: d['date_given'], reverse = True)
		for shot in shots4ind:
			lines.append(gmTools.shorten_text (
				'  %s: %s [%s]' % (
					shot['date_given'].strftime('%Y %b %d'),
					shot['vaccine'],
					shot['batch_no']
				),
				max_width
			))
			if shot['comment']:
				lines.append(gmTools.shorten_text('   ' + shot['comment'], max_width))
			if shot._payload['reaction']:
				lines.append(gmTools.shorten_text('   ' + shot['reaction'], max_width))
	return lines

#------------------------------------------------------------
def create_vaccination(encounter:int=None, episode:int=None, pk_vaccine:int=None, batch_no:str=None):
	cmd = """
		INSERT INTO clin.vaccination (
			fk_encounter,
			fk_episode,
			fk_vaccine,
			batch_no
		) VALUES (
			%(enc)s,
			%(epi)s,
			%(pk_vacc)s,
			%(batch)s
		) RETURNING pk;
	"""
	args = {
		'enc': encounter,
		'epi': episode,
		'pk_vacc': pk_vaccine,
		'batch': batch_no
	}
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
	return cVaccination(aPK_obj = rows[0][0])

#------------------------------------------------------------
def delete_vaccination(vaccination=None):
	SQL = 'DELETE FROM clin.vaccination WHERE pk = %(pk)s'
	args = {'pk': vaccination}
	gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])

#------------------------------------------------------------
def format_latest_vaccinations(output_format='latex', emr=None):

	_log.debug('formatting latest vaccinations into [%s]', output_format)

	vaccs = emr.get_latest_vaccinations()

	if output_format == 'latex':
		return __format_latest_vaccinations_latex(vaccinations = vaccs)

	msg = _('unknown vaccinations output format [%s]') % output_format
	_log.error(msg)
	return msg

#------------------------------------------------------------
def __format_latest_vaccinations_latex(vaccinations=None):

	if not vaccinations:
		return '\\noindent %s' % gmTools.tex_escape_string(_('No vaccinations recorded.'))

	tex =  '\\noindent %s {\\tiny (%s)\\par}\n' % (
		gmTools.tex_escape_string(_('Latest vaccinations')),
		gmTools.tex_escape_string(_('per target condition'))
	)
	tex += '\n'
	tex += '\\noindent \\begin{tabular}{|l|l|l|l|l|l|}\n'
	tex += '\\hline\n'
	tex += '%s & %s & {\\footnotesize %s} & {\\footnotesize %s} & {\\footnotesize %s\\footnotemark} & {\\footnotesize $\\Sigma$\\footnotemark}\\\\\n' % (
		gmTools.tex_escape_string(_('Target')),
		gmTools.tex_escape_string(_('Last given')),
		gmTools.tex_escape_string(_('Vaccine')),
		gmTools.tex_escape_string(_('Lot #')),
		gmTools.tex_escape_string(_('SoaP'))
	)
	tex += '\\hline\n'
	tex += '\n'
	tex += '\\hline\n'
	tex += '%s'			# this is where the actual vaccination rows end up
	tex += '\n'
	tex += '\\end{tabular}\n'
	tex += '\n'
	tex += '\\addtocounter{footnote}{-1}\n'
	tex += '\\footnotetext{%s}\n' % gmTools.tex_escape_string (
		_('SoaP -- "S"ubjective: Reported. "P"lan: Administered here/taken from trustworthy records.')
	)
	tex += '\\addtocounter{footnote}{1}\n'
	tex += '\\footnotetext{$\\Sigma$ -- %s}\n' % gmTools.tex_escape_string (
		_('Total number of vaccinations recorded for the corresponding target condition.')
	)
	tex += '\n'
	row_template = '%s & %s & {\\scriptsize %s} & {\\scriptsize %s} & {\\scriptsize %s} & {\\scriptsize %s}\\\\\n'
	lines = ''
	targets = sorted(vaccinations)
	for target in targets:
		target_count, vacc = vaccinations[target]
		lines += row_template % (
			gmTools.tex_escape_string(target),
			gmTools.tex_escape_string(vacc['date_given'].strftime('%Y %b %d')),
			gmTools.tex_escape_string(gmTools.coalesce(vacc['vaccine'], _('generic'))),
			gmTools.tex_escape_string(vacc['batch_no']),
			vacc['soap_cat'].upper(),
			target_count
		)
		if vacc['site']:
			tag = gmTools.tex_escape_string(_('Injection site'))
			site = gmTools.tex_escape_string(vacc['site'])
			lines += ' & \\multicolumn{5}{l|}{\\scriptsize %s: %s\\par}\\\\\n' % (tag, site)
		if vacc['reaction']:
			tag = gmTools.tex_escape_string(_('Reaction'))
			reaction = gmTools.tex_escape_string(vacc['reaction'])
			lines += ' & \\multicolumn{5}{l|}{\\scriptsize %s: %s\\par}\\\\\n' % (tag, reaction)
		if vacc['comment']:
			tag = gmTools.tex_escape_string(_('Comment'))
			cmt = gmTools.tex_escape_string(vacc['comment'])
			lines += ' & \\multicolumn{5}{l|}{\\scriptsize %s: %s\\par}\\\\\n' % (tag, cmt)
		lines += '\\hline\n'
	return tex % lines

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

#	from Gnumed.pycommon import gmPG
	#--------------------------------------------------------
	def test_vacc():
		vacc = cVaccination(aPK_obj=1)
		print(vacc)
		fields = vacc.get_fields()
		for field in fields:
			print(field, ':', vacc[field])
		print("updatable:", vacc.get_updatable_fields())

#	#--------------------------------------------------------
#	def test_due_vacc():
#		# Test for a due vaccination
#		pk_args = {
#			'pat_id': 12,
#			'indication': 'meningococcus C',
#			'seq_no': 1
#		}
#		missing_vacc = cMissingVaccination(aPK_obj=pk_args)
#		fields = missing_vacc.get_fields()
#		print("\nDue vaccination:")
#		print(missing_vacc)
#		for field in fields:
#			print(field, ':', missing_vacc[field])
#		# Test for an overdue vaccination
#		pk_args = {
#			'pat_id': 12,
#			'indication': 'haemophilus influenzae b',
#			'seq_no': 2
#		}
#		missing_vacc = cMissingVaccination(aPK_obj=pk_args)
#		fields = missing_vacc.get_fields()
#		print("\nOverdue vaccination (?):")
#		print(missing_vacc)
#		for field in fields:
#			print(field, ':', missing_vacc[field])

#	#--------------------------------------------------------
#	def test_due_booster():
#		pk_args = {
#			'pat_id': 12,
#			'indication': 'tetanus'
#		}
#		missing_booster = cMissingBooster(aPK_obj=pk_args)
#		fields = missing_booster.get_fields()
#		print("\nDue booster:")
#		print(missing_booster)
#		for field in fields:
#			print(field, ':', missing_booster[field])

	#--------------------------------------------------------
#	def test_scheduled_vacc():
#		scheduled_vacc = cScheduledVaccination(aPK_obj=20)
#		print("\nScheduled vaccination:")
#		print(scheduled_vacc)
#		fields = scheduled_vacc.get_fields()
#		for field in fields:
#			print(field, ':', scheduled_vacc[field])
#		print("updatable:", scheduled_vacc.get_updatable_fields())

#	#--------------------------------------------------------
#	def test_vaccination_course():
#		vaccination_course = cVaccinationCourse(aPK_obj=7)
#		print("\nVaccination course:")
#		print(vaccination_course)
#		fields = vaccination_course.get_fields()
#		for field in fields:
#			print(field, ':', vaccination_course[field])
#		print("updatable:", vaccination_course.get_updatable_fields())

	#--------------------------------------------------------
#	def test_put_patient_on_schedule():
#		result, msg = put_patient_on_schedule(patient_id=12, course_id=1)
#		print('\nPutting patient id 12 on schedule id 1... %s (%s)' % (result, msg))

	#--------------------------------------------------------
	def test_get_vaccines():
		for vaccine in get_vaccines():
			print('--------------------------------')
			print('\n'.join(vaccine.format()))

	#--------------------------------------------------------
	def test_get_vaccinations():
		#v1 = get_vaccinations(return_pks = True, order_by = 'date_given')
		#print(v1)
		for v in get_vaccinations(order_by = 'date_given, vaccine'):
			print('\n'.join(v.format()))
			#print('\n'.join(v.format_for_failsafe_output()))

	#--------------------------------------------------------
	def test_format_vaccs_failsafe():
		print('\n'.join(format_vaccinations_by_indication_for_failsafe_output(pk_patient = 12)))

	#--------------------------------------------------------
	def test_create_vaccine_dummy_dose():
		print(create_vaccine_dummy_dose())

	#--------------------------------------------------------
	def test_format_latest_vaccinations():
		from Gnumed.business import gmPraxis
		gmPraxis.gmCurrentPraxisBranch.from_first_branch()
		from Gnumed.business import gmClinicalRecord
		emr = gmClinicalRecord.cClinicalRecord(12)
		shots = emr.latest_vaccinations
		#shots = get_vaccinations(pk_identity = 12, return_pks = False)
		print(__format_latest_vaccinations_latex(vaccinations = shots))

	#--------------------------------------------------------
	def test_create_vaccination():
		print(create_vaccination (
			encounter = 1,
			episode = 1,
			pk_vaccine = 204,
			batch_no = 'testing create_vaccination()'
		))

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)
	#test_vaccination_course()
	#test_put_patient_on_schedule()
	#test_scheduled_vacc()
	#test_vacc()
	#test_due_vacc()
	#test_due_booster()

	#test_get_vaccines()
	#test_get_vaccinations()
	#test_format_latest_vaccinations()
	#test_format_vaccs_failsafe()
	#test_create_vaccine_dummy_dose()
	test_create_vaccination()
