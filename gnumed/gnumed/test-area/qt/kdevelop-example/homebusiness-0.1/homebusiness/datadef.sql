--
-- PostgreSQL database dump
--

\connect - postgres

SET search_path = public, pg_catalog;

--
-- TOC entry 23 (OID 73374)
-- Name: plpgsql_call_handler (); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_call_handler () RETURNS language_handler
    AS '/usr/lib/pgsql/plpgsql.so', 'plpgsql_call_handler'
    LANGUAGE c;


--
-- TOC entry 22 (OID 73375)
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: public; Owner: 
--

CREATE TRUSTED PROCEDURAL LANGUAGE plpgsql HANDLER plpgsql_call_handler;


\connect - sjtan

SET search_path = public, pg_catalog;

--
-- TOC entry 8 (OID 132256)
-- Name: product; Type: TABLE; Schema: public; Owner: sjtan
--

CREATE TABLE product (
    name character varying(200),
    code character varying(50) NOT NULL,
    description text,
    product_id integer NOT NULL
);


--
-- TOC entry 9 (OID 132261)
-- Name: money; Type: TABLE; Schema: public; Owner: sjtan
--

CREATE TABLE money (
    "type" character varying(20),
    money_id integer NOT NULL,
    dollars integer,
    cents integer
);


--
-- TOC entry 2 (OID 132263)
-- Name: cust_id_seq; Type: SEQUENCE; Schema: public; Owner: sjtan
--

CREATE SEQUENCE cust_id_seq
    START 1
    INCREMENT 1
    MAXVALUE 9223372036854775807
    MINVALUE 1
    CACHE 1;


--
-- TOC entry 10 (OID 132265)
-- Name: customer; Type: TABLE; Schema: public; Owner: sjtan
--

CREATE TABLE customer (
    cust_id integer NOT NULL,
    firstname character varying(200),
    lastname character varying(200),
    address character varying(200),
    phone character varying(50)
);


--
-- TOC entry 3 (OID 132267)
-- Name: au_money_seq; Type: SEQUENCE; Schema: public; Owner: sjtan
--

CREATE SEQUENCE au_money_seq
    START 1
    INCREMENT 1
    MAXVALUE 9223372036854775807
    MINVALUE 1
    CACHE 1;


--
-- TOC entry 4 (OID 132269)
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: sjtan
--

CREATE SEQUENCE order_id_seq
    START 1
    INCREMENT 1
    MAXVALUE 9223372036854775807
    MINVALUE 1
    CACHE 1;


--
-- TOC entry 11 (OID 132271)
-- Name: orders; Type: TABLE; Schema: public; Owner: sjtan
--

CREATE TABLE orders (
    order_id integer NOT NULL,
    cust_id integer,
    order_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone,
    external_id character varying(50),
    paid_date timestamp without time zone
);


--
-- TOC entry 5 (OID 132273)
-- Name: prod_offer_id_seq; Type: SEQUENCE; Schema: public; Owner: sjtan
--

CREATE SEQUENCE prod_offer_id_seq
    START 1
    INCREMENT 1
    MAXVALUE 9223372036854775807
    MINVALUE 1
    CACHE 1;


--
-- TOC entry 12 (OID 132275)
-- Name: product_offer; Type: TABLE; Schema: public; Owner: sjtan
--

CREATE TABLE product_offer (
    prod_offer_id integer NOT NULL,
    product_code character varying(50),
    money_id integer,
    start_offer timestamp without time zone,
    end_offer timestamp without time zone,
    product_id integer
);


--
-- TOC entry 13 (OID 132277)
-- Name: order_item; Type: TABLE; Schema: public; Owner: sjtan
--

CREATE TABLE order_item (
    order_id integer NOT NULL,
    prod_offer_id integer NOT NULL,
    ordered_time timestamp without time zone DEFAULT now(),
    qty integer NOT NULL,
    CONSTRAINT "$1" CHECK ((qty > 0))
);


--
-- TOC entry 6 (OID 132281)
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: sjtan
--

CREATE SEQUENCE product_id_seq
    START 1
    INCREMENT 1
    MAXVALUE 9223372036854775807
    MINVALUE 1
    CACHE 1;


