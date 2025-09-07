--
-- PostgreSQL database dump
--

-- Dumped from database version 13.0 (Debian 13.0-1.pgdg100+1)
-- Dumped by pg_dump version 13.0 (Debian 13.0-1.pgdg100+1)

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
-- Name: book; Type: TABLE; Schema: public; Owner: picket
--

CREATE TABLE public.book (
    id integer NOT NULL,
    title text NOT NULL,
    author text
);


ALTER TABLE public.book OWNER TO picket;

--
-- Name: book_id_seq; Type: SEQUENCE; Schema: public; Owner: picket
--

CREATE SEQUENCE public.book_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.book_id_seq OWNER TO picket;

--
-- Name: book_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: picket
--

ALTER SEQUENCE public.book_id_seq OWNED BY public.book.id;


--
-- Name: book id; Type: DEFAULT; Schema: public; Owner: picket
--

ALTER TABLE ONLY public.book ALTER COLUMN id SET DEFAULT nextval('public.book_id_seq'::regclass);


--
-- Data for Name: book; Type: TABLE DATA; Schema: public; Owner: picket
--

INSERT INTO public.book (id, title, author) VALUES (1, 'Detective Douche', 'Picket Holmes');
INSERT INTO public.book (id, title, author) VALUES (2, 'Making Murica Great Again', 'Tonald Drump');


--
-- Name: book_id_seq; Type: SEQUENCE SET; Schema: public; Owner: picket
--

SELECT pg_catalog.setval('public.book_id_seq', 2, true);


--
-- Name: book book_pk; Type: CONSTRAINT; Schema: public; Owner: picket
--

ALTER TABLE ONLY public.book
    ADD CONSTRAINT book_pk PRIMARY KEY (id);


--
-- Name: book_id_uindex; Type: INDEX; Schema: public; Owner: picket
--

CREATE UNIQUE INDEX book_id_uindex ON public.book USING btree (id);


--
-- PostgreSQL database dump complete
--

