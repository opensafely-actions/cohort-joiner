from cohortextractor import StudyDefinition, codelist_from_csv, patients


sbp_codelist = codelist_from_csv(
    "codelists/opensafely-systolic-blood-pressure-qof.csv",
    system="snomed",
    column="code",
)

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1921-01-01", "latest": "2021-01-01"},
        "rate": "uniform",
        "incidence": 1,
    },
    index_date="2021-01-01",
    population=patients.satisfying("is_registered AND NOT is_dead"),
    is_registered=patients.registered_as_of(reference_date="index_date"),
    is_dead=patients.died_from_any_cause(
        on_or_before="index_date",
        return_expectations={"incidence": 0.1},
    ),
    has_sbp_event=patients.with_these_clinical_events(
        codelist=sbp_codelist,
        between=["index_date", "index_date"],
        return_expectations={"incidence": 0.1},
    ),
    sbp_event_code=patients.with_these_clinical_events(
        codelist=sbp_codelist,
        between=["index_date", "index_date"],
        returning="code",
        return_expectations={
            "category": {"ratios": {x: 1 / len(sbp_codelist) for x in sbp_codelist}},
            "incidence": 0.1,
        },
    ),
)
