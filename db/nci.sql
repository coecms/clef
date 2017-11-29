/*
 * Database structure for testing
 *
 * In production these tables come from a remote database
 */

CREATE TYPE path_type AS ENUM ('file', 'directory', 'link');

CREATE SCHEMA rr3;

CREATE TABLE rr3.metadata (
    md_hash UUID,
    md_ingested TIMESTAMP WITH TIME ZONE,
    md_type TEXT,
    md_json JSONB,
    PRIMARY KEY (md_hash, md_type)
);

CREATE TABLE rr3.paths (
    pa_hash UUID PRIMARY KEY,
    pa_ingested TIMESTAMP WITH TIME ZONE,
    pa_type PATH_TYPE,
    pa_path TEXT,
    pa_parents UUID[]
);

CREATE VIEW rr3.checksums AS
    SELECT
        md_hash as ch_hash,
        md_json->'attributes'->>'md5' as ch_md5,
        md_json->'attributes'->>'sha256' as ch_sha256
    FROM rr3.metadata
    WHERE md_type = 'checksum';

CREATE SCHEMA ua6;

CREATE TABLE ua6.metadata (
    md_hash UUID,
    md_ingested TIMESTAMP WITH TIME ZONE,
    md_type TEXT,
    md_json JSONB,
    PRIMARY KEY (md_hash, md_type)
);

CREATE TABLE ua6.paths (
    pa_hash UUID PRIMARY KEY,
    pa_ingested TIMESTAMP WITH TIME ZONE,
    pa_type PATH_TYPE,
    pa_path TEXT,
    pa_parents UUID[]
);

CREATE VIEW ua6.checksums AS
    SELECT
        md_hash as ch_hash,
        md_json->'attributes'->>'md5' as ch_md5,
        md_json->'attributes'->>'sha256' as ch_sha256
    FROM ua6.metadata
    WHERE md_type = 'checksum';

-- Read sample data
/*
\copy (with x as (select * from esgf_filter limit 5) select y.* from metadata as y join x on md_hash = file_id) to db/metadata_sample.txt 
\copy (with x as (select * from esgf_filter limit 5) select y.* from checksums as y join x on ch_hash = file_id) to db/checksums_sample.txt 
*/
\copy ua6.metadata  from 'db/metadata_sample.txt'
\copy ua6.paths     from 'db/paths_sample.txt'

