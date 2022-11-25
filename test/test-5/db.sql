--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1 (Ubuntu 15.1-1.pgdg20.04+1)
-- Dumped by pg_dump version 15.1 (Ubuntu 15.1-1.pgdg20.04+1)

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
-- Name: auth; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth (
    username text NOT NULL,
    password text NOT NULL,
    salt text NOT NULL,
    publickeyn text NOT NULL,
    publickeye integer NOT NULL
);


ALTER TABLE public.auth OWNER TO postgres;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groups (
    group_name text NOT NULL,
    participant text NOT NULL,
    is_admin boolean,
    id integer NOT NULL
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- Name: image; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.image (
    sender text NOT NULL,
    reciever text NOT NULL,
    img bytea NOT NULL,
    "time" timestamp without time zone,
    displayed boolean,
    imagenames text NOT NULL
);


ALTER TABLE public.image OWNER TO postgres;

--
-- Name: message; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.message (
    sender text NOT NULL,
    reciever text NOT NULL,
    message text,
    "time" timestamp without time zone
);


ALTER TABLE public.message OWNER TO postgres;

--
-- Name: privatekeytable; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.privatekeytable (
    username text NOT NULL,
    privatekeyn text NOT NULL,
    privatekeye text NOT NULL,
    privatekeyd text NOT NULL,
    privatekeyp text NOT NULL,
    privatekeyq text NOT NULL
);


ALTER TABLE public.privatekeytable OWNER TO postgres;

--
-- Name: server; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.server (
    serverid integer NOT NULL,
    clientid text NOT NULL
);


ALTER TABLE public.server OWNER TO postgres;

--
-- Name: auth auth_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth
    ADD CONSTRAINT auth_pkey PRIMARY KEY (username);


--
-- Name: TABLE auth; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT ON TABLE public.auth TO client;


--
-- Name: TABLE groups; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.groups TO client;


--
-- Name: TABLE image; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.image TO client;


--
-- Name: TABLE message; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT ON TABLE public.message TO client;


--
-- Name: TABLE privatekeytable; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT ON TABLE public.privatekeytable TO client;


--
-- Name: TABLE server; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.server TO server;


--
-- PostgreSQL database dump complete
--

