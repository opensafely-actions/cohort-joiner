import argparse
import glob
import pathlib

import pandas
from cohortextractor import pandas_utils


def read_dataframe(path):
    ext = get_extension(path)
    if ext == ".csv" or ext == ".csv.gz":
        return pandas.read_csv(path)
    elif ext == ".feather":
        return pandas.read_feather(path)
    elif ext == ".dta" or ext == ".dta.gz":
        return pandas.read_stata(path)
    else:
        raise ValueError(f"Cannot read '{ext}' files")


def write_dataframe(dataframe, path):
    # We refactored this function, replacing copy-and-paste code from cohort-extractor
    # with a call to cohort-extractor itself. However, the error types differed. We
    # preserved the pre-refactoring error type.
    try:
        pandas_utils.dataframe_to_file(dataframe, path)
    except RuntimeError:
        ext = get_extension(path)
        raise ValueError(f"Cannot write '{ext}' files")


def get_extension(path):
    return "".join(path.suffixes)


def get_new_path(old_path, suffix="_joined"):
    ext = get_extension(old_path)
    name = old_path.name.split(ext)[0]
    return old_path.with_name(f"{name}{suffix}{ext}")


def left_join(lhs_dataframe, rhs_dataframe):
    return lhs_dataframe.merge(rhs_dataframe, how="left", on="patient_id")


def get_path(*args):
    return pathlib.Path(*args).resolve()


def match_paths(pattern):
    return [get_path(x) for x in glob.glob(pattern)]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lhs",
        dest="lhs_paths",
        required=True,
        type=match_paths,
        metavar="LHS_PATTERN",
        help="Glob pattern for matching one or more dataframes that will form the left-hand side of the join",
    )
    parser.add_argument(
        "--rhs",
        dest="rhs_paths",
        required=True,
        type=match_paths,
        metavar="RHS_PATTERN",
        help="Glob pattern for matching one dataframe that will form the right-hand side of the join",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    lhs_paths = args.lhs_paths
    rhs_path = args.rhs_paths[0]

    rhs_dataframe = read_dataframe(rhs_path)
    for lhs_path in lhs_paths:
        lhs_dataframe = read_dataframe(lhs_path)
        lhs_dataframe = left_join(lhs_dataframe, rhs_dataframe)
        new_lhs_path = get_new_path(lhs_path)
        write_dataframe(lhs_dataframe, new_lhs_path)


if __name__ == "__main__":
    main()
