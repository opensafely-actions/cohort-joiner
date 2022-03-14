# cohort-joiner

cohort-joiner performs a database-style [left join][] between several left-hand cohorts and a single right-hand cohort.
Typically, the left-hand cohorts are several weekly or monthly extracts of pseudonymised patient data for variables that are expected to change by week or by month.
The right-hand cohort is a single extract of these data for variables that are not expected to change.
Extracting and joining the cohorts in this way is more efficient than several weekly or monthly extracts of these data for all variables.

[left join]: https://en.wikipedia.org/wiki/Join_(SQL)#Left_outer_join

## Usage

[_project.yaml_][] in cohort-joiner's GitHub repository demonstrates how to use cohort-joiner.
In summary:

* Use [cohort-extractor][] to extract the left-hand cohorts.
  These are several weekly or monthly extracts for variables that are expected to change,
  such as whether a patient has experienced an <abbr title="Systolic Blood Pressure">SBP</abbr> event.
* Use cohort-extractor to extract the right hand cohort.
  This is a single extract for variables that are not expected to change, such as ethnicity.
* Use cohort-joiner to join the cohorts.

[_project.yaml_]: https://github.com/opensafely-actions/cohort-joiner
[cohort-extractor]: https://docs.opensafely.org/actions-cohortextractor/

## Notes for developers

Please see [_DEVELOPERS.md_](DEVELOPERS.md).
