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
-- Name: competitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competitions (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    starts_at timestamp without time zone NOT NULL,
    week integer NOT NULL,
    home_team_id integer NOT NULL,
    home_team_name character varying(255) NOT NULL,
    home_team_abbreviation character varying(255) NOT NULL,
    home_team_city character varying(255) NOT NULL,
    away_team_id integer NOT NULL,
    away_team_name character varying(255) NOT NULL,
    away_team_abbreviation character varying(255) NOT NULL,
    away_team_city character varying(255) NOT NULL
);


ALTER TABLE public.competitions OWNER TO postgres;

--
-- Name: competitions_dict; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competitions_dict (
);


ALTER TABLE public.competitions_dict OWNER TO postgres;

--
-- Name: contest_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contest_entries (
    entry_id bigint NOT NULL,
    contest_id integer NOT NULL,
    week integer NOT NULL,
    draft_group_id integer NOT NULL,
    entry_name character varying(255) NOT NULL,
    rank integer NOT NULL,
    points_total numeric NOT NULL,
    gross_cash_winnings numeric NOT NULL
);


ALTER TABLE public.contest_entries OWNER TO postgres;

--
-- Name: contest_entry_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contest_entry_stats (
    entry_id bigint NOT NULL,
    contest_id integer NOT NULL,
    entry_name character varying(255) NOT NULL,
    stack character varying(255) NOT NULL,
    usage_by_position character varying(255) NOT NULL,
    usage_by_roster_slot character varying(255) NOT NULL,
    usage_total numeric NOT NULL,
    projection_total numeric NOT NULL,
    projection_by_position character varying(255) NOT NULL,
    projection_by_roster_slot character varying(255) NOT NULL,
    salary_total numeric NOT NULL,
    salary_by_position character varying(255) NOT NULL,
    salary_by_roster_slot character varying(255) NOT NULL
);


ALTER TABLE public.contest_entry_stats OWNER TO postgres;

--
-- Name: contest_rosters; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contest_rosters (
    week integer NOT NULL,
    draft_group_id integer NOT NULL,
    contest_id integer NOT NULL,
    entry_id bigint NOT NULL,
    roster_slot_id integer NOT NULL,
    player_id integer NOT NULL,
    salary numeric,
    "position" character varying(255)
);


ALTER TABLE public.contest_rosters OWNER TO postgres;

--
-- Name: contests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contests (
    contest_id integer NOT NULL,
    double_up boolean NOT NULL,
    draft_group_id integer NOT NULL,
    fifty_fifty boolean NOT NULL,
    guaranteed boolean NOT NULL,
    head_to_head boolean NOT NULL,
    name character varying(255) NOT NULL,
    payout numeric NOT NULL,
    starred boolean NOT NULL,
    starts_at timestamp without time zone NOT NULL,
    week integer NOT NULL,
    entries_max integer NOT NULL,
    entries_fee numeric NOT NULL,
    contest_type integer NOT NULL,
    games_count integer NOT NULL,
    multientry integer NOT NULL,
    max_entry_fee numeric NOT NULL,
    rake numeric
);


ALTER TABLE public.contests OWNER TO postgres;

--
-- Name: draftables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.draftables (
    id integer NOT NULL,
    team_id integer NOT NULL,
    team_abbreviation character varying(255) NOT NULL,
    player_id integer NOT NULL,
    draft_group_id integer NOT NULL,
    competition_id integer,
    name character varying(255) NOT NULL,
    "position" character varying(255) NOT NULL,
    roster_slot_id integer NOT NULL,
    salary numeric,
    swappable boolean NOT NULL,
    disabled boolean NOT NULL
);


ALTER TABLE public.draftables OWNER TO postgres;

--
-- Name: payouts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payouts (
    contest_id integer NOT NULL,
    min_position integer NOT NULL,
    max_position integer NOT NULL,
    payout_cash numeric,
    payout_tickets character varying(255)
);


ALTER TABLE public.payouts OWNER TO postgres;

--
-- Name: player_game_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.player_game_stats (
    week integer NOT NULL,
    player_id integer NOT NULL,
    fpts_ppr numeric
);


