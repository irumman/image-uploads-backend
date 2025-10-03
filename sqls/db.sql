--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: app_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_users (
    id bigint NOT NULL,
    name character varying(100),
    email character varying(500),
    password text,
    is_active boolean
);


ALTER TABLE public.app_users OWNER TO postgres;

--
-- Name: app_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.app_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.app_users_id_seq OWNER TO postgres;

--
-- Name: app_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.app_users_id_seq OWNED BY public.app_users.id;


--
-- Name: auth_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_sessions (
    id uuid NOT NULL,
    user_id bigint NOT NULL,
    refresh_hash bytea NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    last_seen_at timestamp with time zone,
    ip inet,
    user_agent text,
    device_name text,
    is_revoked boolean DEFAULT false NOT NULL,
    revoked_at timestamp with time zone,
    revoke_reason text,
    replaced_by uuid
);


ALTER TABLE public.auth_sessions OWNER TO postgres;

--
-- Name: image_upload; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.image_upload (
    id integer NOT NULL,
    user_id bigint,
    file_path bpchar,
    upload_timestamp timestamp with time zone,
    chapter smallint,
    line_start smallint,
    line_end smallint,
    status smallint,
    script_id smallint
);


ALTER TABLE public.image_upload OWNER TO postgres;

--
-- Name: image_upload_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.image_upload_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.image_upload_id_seq OWNER TO postgres;

--
-- Name: image_upload_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.image_upload_id_seq OWNED BY public.image_upload.id;


--
-- Name: quranic_scripts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quranic_scripts (
    id integer NOT NULL,
    script_name character varying(100)
);


ALTER TABLE public.quranic_scripts OWNER TO postgres;

--
-- Name: quranic_scripts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quranic_scripts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quranic_scripts_id_seq OWNER TO postgres;

--
-- Name: quranic_scripts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quranic_scripts_id_seq OWNED BY public.quranic_scripts.id;


--
-- Name: app_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_users ALTER COLUMN id SET DEFAULT nextval('public.app_users_id_seq'::regclass);


--
-- Name: image_upload id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.image_upload ALTER COLUMN id SET DEFAULT nextval('public.image_upload_id_seq'::regclass);


--
-- Name: quranic_scripts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quranic_scripts ALTER COLUMN id SET DEFAULT nextval('public.quranic_scripts_id_seq'::regclass);


--
-- Data for Name: app_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_users (id, name, email, password, is_active) FROM stdin;
\.


--
-- Data for Name: auth_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_sessions (id, user_id, refresh_hash, created_at, expires_at, last_seen_at, ip, user_agent, device_name, is_revoked, revoked_at, revoke_reason, replaced_by) FROM stdin;
\.


--
-- Data for Name: image_upload; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.image_upload (id, user_id, file_path, upload_timestamp, chapter, line_start, line_end, status, script_id) FROM stdin;
\.


--
-- Data for Name: quranic_scripts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quranic_scripts (id, script_name) FROM stdin;
1	uthmani
\.


--
-- Name: app_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.app_users_id_seq', 1, true);


--
-- Name: image_upload_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.image_upload_id_seq', 1, true);


--
-- Name: quranic_scripts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quranic_scripts_id_seq', 1, true);


--
-- Name: app_users app_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_users
    ADD CONSTRAINT app_users_pkey PRIMARY KEY (id);


--
-- Name: auth_sessions auth_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_pkey PRIMARY KEY (id);


--
-- Name: image_upload image_upload_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.image_upload
    ADD CONSTRAINT image_upload_pkey PRIMARY KEY (id);


--
-- Name: quranic_scripts quranic_scripts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quranic_scripts
    ADD CONSTRAINT quranic_scripts_pkey PRIMARY KEY (id);


--
-- Name: auth_sessions_expires_at_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_sessions_expires_at_idx ON public.auth_sessions USING btree (expires_at);


--
-- Name: auth_sessions_is_revoked_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_sessions_is_revoked_idx ON public.auth_sessions USING btree (is_revoked);


--
-- Name: auth_sessions_user_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_sessions_user_id_idx ON public.auth_sessions USING btree (user_id);


--
-- Name: auth_sessions auth_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_sessions
    ADD CONSTRAINT auth_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_users(id) ON DELETE CASCADE;


--
-- Name: image_upload fk_script; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.image_upload
    ADD CONSTRAINT fk_script FOREIGN KEY (script_id) REFERENCES public.quranic_scripts(id);


--
-- PostgreSQL database dump complete
--

