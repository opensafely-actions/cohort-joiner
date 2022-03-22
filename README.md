# cohort-joiner

cohort-joiner performs a database-style [left join][] between several left-hand cohorts and a single right-hand cohort.
Typically, the left-hand cohorts are several weekly or monthly extracts of pseudonymised patient data for variables that are expected to change by week or by month.
The right-hand cohort is a single extract of these data for variables that are not expected to change.
Extracting and joining the cohorts in this way is more efficient than several weekly or monthly extracts of these data for all variables.

[left join]: https://en.wikipedia.org/wiki/Join_(SQL)#Left_outer_join

## Usage

In summary:

* Use [cohort-extractor][] to extract the left-hand cohorts.
  These are several weekly or monthly extracts for variables that are expected to change,
  such as whether a patient has experienced an <abbr title="Systolic Blood Pressure">SBP</abbr> event.
* Use cohort-extractor to extract the right hand cohort.
  This is a single extract for variables that are not expected to change, such as ethnicity.
* Use cohort-joiner to join the cohorts, and then to save them to an output directory.
* Optionally, use cohort-extractor to generate one or more measures from the joined cohorts.

Let's walk through an example _project.yaml_.

The following cohort-extractor action extracts the left-hand cohorts:

```yaml
generate_cohort:
  run: >
    cohortextractor:latest generate_cohort
      --study-definition study_definition
      --index-date-range "2021-01-01 to 2021-06-30 by month"
  outputs:
    highly_sensitive:
      cohort: output/input_2021-*.csv
```

The following cohort-extractor action extracts the right hand cohort:

```yaml
generate_ethnicity_cohort:
  run: >
    cohortextractor:latest generate_cohort
      --study-definition study_definition_ethnicity
  outputs:
    highly_sensitive:
      cohort: output/input_ethnicity.csv
```

The following cohort-joiner reusable action joins the cohorts, and then saves them to an output directory.
Remember to replace `[version]` with [a cohort-joiner version][1]:

```yaml
join_cohorts:
  run: >
    cohort-joiner:[version]
      --lhs output/input_2021-*.csv
      --rhs output/input_ethnicity.csv
      --output-dir output/joined
  needs: [generate_cohort, generate_ethnicity_cohort]
  outputs:
    highly_sensitive:
      cohort: output/joined/input_2021-*.csv
```

Optionally, the following cohort-extractor action generates one or more measures from the joined cohorts:

```yaml
generate_measures:
  run: >
    cohortextractor:latest generate_measures
      --study-definition study_definition
      --output-dir output/joined
  needs: [join_cohorts]
  outputs:
    moderately_sensitive:
      measure: output/joined/measure_*.csv
```

[1]: https://github.com/opensafely-actions/cohort-joiner/tags
[cohort-extractor]: https://docs.opensafely.org/actions-cohortextractor/

## Notes for developers

Please see [_DEVELOPERS.md_](DEVELOPERS.md).