ALTER TABLE public.player_game_stats OWNER TO postgres;

--
-- Name: players_dict; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.players_dict (
    player_name character varying(255) NOT NULL,
    "position" character varying(255) NOT NULL,
    team character varying(255) NOT NULL,
    draftkings_name character varying(255) NOT NULL,
    player_id integer NOT NULL
);


ALTER TABLE public.players_dict OWNER TO postgres;

--
-- Name: projections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projections (
    week integer NOT NULL,
    player_id integer NOT NULL,
    projection_ppr numeric,
    sd_pts numeric,
    dropoff numeric,
    floor numeric,
    ceiling numeric,
    points_vor numeric,
    floor_vor numeric,
    ceiling_vor numeric,
    uncertainty numeric
);


ALTER TABLE public.projections OWNER TO postgres;

--
-- Name: competitions competitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competitions
    ADD CONSTRAINT competitions_pkey PRIMARY KEY (id);


--
-- Name: contest_entries contest_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contest_entries
    ADD CONSTRAINT contest_entries_pkey PRIMARY KEY (entry_id);


--
-- Name: contest_entry_stats contest_entry_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contest_entry_stats
    ADD CONSTRAINT contest_entry_stats_pkey PRIMARY KEY (entry_id);


--
-- Name: contest_rosters contest_rosters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contest_rosters
    ADD CONSTRAINT contest_rosters_pkey PRIMARY KEY (entry_id, player_id);


--
-- Name: contests contests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contests
    ADD CONSTRAINT contests_pkey PRIMARY KEY (contest_id);


--
-- Name: draftables draftables_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.draftables
    ADD CONSTRAINT draftables_pkey PRIMARY KEY (id);


--
-- Name: payouts payouts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payouts
    ADD CONSTRAINT payouts_pkey PRIMARY KEY (contest_id, min_position);


--
-- Name: player_game_stats player_game_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.player_game_stats
    ADD CONSTRAINT player_game_stats_pkey PRIMARY KEY (week, player_id);


--
-- Name: players_dict players_dict_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.players_dict
    ADD CONSTRAINT players_dict_pkey PRIMARY KEY (player_name, "position", team);


--
-- Name: projections projections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projections
    ADD CONSTRAINT projections_pkey PRIMARY KEY (week, player_id);


--
-- Name: contest_entries_contest_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_entries_contest_id_idx ON public.contest_entries USING btree (contest_id);


--
-- Name: contest_entries_dgid_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_entries_dgid_idx ON public.contest_entries USING btree (draft_group_id);


--
-- Name: contest_entries_entry_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_entries_entry_id_idx ON public.contest_entries USING btree (entry_id);


--
-- Name: contest_entries_entry_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_entries_entry_name_idx ON public.contest_entries USING btree (entry_name);


--
-- Name: contest_entries_week_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_entries_week_idx ON public.contest_entries USING btree (week);


--
-- Name: contest_entry_stats_contest_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_entry_stats_contest_id_idx ON public.contest_entry_stats USING btree (contest_id);


--
-- Name: contest_entry_stats_entry_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_entry_stats_entry_id_idx ON public.contest_entry_stats USING btree (entry_id);


--
-- Name: contest_entry_stats_entry_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_entry_stats_entry_name_idx ON public.contest_entry_stats USING btree (entry_name);


--
-- Name: contest_rosters_cid_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_rosters_cid_idx ON public.contest_rosters USING btree (contest_id);


--
-- Name: contest_rosters_dgid_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_rosters_dgid_idx ON public.contest_rosters USING btree (draft_group_id);


--
-- Name: contest_rosters_entry_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_rosters_entry_id_idx ON public.contest_rosters USING btree (entry_id);


--
-- Name: contest_rosters_player_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_rosters_player_id_idx ON public.contest_rosters USING btree (player_id);


--
-- Name: contest_rosters_roster_slot_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_rosters_roster_slot_id_idx ON public.contest_rosters USING btree (roster_slot_id);


--
-- Name: contest_rosters_week_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX contest_rosters_week_idx ON public.contest_rosters USING btree (week);


--
-- PostgreSQL database dump complete
--

