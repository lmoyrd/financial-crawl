-- Table: public.KCB_PROCESS

-- DROP TABLE IF EXISTS public."KCB_PROCESS";

CREATE TABLE IF NOT EXISTS public."KCB_PROCESS"
(
    company_id text COLLATE pg_catalog."default",
    company_name text COLLATE pg_catalog."default",
    stage integer,
    stage_name text COLLATE pg_catalog."default",
    stage_status integer,
    stage_status_name text COLLATE pg_catalog."default",
    "timestamp" bigint,
    date text COLLATE pg_catalog."default",
    project_id text COLLATE pg_catalog."default",
    id text COLLATE pg_catalog."default" NOT NULL,
    reason text COLLATE pg_catalog."default",
    CONSTRAINT id PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."KCB_PROCESS"
    OWNER to postgres;

COMMENT ON TABLE public."KCB_PROCESS"
    IS '公司进程';

COMMENT ON COLUMN public."KCB_PROCESS".company_id
    IS '公司名称';

COMMENT ON COLUMN public."KCB_PROCESS".company_name
    IS '公司名称';

COMMENT ON COLUMN public."KCB_PROCESS".stage
    IS '项目所处流程';

COMMENT ON COLUMN public."KCB_PROCESS".stage_name
    IS '阶段名';

COMMENT ON COLUMN public."KCB_PROCESS".stage_status
    IS '阶段状态';

COMMENT ON COLUMN public."KCB_PROCESS"."timestamp"
    IS '时间戳';

-- Table: public.KCB_OTHER

-- DROP TABLE IF EXISTS public."KCB_OTHER";

CREATE TABLE IF NOT EXISTS public."KCB_OTHER"
(
    company_id text COLLATE pg_catalog."default",
    company_name text COLLATE pg_catalog."default",
    stage integer,
    stage_name text COLLATE pg_catalog."default",
    stage_status integer,
    stage_status_name text COLLATE pg_catalog."default",
    "timestamp" bigint,
    date text COLLATE pg_catalog."default",
    project_id text COLLATE pg_catalog."default",
    id text COLLATE pg_catalog."default" NOT NULL,
    reason text COLLATE pg_catalog."default",
    CONSTRAINT "KCB_OTHER_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

-- Table: public.KCB_MILESTONE

-- DROP TABLE IF EXISTS public."KCB_MILESTONE";

CREATE TABLE IF NOT EXISTS public."KCB_MILESTONE"
(
    company_id text COLLATE pg_catalog."default",
    company_name text COLLATE pg_catalog."default",
    stage integer,
    stage_name text COLLATE pg_catalog."default",
    stage_status integer,
    stage_status_name text COLLATE pg_catalog."default",
    "timestamp" bigint,
    date text COLLATE pg_catalog."default",
    project_id text COLLATE pg_catalog."default",
    id text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "KCB_MILESTONE_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

-- Table: public.KCB_IPO

-- DROP TABLE IF EXISTS public."KCB_IPO";

CREATE TABLE IF NOT EXISTS public."KCB_IPO"
(
    project_id text COLLATE pg_catalog."default" NOT NULL,
    total_fund_rasing double precision NOT NULL DEFAULT 0.0,
    stage integer NOT NULL,
    stage_status integer,
    biz_type integer,
    csrc_code character varying(10) COLLATE pg_catalog."default",
    law_office_id text COLLATE pg_catalog."default",
    sponsor_id text COLLATE pg_catalog."default",
    sponsor_name text COLLATE pg_catalog."default",
    accounting_firm_id text COLLATE pg_catalog."default",
    accounting_firm_name text COLLATE pg_catalog."default",
    rating_agency_id text COLLATE pg_catalog."default",
    rating_agency_name text COLLATE pg_catalog."default",
    accept_apply_date text COLLATE pg_catalog."default",
    law_office_name text COLLATE pg_catalog."default",
    asset_evaluation_institute_id text COLLATE pg_catalog."default",
    asset_evaluation_institute_name text COLLATE pg_catalog."default",
    company_id text COLLATE pg_catalog."default",
    update_date text COLLATE pg_catalog."default",
    create_date text COLLATE pg_catalog."default",
    company_name text COLLATE pg_catalog."default",
    stage_name character varying(20) COLLATE pg_catalog."default",
    stage_status_name character varying(20) COLLATE pg_catalog."default",
    issue_market integer,
    csrc_desc text COLLATE pg_catalog."default",
    accept_apply_time bigint,
    update_time bigint,
    create_time bigint,
    CONSTRAINT "KCB_IPO_pkey" PRIMARY KEY (project_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."KCB_IPO"
    OWNER to postgres;

COMMENT ON TABLE public."KCB_IPO"
    IS '科创板IPO信息';

COMMENT ON COLUMN public."KCB_IPO".project_id
    IS '工程id';

COMMENT ON COLUMN public."KCB_IPO".total_fund_rasing
    IS '总募资金额';

COMMENT ON COLUMN public."KCB_IPO".stage
    IS '当前所处阶段';

COMMENT ON COLUMN public."KCB_IPO".stage_status
    IS '当前所处阶段状态';

COMMENT ON COLUMN public."KCB_IPO".biz_type
    IS '业务类型';

COMMENT ON COLUMN public."KCB_IPO".csrc_code
    IS '证监会行业分类码';

COMMENT ON COLUMN public."KCB_IPO".law_office_id
    IS '律所机构id';

COMMENT ON COLUMN public."KCB_IPO".sponsor_id
    IS '保荐机构id';

COMMENT ON COLUMN public."KCB_IPO".sponsor_name
    IS '保荐机构名';

COMMENT ON COLUMN public."KCB_IPO".accounting_firm_id
    IS '会计事务所id';

COMMENT ON COLUMN public."KCB_IPO".accounting_firm_name
    IS '会计事务所名';

COMMENT ON COLUMN public."KCB_IPO".rating_agency_id
    IS '资信评级机构id';

COMMENT ON COLUMN public."KCB_IPO".rating_agency_name
    IS '资信评级机构名';

COMMENT ON COLUMN public."KCB_IPO".accept_apply_date
    IS '交易所受理时间';

COMMENT ON COLUMN public."KCB_IPO".law_office_name
    IS '律所名';

COMMENT ON COLUMN public."KCB_IPO".asset_evaluation_institute_id
    IS '资产评估机构id';

COMMENT ON COLUMN public."KCB_IPO".asset_evaluation_institute_name
    IS '资产评估机构';

COMMENT ON COLUMN public."KCB_IPO".company_id
    IS '公司id';

-- Table: public.KCB_INTERMEDIARY_PERSON

-- DROP TABLE IF EXISTS public."KCB_INTERMEDIARY_PERSON";

CREATE TABLE IF NOT EXISTS public."KCB_INTERMEDIARY_PERSON"
(
    project_id text COLLATE pg_catalog."default",
    intermediary_id text COLLATE pg_catalog."default",
    id text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default",
    job_type integer,
    job_title text COLLATE pg_catalog."default",
    CONSTRAINT "KCB_INTERMEDIARY_PERSON_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."KCB_INTERMEDIARY_PERSON"
    OWNER to postgres;

COMMENT ON TABLE public."KCB_INTERMEDIARY_PERSON"
    IS '科创板机构人员';

-- Table: public.KCB_INTERMEDIARY

-- DROP TABLE IF EXISTS public."KCB_INTERMEDIARY";

CREATE TABLE IF NOT EXISTS public."KCB_INTERMEDIARY"
(
    type bigint,
    name text COLLATE pg_catalog."default",
    intermeidary_order bigint DEFAULT '-1'::integer,
    intermediary_id text COLLATE pg_catalog."default" NOT NULL,
    project_id text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "中介id" PRIMARY KEY (intermediary_id, project_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."KCB_INTERMEDIARY"
    OWNER to postgres;

COMMENT ON TABLE public."KCB_INTERMEDIARY"
    IS '科创板中介机构';

COMMENT ON COLUMN public."KCB_INTERMEDIARY".type
    IS '中介类型';

COMMENT ON COLUMN public."KCB_INTERMEDIARY".name
    IS '中介机构名称';

COMMENT ON COLUMN public."KCB_INTERMEDIARY".intermeidary_order
    IS '中介机构顺序';

-- Table: public.KCB_FILE

-- DROP TABLE IF EXISTS public."KCB_FILE";

CREATE TABLE IF NOT EXISTS public."KCB_FILE"
(
    file_id text COLLATE pg_catalog."default" NOT NULL,
    file_name text COLLATE pg_catalog."default",
    file_url text COLLATE pg_catalog."default",
    file_size integer,
    publish_time bigint,
    file_type_of_process integer,
    file_type_of_audit integer,
    file_type_of_process_desc character varying(20) COLLATE pg_catalog."default",
    file_type_of_audit_desc character varying(20) COLLATE pg_catalog."default",
    company_name character varying(50) COLLATE pg_catalog."default",
    stage integer,
    stage_name character varying(20) COLLATE pg_catalog."default",
    project_id text COLLATE pg_catalog."default",
    company_id text COLLATE pg_catalog."default",
    publish_date text COLLATE pg_catalog."default",
    CONSTRAINT "KCB_FILE_pkey" PRIMARY KEY (file_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."KCB_FILE"
    OWNER to postgres;

COMMENT ON TABLE public."KCB_FILE"
    IS '文件信息';

COMMENT ON COLUMN public."KCB_FILE".file_name
    IS '文件名';

COMMENT ON COLUMN public."KCB_FILE".file_url
    IS '文件url';

COMMENT ON COLUMN public."KCB_FILE".file_size
    IS '文件大小';

COMMENT ON COLUMN public."KCB_FILE".publish_time
    IS '上传时间/更新时间';

COMMENT ON COLUMN public."KCB_FILE".file_type_of_process
    IS '文件所属进程类型，说明文件所属进度节点；由于科创板没有区分这两种类型，所以在科创板这里定义为一样的数据';

COMMENT ON COLUMN public."KCB_FILE".file_type_of_audit
    IS '文件所属审核类型，提交给权力机关的类型；由于科创板没有区分这两种类型，所以在科创板这里定义为一样的数据';

COMMENT ON COLUMN public."KCB_FILE".file_type_of_process_desc
    IS '文件所属进程类型中文';

COMMENT ON COLUMN public."KCB_FILE".file_type_of_audit_desc
    IS '文件所属审核类型中文';

COMMENT ON COLUMN public."KCB_FILE".stage
    IS '文件所属阶段';

-- Table: public.INTERMEDIARY

-- DROP TABLE IF EXISTS public."INTERMEDIARY";

CREATE TABLE IF NOT EXISTS public."INTERMEDIARY"
(
    id text COLLATE pg_catalog."default" NOT NULL,
    name character varying(50) COLLATE pg_catalog."default",
    abbr text COLLATE pg_catalog."default",
    code character varying(10) COLLATE pg_catalog."default",
    csrc_company_type integer,
    csrc_code character varying(10) COLLATE pg_catalog."default",
    csrc_desc text COLLATE pg_catalog."default",
    province text COLLATE pg_catalog."default",
    city text COLLATE pg_catalog."default",
    phone text COLLATE pg_catalog."default",
    website text COLLATE pg_catalog."default",
    email text COLLATE pg_catalog."default",
    csrc_parent_code "char",
    loc text COLLATE pg_catalog."default",
    CONSTRAINT "INTERMEDIARY_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

-- Table: public.COMPANY_MANAGER

-- DROP TABLE IF EXISTS public."COMPANY_MANAGER";

CREATE TABLE IF NOT EXISTS public."COMPANY_MANAGER"
(
    company_id text COLLATE pg_catalog."default",
    company_name text COLLATE pg_catalog."default",
    id text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default",
    job_title text COLLATE pg_catalog."default",
    CONSTRAINT "COMPANY_MANAGER_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."COMPANY_MANAGER"
    OWNER to postgres;

COMMENT ON TABLE public."COMPANY_MANAGER"
    IS '公司高管';

COMMENT ON COLUMN public."COMPANY_MANAGER".job_title
    IS '任职名称';

-- Table: public.COMPANY

-- DROP TABLE IF EXISTS public."COMPANY";

CREATE TABLE IF NOT EXISTS public."COMPANY"
(
    id text COLLATE pg_catalog."default" NOT NULL,
    name character varying(50) COLLATE pg_catalog."default",
    abbr character varying(10) COLLATE pg_catalog."default",
    code character varying(10) COLLATE pg_catalog."default",
    csrc_company_type integer,
    csrc_code character varying(10) COLLATE pg_catalog."default",
    csrc_desc text COLLATE pg_catalog."default",
    province character varying(10) COLLATE pg_catalog."default",
    city text COLLATE pg_catalog."default",
    phone text COLLATE pg_catalog."default",
    website text COLLATE pg_catalog."default",
    email text COLLATE pg_catalog."default",
    csrc_parent_code "char",
    loc text COLLATE pg_catalog."default",
    CONSTRAINT "KCB_COMPANY_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."COMPANY"
    OWNER to postgres;

COMMENT ON TABLE public."COMPANY"
    IS '预上市公司';

COMMENT ON COLUMN public."COMPANY".id
    IS '公司id';

COMMENT ON COLUMN public."COMPANY".name
    IS '公司名称';

COMMENT ON COLUMN public."COMPANY".abbr
    IS '公司简称';

COMMENT ON COLUMN public."COMPANY".code
    IS '公司证券代码';

COMMENT ON COLUMN public."COMPANY".csrc_company_type
    IS '证监会行业类型';

COMMENT ON COLUMN public."COMPANY".csrc_code
    IS '证监会行业分类代码';

COMMENT ON COLUMN public."COMPANY".csrc_desc
    IS '证监会行业分类';

COMMENT ON COLUMN public."COMPANY".province
    IS '省份';

COMMENT ON COLUMN public."COMPANY".city
    IS '公司所在城市';

COMMENT ON COLUMN public."COMPANY".phone
    IS '手机号';

COMMENT ON COLUMN public."COMPANY".website
    IS '网站';

COMMENT ON COLUMN public."COMPANY".csrc_parent_code
    IS '证监会分类代码父级';

COMMENT ON COLUMN public."COMPANY".loc
    IS '公司地址';