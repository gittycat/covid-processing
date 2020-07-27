--
-- Init tables
--

drop table if exists collections;
create table collections (
    id  serial PRIMARY KEY,
    labcode INT,
    collect_date DATE check (collect_date > '2020-01-01'),
    first_name VARCHAR(100),
    family_name VARCHAR(100),
    phone VARCHAR(100),
    phone2 VARCHAR(100),
    dob DATE check (dob > '1900-01-01'),
    address VARCHAR(100),
    suburb  VARCHAR(100),
    state   VARCHAR(100),
    postcode CHAR(4),
    contacted BOOLEAN default false,
    contact_date DATE check (contact_date > '2020-01-01'),
    contact_method VARCHAR(80),
    notes TEXT,
    UNIQUE(collect_date, dob, first_name, family_name)
);


drop table if exists lab_results;
create table lab_results (
    labcode INT UNIQUE NOT NULL,
    servicedate DATE,
    pat_idno INT NOT NULL,
    pat_surname VARCHAR(100),
    pat_given_name VARCHAR(100),
    sex VARCHAR(20),
    dateofbirth DATE check (dateofbirth > '1900-01-01'),
    pat_add1 VARCHAR(100),
    pat_add2 VARCHAR(100),
    pat_add3 VARCHAR(100),
    pat_pcode char(4),
    clinical_data_line_1 TEXT,
    clinical_data_line_2 TEXT,
    specimen_collection_date DATE,
    labname TEXT,
    proc TEXT,
    data_status TEXT,
    specimendate DATE,
    ageindays TEXT,
    ageinyears TEXT,
    senderscode TEXT,
    senders_surname TEXT,
    senders_initials TEXT,
    sendersadd1 TEXT,
    sendersadd2 TEXT,
    sendersadd3 TEXT,
    senders_pc TEXT,
    doc_idnumber TEXT,
    doc_surname TEXT,
    doc_initials TEXT,
    doc_provnumber TEXT,
    senders_ref TEXT,
    their_ref TEXT,
    vidrl_lab_no TEXT,
    specimen_type TEXT,
    specimen_site TEXT,
    wuhpcr TEXT,
    wuhpcr1 TEXT,
    wuhpcr2 TEXT,
    wuhpcr3 TEXT,
    wuhpcr4 TEXT,
    wuhpcr5 TEXT
);