--
-- TOC entry 14 (OID 132283)
-- Name: discount; Type: TABLE; Schema: public; Owner: sjtan
--

CREATE TABLE discount (
    discount_id integer NOT NULL,
    amount integer,
    percent numeric(5,2),
    order_id integer,
    prod_offer_id integer,
    is_order boolean,
    is_order_item boolean,
    applied timestamp without time zone,
    discount_type character varying(30)
);


--
-- TOC entry 7 (OID 132285)
-- Name: discount_id_seq; Type: SEQUENCE; Schema: public; Owner: sjtan
--

CREATE SEQUENCE discount_id_seq
    START 1
    INCREMENT 1
    MAXVALUE 9223372036854775807
    MINVALUE 1
    CACHE 1;


--
-- TOC entry 16 (OID 132521)
-- Name: money_pkey; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY money
    ADD CONSTRAINT money_pkey PRIMARY KEY (money_id);


--
-- TOC entry 17 (OID 132523)
-- Name: customer_pkey; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY customer
    ADD CONSTRAINT customer_pkey PRIMARY KEY (cust_id);


--
-- TOC entry 18 (OID 132525)
-- Name: orders_pkey; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- TOC entry 24 (OID 132527)
-- Name: $1; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY orders
    ADD CONSTRAINT "$1" FOREIGN KEY (cust_id) REFERENCES customer(cust_id) ON UPDATE NO ACTION ON DELETE NO ACTION;


--
-- TOC entry 19 (OID 132531)
-- Name: product_offer_pkey; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY product_offer
    ADD CONSTRAINT product_offer_pkey PRIMARY KEY (prod_offer_id);


--
-- TOC entry 25 (OID 132533)
-- Name: $2; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY product_offer
    ADD CONSTRAINT "$2" FOREIGN KEY (money_id) REFERENCES money(money_id) ON UPDATE NO ACTION ON DELETE NO ACTION;


--
-- TOC entry 20 (OID 132537)
-- Name: order_item_pkey; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY order_item
    ADD CONSTRAINT order_item_pkey PRIMARY KEY (order_id, prod_offer_id);


--
-- TOC entry 27 (OID 132539)
-- Name: $2; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY order_item
    ADD CONSTRAINT "$2" FOREIGN KEY (order_id) REFERENCES orders(order_id) ON UPDATE NO ACTION ON DELETE NO ACTION;


--
-- TOC entry 28 (OID 132543)
-- Name: $3; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY order_item
    ADD CONSTRAINT "$3" FOREIGN KEY (prod_offer_id) REFERENCES product_offer(prod_offer_id) ON UPDATE NO ACTION ON DELETE NO ACTION;


--
-- TOC entry 15 (OID 132547)
-- Name: product_pkey; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY product
    ADD CONSTRAINT product_pkey PRIMARY KEY (product_id);


--
-- TOC entry 26 (OID 132549)
-- Name: $1; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY product_offer
    ADD CONSTRAINT "$1" FOREIGN KEY (product_id) REFERENCES product(product_id) ON UPDATE NO ACTION ON DELETE NO ACTION;


--
-- TOC entry 21 (OID 132553)
-- Name: discount_pkey; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY discount
    ADD CONSTRAINT discount_pkey PRIMARY KEY (discount_id);


--
-- TOC entry 29 (OID 132555)
-- Name: $1; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY discount
    ADD CONSTRAINT "$1" FOREIGN KEY (amount) REFERENCES money(money_id) ON UPDATE NO ACTION ON DELETE NO ACTION;


--
-- TOC entry 30 (OID 132559)
-- Name: $2; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY discount
    ADD CONSTRAINT "$2" FOREIGN KEY (order_id) REFERENCES orders(order_id) ON UPDATE NO ACTION ON DELETE NO ACTION;


--
-- TOC entry 31 (OID 132563)
-- Name: fk_order_item; Type: CONSTRAINT; Schema: public; Owner: sjtan
--

ALTER TABLE ONLY discount
    ADD CONSTRAINT fk_order_item FOREIGN KEY (order_id, prod_offer_id) REFERENCES order_item(order_id, prod_offer_id) ON UPDATE NO ACTION ON DELETE NO ACTION;


