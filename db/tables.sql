CREATE OR REPLACE VIEW metadata AS
    SELECT
        md_hash,
        md_ingested,
        md_type,
        md_json
    FROM rr3.metadata
    UNION ALL
    SELECT
        md_hash,
        md_ingested,
        md_type,
        md_json
    FROM al33.metadata
    UNION ALL
    SELECT
        md_hash,
        md_ingested,
        md_type,
        md_json
    FROM oi10.metadata;


CREATE OR REPLACE VIEW paths AS
    SELECT
        pa_hash,
        pa_type,
        pa_path,
        pa_parents
    FROM rr3.paths
    UNION ALL
    SELECT
        pa_hash,
        pa_type,
        pa_path,
        pa_parents
    FROM al33.paths
    UNION ALL
    SELECT
        pa_hash,
        pa_type,
        pa_path,
        pa_parents
    FROM oi10.paths;

/*
CREATE OR REPLACE VIEW checksums AS
    SELECT
        ch_hash,
        ch_md5,
        ch_sha256
    FROM rr3.checksums
    UNION ALL
    SELECT
        ch_hash,
        ch_md5,
        ch_sha256
    FROM al33.checksums
    UNION ALL
    SELECT
        ch_hash,
        ch_md5,
        ch_sha256
    FROM oi10.checksums;
*/


/* Filter to unify the schemas and only return CMIP data files
 */
CREATE OR REPLACE VIEW esgf_filter AS
    SELECT
        pa_hash AS file_id,
        5 AS cmip_era,
        pa_path AS path
    FROM rr3.paths
    WHERE
        pa_type IN ('file', 'link')
    AND pa_parents[4] = md5('/g/data1/rr3/publications')::uuid
    AND split_part(pa_path, '/', 6) != 'CMIP5RT'
    AND split_part(pa_path, '/', 15) != 'files'
    AND split_part(pa_path, '/', 17) != 'files'
    AND pa_path LIKE '%.nc'
    UNION ALL
    SELECT
        pa_hash AS file_id,
        6 AS cmip_era,
        pa_path AS path
    FROM oi10.paths
    WHERE
        pa_type IN ('file', 'link')
    AND pa_parents[4] = md5('/g/data1b/oi10/replicas')::uuid
    AND pa_path LIKE '%.nc'
    UNION ALL
    SELECT
        pa_hash AS file_id,
        5 AS cmip_era,
        pa_path AS path
    FROM al33.paths
    WHERE
        pa_type IN ('file', 'link')
    AND pa_parents[4] = md5('/g/data1b/al33/replicas')::uuid
    -- AND split_part(pa_path, '/', 7) = 'combined'
    AND pa_path LIKE '%.nc';


/* Materialize the filter
 */
CREATE MATERIALIZED VIEW IF NOT EXISTS esgf_paths AS
    SELECT
        file_id,
        cmip_era,
        path
    FROM esgf_filter;
CREATE UNIQUE INDEX IF NOT EXISTS esgf_path_file_id_idx ON esgf_paths(file_id);
CREATE INDEX IF NOT EXISTS esgf_paths_basename_idx ON esgf_paths (regexp_replace(path, '^.*/', ''));

CREATE MATERIALIZED VIEW IF NOT EXISTS checksums AS
    SELECT
        md_hash as ch_hash,
        md_json->>'md5' as ch_md5,
        md_json->>'sha256' as ch_sha256
    FROM metadata
    JOIN esgf_paths ON md_hash = file_id
    WHERE md_type = 'checksum';
CREATE UNIQUE INDEX IF NOT EXISTS checksums_hash_idx ON checksums(ch_hash);
CREATE INDEX IF NOT EXISTS checksums_md5_idx ON checksums(ch_md5);
CREATE INDEX IF NOT EXISTS checksums_sha256_idx ON checksums(ch_sha256);

/* modified this so it works with both cmip5 and cmip6 using attributes_map.json */
CREATE OR REPLACE VIEW c5_dataset_metadata AS
    SELECT
        md_hash AS file_id,
        md_json->'attributes'->>'project_id' as project,
        md_json->'attributes'->>'product' as product,
        md_json->'attributes'->>'institute_id' as institute,
        md_json->'attributes'->>'model_id' as model,
        md_json->'attributes'->>'experiment_id' as experiment,
        md_json->'attributes'->>'frequency' as frequency,
        md_json->'attributes'->>'modeling_realm' as realm,
        md_json->'attributes'->>'realization' as r,
        md_json->'attributes'->>'initialization_method' as i,
        md_json->'attributes'->>'physics_version' as p,
        substring(md_json->'attributes'->>'table_id','Table (\S+) .*') as cmor_table
    FROM metadata
    JOIN esgf_paths ON md_hash = file_id
    WHERE md_type = 'netcdf'
    AND cmip_era = 5;

