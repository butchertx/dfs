--
-- PostgreSQL database dump
--

-- Dumped from database version 13.3
-- Dumped by pg_dump version 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1)

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
-- Name: player_games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.player_games (
    player_name character varying(255) NOT NULL,
    pos character varying(255) NOT NULL,
    fpts_dk numeric NOT NULL,
    season integer NOT NULL,
    game_num integer NOT NULL,
    week_num integer NOT NULL,
    date timestamp without time zone NOT NULL,
    team character varying(255) NOT NULL,
    opp_team character varying(255) NOT NULL,
    home_team boolean NOT NULL
);


ALTER TABLE public.player_games OWNER TO postgres;

--
-- Name: team_games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.team_games (
    team character varying(255) NOT NULL,
    date timestamp without time zone NOT NULL,
    pts integer NOT NULL,
    td integer NOT NULL,
    over_under numeric NOT NULL,
    day character varying(255) NOT NULL,
    game_num integer NOT NULL,
    week_num integer NOT NULL,
    season integer NOT NULL,
    opp_team character varying(255) NOT NULL,
    home_team boolean NOT NULL,
    result character varying(255) NOT NULL
);


ALTER TABLE public.team_games OWNER TO postgres;

--
-- Name: player_games player_games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.player_games
    ADD CONSTRAINT player_games_pkey PRIMARY KEY (player_name, season, week_num, team);

--
-- Name: team_games team_games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_games
    ADD CONSTRAINT team_games_pkey PRIMARY KEY (team, season, week_num);


--
-- PostgreSQL database dump complete
--

