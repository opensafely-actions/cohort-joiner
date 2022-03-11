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
def csv_dataframe(tmp_path, dataframe):
    csv_path = tmp_path / "input.csv"
    dataframe.to_csv(csv_path, index=False)
    return csv_path, dataframe


class TestReadDataframe:
    def test_read_csv(self, csv_dataframe):
        csv_path, dataframe_in = csv_dataframe
        dataframe_out = cohort_joiner.read_dataframe(csv_path)
        pandas_testing.assert_frame_equal(dataframe_in, dataframe_out)

    def test_read_xlsx(self):
        # xlsx is not supported
        dataframe_out = cohort_joiner.read_dataframe(pathlib.Path("input.xlsx"))
        assert dataframe_out is None


class TestWriteDataframe:
    def test_write_csv(self, tmp_path, dataframe):
        csv_path = tmp_path / "input.csv"
        cohort_joiner.write_dataframe(dataframe, csv_path)
        assert csv_path.exists()

    def test_write_xlsx(self, tmp_path, dataframe):
        xlsx_path = tmp_path / "input.xlsx"
        cohort_joiner.write_dataframe(dataframe, xlsx_path)
        assert not xlsx_path.exists()


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
            "patient_id": [1],
            "has_sbp_event": [True],
            "sbp_event_code": [198081000000101],
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
            "patient_id": [1],
            "has_sbp_event": [True],
            "sbp_event_code": [198081000000101],
            "ethnicity": [1],
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
            "--lhs_paths",
            "input_2021-*.csv",
            "--rhs_paths",
            "input_ethnicity.csv",
        ],
    )
    for name in ["input_2021-01-01.csv", "input_ethnicity.csv"]:
        pathlib.Path(name).touch()

    args = cohort_joiner.parse_args()

    assert args.lhs_paths == [tmp_path / "input_2021-01-01.csv"]
    assert args.rhs_paths == [tmp_path / "input_ethnicity.csv"]