/* modified this so it works with both cmip5 and cmip6 using attributes_map.json */
CREATE OR REPLACE VIEW c6_dataset_metadata AS
    SELECT
        md_hash AS file_id,
        md_json->'attributes'->>'activity_id' as activity_id,
        md_json->'attributes'->>'mip_era' as project,
        md_json->'attributes'->>'institution_id' as institution_id,
        md_json->'attributes'->>'mip_era' as mip_era,
        md_json->'attributes'->>'source_id' as source_id,
        md_json->'attributes'->>'source_type' as source_type,
        md_json->'attributes'->>'experiment_id' as experiment_id,
        md_json->'attributes'->>'sub_experiment_id' as sub_experiment_id,
        md_json->'attributes'->>'frequency' as frequency,
        md_json->'attributes'->>'realm' as realm,
        md_json->'attributes'->>'realization_index' as r,
        md_json->'attributes'->>'initialization_index' as i,
        md_json->'attributes'->>'physics_index' as p,
        md_json->'attributes'->>'forcing_index' as f,
        md_json->'attributes'->>'variable_id' as variable_id,
        md_json->'attributes'->>'grid_label' as grid_label,
        md_json->'attributes'->>'nominal_resolution' as nominal_resolution,
        md_json->'attributes'->>'table_id' as table_id
    FROM metadata
    JOIN esgf_paths ON md_hash = file_id
    WHERE md_type = 'netcdf'
    AND cmip_era = 6;

CREATE MATERIALIZED VIEW IF NOT EXISTS c5_metadata_dataset_link AS
    SELECT
        file_id,
        md5(
            COALESCE(project,'') ||'.'||
            COALESCE(product,'') ||'.'||
            COALESCE(institute,'') ||'.'||
            model ||'.'||
            experiment ||'.'||
            frequency ||'.'||
            COALESCE(realm,'') ||'.'||
            COALESCE(cmor_table,'') ||'.'||
            COALESCE('r'||r||'i'||i||'p'||p,'')
        )::uuid as dataset_id
    FROM c5_dataset_metadata
    NATURAL JOIN esgf_paths;
CREATE UNIQUE INDEX IF NOT EXISTS c5_metadata_dataset_link_file_id ON c5_metadata_dataset_link(file_id);
CREATE INDEX IF NOT EXISTS c5_metadata_dataset_link_dataset_id ON c5_metadata_dataset_link(dataset_id);
GRANT SELECT ON c5_metadata_dataset_link TO PUBLIC;

/* we probably can eliminate coalesce for institution-id , activity and variant_label since they should always be there */
CREATE MATERIALIZED VIEW IF NOT EXISTS c6_metadata_dataset_link AS
    SELECT
        file_id,
        md5(
            COALESCE(mip_era,'') ||'.'||
            COALESCE(activity_id,'') ||'.'||
            COALESCE(institution_id,'') ||'.'||
            source_id ||'.'||
            experiment_id ||'.'||
            COALESCE(sub_experiment_id,'') ||'-'||
            COALESCE('r'||r||'i'||i||'p'||p||'f'||f,'') ||
            COALESCE(table_id,'') ||'.'||
            variable_id ||'.'||
            COALESCE(grid_label,'') ||'.'
        )::uuid as dataset_id
    FROM c6_dataset_metadata;
CREATE UNIQUE INDEX IF NOT EXISTS c6_metadata_dataset_link_file_id ON c6_metadata_dataset_link(file_id);
CREATE INDEX IF NOT EXISTS c6_metadata_dataset_link_dataset_id ON c6_metadata_dataset_link(dataset_id);
GRANT SELECT ON c6_metadata_dataset_link TO PUBLIC;


CREATE MATERIALIZED VIEW IF NOT EXISTS cmip5_dataset AS
    SELECT DISTINCT
        dataset_id,
        project,
        product,
        institute,
        CASE WHEN model = 'ACCESS1-0' THEN 'ACCESS1.0'
            WHEN model = 'ACCESS1-3' THEN 'ACCESS1.3'
            WHEN model = 'CSIRO-Mk3-6-0' THEN 'CSIRO-Mk3.6.0'
            WHEN model = 'CESM1-WACCM' THEN 'CESM1(WACCM)'
            WHEN model = 'MRI-AGCM3-2H' THEN 'MRI-AGCM3.2H'
            WHEN model = 'MRI-AGCM3-2S' THEN 'MRI-AGCM3.2S'
            WHEN model = 'bcc-csm1-1-m' THEN 'BCC-CSM1.1(m)'
            WHEN model = 'bcc-csm1-1' THEN 'BCC-CSM1.1'
            WHEN model = 'inmcm4' THEN 'INM-CM4'
            WHEN model = 'CESM1-CAM5' THEN 'CESM1(CAM5)'
            WHEN model = 'CESM1-BGC' THEN 'CESM1(BGC)'
            WHEN model = 'CESM1-CAM5-1-FV2' THEN 'CESM1(CAM5.1,FV2)'
            WHEN model = 'CESM1-FASTCHEM' THEN 'CESM1(FASTCHEM)'
            ELSE model END
            AS model,
        experiment,
        frequency,
        realm,
        cmor_table,
        r,
        i,
        p,
        'r'||r||'i'||i||'p'||p AS ensemble
    FROM c5_dataset_metadata
    NATURAL JOIN c5_metadata_dataset_link;
