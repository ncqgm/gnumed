#!/usr/bin/env python

import string, re

def generate_queries(raw):

	queries = []

	# "+<...>" - DOD date of death
	if re.match("^(\s|\t)*\+.+$", raw):
		print "supposedly d.o.d."
		print " will return:"
		print "  1) patient based on d.o.d."
		print "  2) not found"
		tmp = raw.replace('+', '')
		queries.append("... where date_trunc('day', identity.deceased) like (select timestamp '%s');" % tmp)
		return queries

#------------------------------------------------------------------
def tokenize(raw):
	# "#<ZIFFERN>" format: patient ID
	if re.match("^(\s|\t)*#(\d|\s|\t)+$", raw):
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		tmp = tmp.replace('#', '')
		return [{'type': 'ID', 'value': (tmp,)}]

	# "<ZIFFERN>" - patient ID or DOB
	if re.match("^(\s|\t)*\d+(\s|\t)*$", raw):
		return [{'type': 'ID-DOB', 'value': (raw.strip(),)}]

	# "<Z I  FF ERN>" - DOB or patient ID
	if re.match("^(\d|\s|\t)+$", raw):
		return [{'type': 'DOB-ID', 'value': (raw.strip(),)}]

	# "*<...>" - DOB
	elif re.match("^(\s|\t)*(\*|\$).+$", raw):
		tmp = raw.replace('*', '')
		return [{'type': 'DOB', 'value': (tmp.strip(),)}]

	# we caught all "easy" cases with only one token,
	# any remaining digits signify a date
	major_parts = []
	tmp = re.split(",|;", raw)
	for part in tmp:
		part = part.strip()
		if re.search("\d+", part):
			# we may want to strip spaces between non-alpha words such
			# that PostgreSQL does not die on them
			major_parts.append({'type': 'date', 'value': (part,)})
		else:
			minor_parts = re.split("\s*|\t*", part)
			major_parts.append({'type': 'name', 'value': minor_parts})
	return major_parts
#------------------------------------------------------------------
def first_level_queries(tree):
	return "don't know"
#------------------------------------------------------------------
def second_level_queries(tree):
	# replace umlauts with wildcards
	return "don't know"
#------------------------------------------------------------------
while 1:
	print "---------------------"
	print "hit <CTRL-C> to abort"
	patient_data = raw_input("please input patient details: ")
	token_tree = tokenize(patient_data)
	print token_tree
	queries1 = first_level_queries(token_tree)

	#queries = generate_queries(patient_data)
	#for query in queries:
	#	print "query:", query

#------------------------------------------------------------------
# config: sort order for complex names according to language
# Umlauts per language

#First level queries are going to be literal with truncation.
#Those are sent off blocking.

#Second level queries are going to replace Umlauts and
#re-shuffle name parts in a few special cases.

#Third level queries will drop part of the input and do
#substring matches on name parts.

#Second and third level are probably best put into a thread.

#Second and third level results will only be displayed when the
#first level doesn't return matches or the user hits "broaden
#search".

#However, what would be the best idea for replacing Umlauts in
#second/third level queries ? Replace them by their common
#misspelling (ü -> ue) or replace them with a wildcard "." and
#match by regex ? I tend to prefer the latter as the first will
#require me to generate a query for every possible combination
#of Umlaut replacement. This increases the number of queries by
#way of permutation. Replacing with wildcards is O(1) but will
#return a few matches that we didn't intend to see (Müller ->
#M.ller -> matches Miller as well). Perhaps this is acceptable
#since on second level queries we are into "extended query
#mode" already anyway.
#------------------------------------------------------------------
# levenshtein()
# - nr. of substitutions between two strings
# - contrib/fuzzystrmatch

# nicknames (Thai, Australian)

# soundex()
#------------------------------------------------------------------
#> It would also be good to support nicknames, as some people (Australians in particular)
#> are notorious for using them to exclusion.
#Same in Thailand. Are you saying nickname use is so prominent
#in Australia that Australian docs will want to be able to type
#the nickname to pull up the record at the time the patient
#comes in ?


#and always come up with a reasonable list of suggestions with
#myself on top. This will catch 99% of the cases. We commonly
#have the following problems:

#1) name changes
#   - marriage
#   - old last name not found in database

#2) People with German ancestry from the Ukraine
#   - difficult to get precise and _consistent_ spelling
#   - their German is often limited, especially in
#     pronounciation
#   - social security slips are often handwritten and therefore
#     unreadable
#   - social security slips are re-used among several people

#3) Vietnamese People
#   - those (and the Mozambiquans) were the Turk Gastarbeiter
#     of East Germany
#   - last and first name are often switched around, even on
#     the health insurance card

#4) Umlauts
#   - insurance companies nearly randomly spell people's names
#     with regards to Umlauts
#   - Müller will often be Mueller

#Obviously, there's different ways to construct a name: Thai
#people have many parts to choose from, it depends on the
#sitution, there's no clear concept of a first name, their
#"firstest" name is probably the nickname; Germans write "first
#last", Japanese "last first". Therefore query generation and
#order is language dependant.
#------------------------------------------------------------------
