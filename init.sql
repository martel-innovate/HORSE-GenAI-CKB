--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1.pgdg120+1)
-- Dumped by pg_dump version 16.3 (Debian 16.3-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: test_attack; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_attack (
    mitigation_priority integer,
    attack character varying,
    mitigation character varying,
    id integer NOT NULL
);


ALTER TABLE public.test_attack OWNER TO postgres;

--
-- Name: test_attack_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_attack_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_attack_id_seq OWNER TO postgres;

--
-- Name: test_attack_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_attack_id_seq OWNED BY public.test_attack.id;


--
-- Name: test_attack id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_attack ALTER COLUMN id SET DEFAULT nextval('public.test_attack_id_seq'::regclass);


--
-- Name: test_attack test_attack_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_attack
    ADD CONSTRAINT test_attack_pkey PRIMARY KEY (id);


--
-- Name: test_attack unique attacks mitigations; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_attack
    ADD CONSTRAINT "unique attacks mitigations" UNIQUE (attack, mitigation);


--
-- PostgreSQL database dump complete
--

