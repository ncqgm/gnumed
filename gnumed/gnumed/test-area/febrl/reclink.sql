-- sets up a database for running datasetTest.py  in postgres


--
-- PostgreSQL database dump
--

\connect - sjtan

--
-- TOC entry 1 (OID 0)
-- Name: reclink; Type: DATABASE; Schema: -; Owner: sjtan
--

CREATE DATABASE reclink WITH TEMPLATE = template0 ENCODING = 0;


\connect reclink sjtan

\connect - postgres

SET search_path = public, pg_catalog;

--
-- TOC entry 4 (OID 73374)
-- Name: plpgsql_call_handler (); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_call_handler () RETURNS language_handler
    AS '/usr/lib/pgsql/plpgsql.so', 'plpgsql_call_handler'
    LANGUAGE c;


--
-- TOC entry 3 (OID 73375)
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: public; Owner: 
--

CREATE TRUSTED PROCEDURAL LANGUAGE plpgsql HANDLER plpgsql_call_handler;


\connect - sjtan

SET search_path = public, pg_catalog;

--
-- TOC entry 2 (OID 476644)
-- Name: test; Type: TABLE; Schema: public; Owner: sjtan
--

CREATE TABLE test (
    givenname text,
    surname text,
    postcode text
);


--
-- Data for TOC entry 5 (OID 476644)
-- Name: test; Type: TABLE DATA; Schema: public; Owner: sjtan
--

COPY test (givenname, surname, postcode) FROM stdin;
ole	nielsen	2600
peter	christen	
tim	churches	2021
markus	hegland	
s	roberts	4321
kim		2001
justin	xi zhu	
ole	nielsen	2600
peter	christen	
tim	churches	2021
markus	hegland	
s	roberts	4321
kim		2001
justin	xi zhu	
\.


