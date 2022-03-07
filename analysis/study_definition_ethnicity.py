from cohortextractor import StudyDefinition, codelist_from_csv, patients


ethnicity_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    system="ctv3",
    column="Code",
    category_column="Grouping_6",
)

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1921-01-01", "latest": "2021-01-01"},
        "rate": "uniform",
        "incidence": 1,
    },
    index_date="2021-01-01",
    population=patients.all(),
    ethnicity=patients.with_these_clinical_events(
        ethnicity_codelist,
        returning="category",
        find_last_match_in_period=True,
        return_expectations={
            "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
            "incidence": 0.75,
        },
    ),
)