CREATE UNIQUE INDEX IF NOT EXISTS cmip5_dataset_dataset_id ON cmip5_dataset(dataset_id);
GRANT SELECT ON cmip5_dataset TO PUBLIC;
    
CREATE MATERIALIZED VIEW IF NOT EXISTS cmip6_dataset AS
    SELECT DISTINCT
        dataset_id,
        project,
        activity_id,  /** .e.CMIP for DECK etc **/ 
        institution_id,
        source_id,  /** instead of model **/
        source_type,  /** AOGM, BGC **/
        experiment_id,
        sub_experiment_id,
        frequency,
        realm,
        mip_era, /** this should always be CMIP6 so might be skipped as well? **/
        r,
        i,
        p,
        f,
        'r'||r||'i'||i||'p'||p||'f'||f AS variant_label,
        sub_experiment_id||'-'||'r'||r||'i'||i||'p'||p||'f'||f AS member_id,
        variable_id,
        grid_label,
        nominal_resolution,
        table_id     /** instead of cmor_table **/
    FROM c6_dataset_metadata
    NATURAL JOIN c6_metadata_dataset_link;
CREATE UNIQUE INDEX IF NOT EXISTS cmip6_dataset_dataset_id ON cmip6_dataset(dataset_id);
GRANT SELECT ON cmip6_dataset TO PUBLIC;
/* Extra metadata not stored in the file itself. This table stores manually
 * entered data, automatic data is in the view `extended_metadata_path` and
 * both are combined in the materialized view `extended_metadata`.
 *
 * Users should go through the 'extended_metadata' table
 */
CREATE TABLE IF NOT EXISTS extended_metadata_manual (
    file_id UUID PRIMARY KEY,
    version TEXT,
    variable TEXT,
    period INT4RANGE  /* Date stored as a 6 character integer, e.g. 198001
                         to avoid calendar issues */
    );

/* Users can add their own messages here
 */
CREATE TABLE IF NOT EXISTS errata (
    id SERIAL PRIMARY KEY,
    value TEXT,
    added_by TEXT DEFAULT CURRENT_USER,
    added_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
GRANT SELECT ON errata TO PUBLIC;
GRANT INSERT (value) ON errata TO PUBLIC;

/* Links an errata message to a file
 */
CREATE TABLE IF NOT EXISTS file_errata_link (
    errata_id INTEGER REFERENCES errata(id) ON DELETE CASCADE,
    file_id UUID,
    added_by TEXT DEFAULT CURRENT_USER,
    added_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (errata_id, file_id)
    );
GRANT SELECT ON file_errata_link TO PUBLIC;
GRANT INSERT (errata_id, file_id) ON file_errata_link TO PUBLIC;

/* Gather information from the file path that isn't present in the file
 * attributes. This won't always be correct, values can be overriden by adding
 * a row in `extended_metadata_manual` and refreshing `extended_metadata`
 */
CREATE OR REPLACE VIEW extended_metadata_path AS
    WITH x AS (
        SELECT file_id, string_to_array(path,'/') AS path_parts
        FROM esgf_paths),
    y AS (
        SELECT file_id, path_parts[array_length(path_parts,1)-2] AS version
        FROM x),
    versions AS (
        SELECT file_id, SUBSTRING(version, '^v?(\d+)$') AS version  FROM y WHERE version ~* '^v?\d+$'),
    variables AS (
        SELECT file_id, split_part(path_parts[array_length(path_parts,1)],'_',1) AS variable
        FROM x),
    b AS (
        SELECT file_id, substring(path,'\d+-\d+(?=\.nc$)') AS dates
        FROM esgf_paths),
    c AS (
        SELECT file_id, substr(split_part(dates,'-',1),1,6)::int AS l, substr(split_part(dates,'-',2),1,6)::int AS h
        FROM b),
    d AS (
        SELECT file_id, int4range(l,h,'[]') AS period
        FROM c WHERE l <= h),
    access_versions AS (
        SELECT file_id, split_part(path_parts[array_length(path_parts,1)-1],'_',2) as access_version
        FROM x WHERE path_parts[5] = 'authoritative'
        )

    SELECT file_id, COALESCE(access_version, version) AS version, variable, period
    FROM variables
    NATURAL LEFT JOIN versions
    NATURAL LEFT JOIN access_versions
    NATURAL LEFT JOIN d;

CREATE MATERIALIZED VIEW IF NOT EXISTS extended_metadata AS
    SELECT
        file_id, 
        COALESCE(m.version, p.version) AS version,
        COALESCE(m.variable, p.variable) AS variable,
        COALESCE(m.period, p.period) AS period
    FROM extended_metadata_path AS p
    NATURAL LEFT JOIN extended_metadata_manual AS m;
GRANT SELECT ON extended_metadata TO PUBLIC;
CREATE UNIQUE INDEX IF NOT EXISTS extended_metadata_file_id ON extended_metadata(file_id);
