CREATE OR REPLACE FUNCTION init_schema(name text) 
   RETURNS void AS
$BODY$
    BEGIN

    EXECUTE 'CREATE SCHEMA ' || name ; 
    
    --
    -- Name: active_fire; Type: TABLE; Schema: public; Owner: postgres
    --
    EXECUTE 'CREATE TABLE ' || name || '.active_fire (' ||
        'fid bigint NOT NULL, ' ||
        'latitude real, ' || 
        'longitude real, ' || 
        'collection_date timestamp without time zone, ' || 
        'geom geometry(Point,4326), ' || 
        'event_fid integer, ' || 
        'pixel_size integer NOT NULL, ' ||
        'band_i_m character(1) NOT NULL)';
    
    
    EXECUTE 'ALTER TABLE ' || name || '.active_fire OWNER TO postgres';
    
    --
    -- Name: active_fire_fid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE SEQUENCE ' || name || '.active_fire_fid_seq ' ||
        'START WITH 1 ' ||
        'INCREMENT BY 1 ' || 
        'NO MINVALUE ' || 
        'NO MAXVALUE ' ||
        'CACHE 1';
    
    
    EXECUTE 'ALTER TABLE ' || name || '.active_fire_fid_seq OWNER TO postgres';
    
    --
    -- Name: active_fire_fid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER SEQUENCE ' || name || '.active_fire_fid_seq OWNED BY '||
        name || '.active_fire.fid';
    
    
    --
    -- Name: fire_collections; Type: TABLE; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE TABLE ' || name || '.fire_collections (' ||
        'fid bigint NOT NULL, ' ||
        'active boolean, ' ||
        'initial_fid bigint, ' ||
        'last_update timestamp without time zone, ' || 
        'initial_date timestamp without time zone)';
    
    
    EXECUTE 'ALTER TABLE ' || name || '.fire_collections OWNER TO postgres';
    
    --
    -- Name: fire_collections_fid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE SEQUENCE ' || name || '.fire_collections_fid_seq ' ||
        'START WITH 1 ' ||
        'INCREMENT BY 1 ' ||
        'NO MINVALUE ' ||
        'NO MAXVALUE ' ||
        'CACHE 1';
    
    
    EXECUTE 'ALTER TABLE ' || name || '.fire_collections_fid_seq OWNER TO postgres';
    
    --
    -- Name: fire_collections_fid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER SEQUENCE ' || name || '.fire_collections_fid_seq OWNED BY ' ||
         name || '.fire_collections.fid';
    
    
    --
    -- Name: fire_events; Type: TABLE; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE TABLE ' || name || '.fire_events (' ||
        'fid bigint NOT NULL, ' || 
        'latitude real, ' || 
        'longitude real, ' || 
        'geom geometry(MultiPoint,102008), ' || 
        'source character(10), ' || 
        'collection_id bigint, ' || 
        'collection_date timestamp without time zone, ' ||
        'pixel_size integer NOT NULL, ' ||
        'band_i_m character(1) NOT NULL)';
    
    
    EXECUTE 'ALTER TABLE ' || name || '.fire_events OWNER TO postgres';
    
    --
    -- Name: fire_events_fid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE SEQUENCE ' || name || '.fire_events_fid_seq ' || 
        'START WITH 1 ' ||
        'INCREMENT BY 1 ' || 
        'NO MINVALUE ' ||
        'NO MAXVALUE ' ||
        'CACHE 1';
    
    
    EXECUTE 'ALTER TABLE ' || name || '.fire_events_fid_seq OWNER TO postgres';
    
    --
    -- Name: fire_events_fid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER SEQUENCE ' || name || '.fire_events_fid_seq OWNED BY ' ||
         name || '.fire_events.fid';
    
    
    --
    -- Name: threshold_burned; Type: TABLE; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE TABLE ' || name || '.threshold_burned (' || 
        'fid bigint NOT NULL, ' ||
        'latitude real, ' ||
        'longitude real, ' ||
        'collection_date timestamp without time zone, ' || 
        'geom geometry(Point,4326), ' ||
        'confirmed_burn boolean DEFAULT false, ' ||
        'pixel_size integer NOT NULL, ' ||
        'band_i_m character(1) NOT NULL)';
    
    
    EXECUTE 'ALTER TABLE ' || name || '.threshold_burned OWNER TO postgres';
    
    --
    -- Name: threshold_burned_fid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE SEQUENCE ' || name || '.threshold_burned_fid_seq ' || 
        'START WITH 1 ' ||
        'INCREMENT BY 1 ' ||
        'NO MINVALUE ' || 
        'NO MAXVALUE ' ||
        'CACHE 1';
    
    
    EXECUTE 'ALTER TABLE ' || name || '.threshold_burned_fid_seq OWNER TO postgres';
    
    --
    -- Name: threshold_burned_fid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER SEQUENCE ' || name || '.threshold_burned_fid_seq OWNED BY ' ||
        name || '.threshold_burned.fid';
    
    
    --
    -- Name: fid; Type: DEFAULT; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER TABLE ONLY ' || name || 
      '.active_fire ALTER COLUMN fid SET DEFAULT ' ||
      'nextval(' || quote_literal(name || '.active_fire_fid_seq') || '::regclass)';
    
    
    --
    -- Name: fid; Type: DEFAULT; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER TABLE ONLY ' || name || 
      '.fire_collections ALTER COLUMN fid SET DEFAULT ' ||
      'nextval(' || quote_literal(name || '.fire_collections_fid_seq') || '::regclass)';
    
    
    --
    -- Name: fid; Type: DEFAULT; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER TABLE ONLY ' || name ||
       '.fire_events ALTER COLUMN fid SET DEFAULT ' ||
       'nextval(' || quote_literal(name || '.fire_events_fid_seq') || '::regclass)';
    
    
    --
    -- Name: fid; Type: DEFAULT; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER TABLE ONLY ' || name || 
      '.threshold_burned ALTER COLUMN fid SET DEFAULT ' ||
      'nextval(' || quote_literal(name || '.threshold_burned_fid_seq') || '::regclass)';
    
    
    --
    -- Name: active_fire_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER TABLE ONLY ' || name || '.active_fire ' || 
        'ADD CONSTRAINT ' || name || '_active_fire_pkey PRIMARY KEY (fid)';
    
    
    --
    -- Name: fire_collections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER TABLE ONLY ' || name || '.fire_collections ' || 
        'ADD CONSTRAINT ' || name || '_fire_collections_pkey PRIMARY KEY (fid)';
    
    
    --
    -- Name: fire_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER TABLE ONLY ' || name || '.fire_events ' || 
        'ADD CONSTRAINT ' || name || '_fire_events_pkey PRIMARY KEY (fid)';
    
    
    --
    -- Name: threshold_burned_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
    --
    
    EXECUTE 'ALTER TABLE ONLY ' || name || '.threshold_burned ' || 
        'ADD CONSTRAINT ' || name || '_threshold_burned_pkey PRIMARY KEY (fid)';
    
    
    --
    -- Name: idx_active_fire_geom; Type: INDEX; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE INDEX idx_' || name || '_active_fire_geom ON ' || 
       name || '.active_fire USING gist (geom)';
    
    
    --
    -- Name: idx_fire_events_geom; Type: INDEX; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE INDEX idx_' || name || '_fire_events_geom ON ' || 
       name || '.fire_events USING gist (geom)';
    
    
    --
    -- Name: idx_threshold_burned_geom; Type: INDEX; Schema: public; Owner: postgres
    --
    
    EXECUTE 'CREATE INDEX idx_' || name || '_threshold_burned_geom ON ' || 
       name || '.threshold_burned USING gist (geom)';
       
    END
$BODY$ 
  LANGUAGE plpgsql VOLATILE
  COST 100 ; 
ALTER FUNCTION init_schema(text)
  OWNER to postgres ;
