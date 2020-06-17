/*
 * Database structure for testing
 *
 * In production these tables come from a remote database
 */

CREATE TYPE path_type AS ENUM ('file', 'directory', 'link');

CREATE SCHEMA dataset_cmip5;

CREATE TABLE dataset_cmip5.metadata (
    md_hash UUID,
    md_ingested TIMESTAMP WITH TIME ZONE,
    md_type TEXT,
    md_json JSONB,
    PRIMARY KEY (md_hash, md_type)
);

CREATE TABLE dataset_cmip5.paths (
    pa_hash UUID PRIMARY KEY,
    pa_ingested TIMESTAMP WITH TIME ZONE,
    pa_type PATH_TYPE,
    pa_path TEXT,
    pa_parents UUID[]
);

CREATE VIEW dataset_cmip5.checksums AS
    SELECT
        md_hash as ch_hash,
        md_json->>'md5' as ch_md5,
        md_json->>'sha256' as ch_sha256
    FROM dataset_cmip5.metadata
    WHERE md_type = 'checksum';

CREATE SCHEMA dataset_cmip6;

CREATE TABLE dataset_cmip6.metadata (
    md_hash UUID,
    md_ingested TIMESTAMP WITH TIME ZONE,
    md_type TEXT,
    md_json JSONB,
    PRIMARY KEY (md_hash, md_type)
);

CREATE TABLE dataset_cmip6.paths (
    pa_hash UUID PRIMARY KEY,
    pa_ingested TIMESTAMP WITH TIME ZONE,
    pa_type PATH_TYPE,
    pa_path TEXT,
    pa_parents UUID[]
);

CREATE VIEW dataset_cmip6.checksums AS
    SELECT
        md_hash as ch_hash,
        md_json->>'md5' as ch_md5,
        md_json->>'sha256' as ch_sha256
    FROM dataset_cmip6.metadata
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
\copy dataset_cmip5.metadata  from 'db/sample_rr3_metadata.txt'
\copy dataset_cmip5.paths     from 'db/sample_rr3_paths.txt'
\copy dataset_cmip6.metadata  from 'db/sample_oi10_metadata.txt'
\copy dataset_cmip6.paths     from 'db/sample_oi10_paths.txt'
\copy dataset_cmip5.metadata  from 'db/sample_al33_metadata.txt'
\copy dataset_cmip5.paths     from 'db/sample_al33_paths.txt'
