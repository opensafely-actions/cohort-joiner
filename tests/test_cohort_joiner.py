import csv
import gzip
import pathlib

import pandas
import pytest
from pandas import testing as pandas_testing

from analysis import cohort_joiner


@pytest.fixture
def dataframe():
    return pandas.DataFrame(
        {
            "patient_id": [1],
            "has_sbp_event": [True],
            "sbp_event_code": [198081000000101],
        }
    )


@pytest.fixture
def write_dataframe(tmp_path, dataframe):
    def _write_dataframe(ext):
        path = tmp_path / f"input{ext}"
        cohort_joiner.write_dataframe(dataframe, path)
        return path, dataframe

    return _write_dataframe


class TestReadDataframe:
    @pytest.mark.parametrize("ext", [".csv"])
    def test_read_supported_file_type(self, write_dataframe, ext):
        path, dataframe_in = write_dataframe(ext)
        dataframe_out = cohort_joiner.read_dataframe(path)
        pandas_testing.assert_frame_equal(dataframe_in, dataframe_out)

    def test_read_unsupported_file_type(self):
        with pytest.raises(ValueError):
            cohort_joiner.read_dataframe(pathlib.Path("input.xlsx"))


class TestWriteDataframe:
    @pytest.mark.parametrize(
        "ext,open_func",
        [
            (".csv", open),
            (".csv.gz", gzip.open),
        ],
    )
    def test_write_csv(self, tmp_path, ext, dataframe, open_func):
        csv_path = tmp_path / f"input{ext}"
        cohort_joiner.write_dataframe(dataframe, csv_path)
        # When writing a dataframe to a CSV, it's easy to write the dataframe's index,
        # too. If the index doesn't have a name, then the first column in the CSV won't
        # have a header. This is undesirable, as it can introduce subtle bugs into
        # downstream actions within the OpenSAFELY framework, especially those that
        # expect their input to resemble cohort-extractor's output. For this reason, we
        # read the CSV that we wrote, and test that the header row (the zeroth row) is
        # correct.
        with open_func(csv_path, "rt", newline="") as f:
            lines = list(csv.reader(f))
        assert list(dataframe.columns) == lines[0]

    def test_write_xlsx(self, tmp_path, dataframe):
        xlsx_path = tmp_path / "input.xlsx"
        with pytest.raises(ValueError):
            cohort_joiner.write_dataframe(dataframe, xlsx_path)


@pytest.mark.parametrize(
    "old_name,new_name",
    [
        ("input.csv", "input_joined.csv"),
        ("input.csv.gz", "input_joined.csv.gz"),
    ],
)
def test_get_new_path(tmp_path, old_name, new_name):
    assert tmp_path / new_name == cohort_joiner.get_new_path(tmp_path / old_name)


def test_left_join():
    lhs_dataframe = pandas.DataFrame(
        {
            "patient_id": [1, 3],
            "has_sbp_event": [True, True],
            "sbp_event_code": [198081000000101, 198081000000101],
        }
    )
    rhs_dataframe = pandas.DataFrame(
        {
            "patient_id": [1, 2],
            "ethnicity": [1, 1],
        }
    )
    exp_dataframe = pandas.DataFrame(
        {
            "patient_id": [1, 3],
            "has_sbp_event": [True, True],
            "sbp_event_code": [198081000000101, 198081000000101],
            "ethnicity": [1, None],
        }
    )
    obs_dataframe = cohort_joiner.left_join(lhs_dataframe, rhs_dataframe)
    pandas_testing.assert_frame_equal(exp_dataframe, obs_dataframe)


def test_parse_args(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        [
            "cohort_joiner.py",
            "--lhs",
            "input_2021-*.csv",
            "--rhs",
            "input_ethnicity.csv",
        ],
    )
    for name in ["input_2021-01-01.csv", "input_ethnicity.csv"]:
        pathlib.Path(name).touch()

    args = cohort_joiner.parse_args()

    assert args.lhs_paths == [tmp_path / "input_2021-01-01.csv"]
    assert args.rhs_paths == [tmp_path / "input_ethnicity.csv"]
