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
        md_json->>'md5' as ch_md5,
        md_json->>'sha256' as ch_sha256
    FROM rr3.metadata
    WHERE md_type = 'checksum';

CREATE SCHEMA oi10;

CREATE TABLE oi10.metadata (
    md_hash UUID,
    md_ingested TIMESTAMP WITH TIME ZONE,
    md_type TEXT,
    md_json JSONB,
    PRIMARY KEY (md_hash, md_type)
);

CREATE TABLE oi10.paths (
    pa_hash UUID PRIMARY KEY,
    pa_ingested TIMESTAMP WITH TIME ZONE,
    pa_type PATH_TYPE,
    pa_path TEXT,
    pa_parents UUID[]
);

CREATE VIEW oi10.checksums AS
    SELECT
        md_hash as ch_hash,
        md_json->>'md5' as ch_md5,
        md_json->>'sha256' as ch_sha256
    FROM oi10.metadata
    WHERE md_type = 'checksum';

CREATE SCHEMA al33;

CREATE TABLE al33.metadata (
    md_hash UUID,
    md_ingested TIMESTAMP WITH TIME ZONE,
    md_type TEXT,
    md_json JSONB,
    PRIMARY KEY (md_hash, md_type)
);

CREATE TABLE al33.paths (
    pa_hash UUID PRIMARY KEY,
    pa_ingested TIMESTAMP WITH TIME ZONE,
    pa_type PATH_TYPE,
    pa_path TEXT,
    pa_parents UUID[]
);

CREATE VIEW al33.checksums AS
    SELECT
        md_hash as ch_hash,
        md_json->>'md5' as ch_md5,
        md_json->>'sha256' as ch_sha256
    FROM al33.metadata
    WHERE md_type = 'checksum';

-- Read sample data
/*
\copy (with x as (select * from esgf_filter join rr3.paths on file_id = pa_hash limit 5) select y.* from metadata as y join x on md_hash = file_id) to db/metadata_sample.rr3.txt
\copy (with x as (select * from esgf_filter join rr3.paths on file_id = pa_hash limit 5) select y.* from checksums as y join x on ch_hash = file_id) to db/checksums_sample.rr3.txt
\copy (with x as (select * from esgf_filter join oi10.paths on file_id = pa_hash limit 5) select y.* from metadata as y join x on md_hash = file_id) to db/metadata_sample.oi10.txt
\copy (with x as (select * from esgf_filter join oi10.paths on file_id = pa_hash limit 5) select y.* from checksums as y join x on ch_hash = file_id) to db/checksums_sample.oi10.txt
\copy (with x as (select * from esgf_filter join al33.paths on file_id = pa_hash limit 5) select y.* from metadata as y join x on md_hash = file_id) to db/metadata_sample.al33.txt
\copy (with x as (select * from esgf_filter join al33.paths on file_id = pa_hash limit 5) select y.* from checksums as y join x on ch_hash = file_id) to db/checksums_sample.al33.txt
*/
\copy rr3.metadata  from 'db/sample_rr3_metadata.txt'
\copy rr3.paths     from 'db/sample_rr3_paths.txt'
\copy oi10.metadata  from 'db/sample_oi10_metadata.txt'
\copy oi10.paths     from 'db/sample_oi10_paths.txt'
\copy al33.metadata  from 'db/sample_al33_metadata.txt'
\copy al33.paths     from 'db/sample_al33_paths.txt'
