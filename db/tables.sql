CREATE OR REPLACE VIEW esgf_filter AS
    SELECT
        pa_hash AS file_id
    FROM paths
    WHERE
        pa_type = 'file'
        AND pa_parents[6] = md5('/g/data1/ua6/unofficial-ESG-replica/tmp/tree')::uuid;


CREATE OR REPLACE VIEW dataset_metadata AS
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
        md_json->'attributes'->>'physics_version' as p
    FROM metadata
    WHERE md_type = 'netcdf';


CREATE MATERIALIZED VIEW IF NOT EXISTS esgf_metadata_dataset_link AS
    SELECT
        file_id,
        md5(
            COALESCE(project,'') ||'.'||
            COALESCE(product,'') ||'.'||
            COALESCE(institute,'') ||'.'||
            model ||'.'||
            experiment ||'.'||
            frequency ||'.'||
            realm ||'.'||
            'r'||r||'i'||i||'p'||p
        )::uuid as dataset_id
    FROM dataset_metadata
    NATURAL JOIN esgf_filter;
CREATE INDEX esgf_metadata_dataset_link_file_id ON esgf_metadata_dataset_link(file_id);
CREATE INDEX esgf_metadata_dataset_link_dataset_id ON esgf_metadata_dataset_link(dataset_id);
GRANT SELECT ON esgf_metadata_dataset_link TO PUBLIC;


CREATE MATERIALIZED VIEW IF NOT EXISTS esgf_dataset AS
    SELECT DISTINCT
        dataset_id,
        project,
        product,
        institute,
        model,
        experiment,
        frequency,
        realm,
        r,
        i,
        p,
        'r'||r||'i'||i||'p'||p AS ensemble
    FROM dataset_metadata
    NATURAL JOIN esgf_metadata_dataset_link;
CREATE INDEX IF NOT EXISTS esgf_dataset_dataset_id ON esgf_dataset(dataset_id);
GRANT SELECT ON esgf_dataset TO PUBLIC;
    
    
