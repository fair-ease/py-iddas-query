from argparse import ArgumentParser
import sys
from logging import getLogger
from pathlib import Path
from sema.commons.glob import getMatchingGlobPaths
from sema.commons.j2 import J2RDFSyntaxBuilder
from sema.query import GraphSource, QueryResult
from io import StringIO

log = getLogger(__name__)
QRY_FLDR = Path(__file__).parent / "query"
# have a central J2_syntac builder to inspect and execute the queries
J2SB: J2RDFSyntaxBuilder = J2RDFSyntaxBuilder(templates_folder=QRY_FLDR)


def listinfo(args):
    if args.query is None:
        list_queries()
        return True
    # else
    list_vars(args.query)
    return True


def list_queries() -> list[str]:
    files = getMatchingGlobPaths(QRY_FLDR, includes=["*.sparql"])
    qrynames = [f.stem for f in files]
    qrynames.sort()
    log.debug(f"Available queries found are: {qrynames}")
    if (not qrynames):
        print("No queries found in the query folder")
        return []
    # else
    print("Available queries found are:")
    print(" - " + "\n - ".join(qrynames))
    return qrynames


def check_query_exists(qryname: str):
    filename = f"{qryname}.sparql"
    if not (QRY_FLDR / filename).exists():
        raise ValueError(f"Query with name {qryname} does not have a matching template file")
    return filename


def list_vars(qryname: str) -> list[str]:
    filename = check_query_exists(qryname)
    # then use the j2 querybuilder to inspect the vars
    vars = list(J2SB.variables_in_template(filename))
    vars.sort()
    if (not vars):
        print(f"No variables found for query {qryname}")
        return []
    # else
    print(f"Variables needed for query {qryname} are:")
    print(" - " + "\n - ".join(vars))
    return vars


def query(args):
    qryname = args.query
    params = {k: v for k, v in args.var} if args.var else {}

    try:
        filename = check_query_exists(qryname)

        # then use the j2 querybuilder to execute the query
        qry = J2SB.build_syntax(filename, **params)
        gs: GraphSource = GraphSource.build(args.url)
        # raise ValueError("breaking here")
        qr: QueryResult = gs.query(qry)
        # handle output
        handle_output(qr, bool(args.output == "-"), Path(args.output), args.force)

    except Exception as e:
        print(f"Error: {e}")
        print(f"Failed to execute query {qryname=}, {params=} on server {args.url}")
        print("Using qry:\n--\n", qry, "\n--")
        return False
    # else
    return True


def handle_output(qr: QueryResult, is_stdout: bool, out_path: Path, force: bool):
    if is_stdout:
        io = StringIO()
    else:
        if not force and out_path.exists():
            raise FileExistsError(f"Output file {out_path} already exists")
    # else
    # for now just dump as csv - have to convert to some json later
    qr.as_csv(io if is_stdout else out_path)
    if is_stdout:
        print(io.getvalue())


def get_arg_parser() -> ArgumentParser:
    """
    Defines the arguments to this script by using Python's
    [argparse](https://docs.python.org/3/library/argparse.html)
    """
    parser = ArgumentParser(
        description=(
            "A tool to find matching datasources in "
            "the FE Asset Catalog (IDDAS) and expose them as json entries "
            "to be pasted into the TerriaMap config."
        ),
    )

    # subparsers for LIST and QUERY commands
    subparsers = parser.add_subparsers(
        title="actions",
        description="valid actions",
        required=True,
    )

    ls_parser = subparsers.add_parser(
        "list",
        aliases=["ls", "l"],
        help=(
            "List all available queries, "
            "or list the available params for a selected query"
        ),
    )

    ls_parser.add_argument(
        "query",
        nargs="?",  # optional
        metavar="QUERYNAME",  # meaning of the argument
        action="store",
        help=(
            "Selects the query for which to list the available params. "
            "If not provided, lists all available queries."
        ),
    )

    ls_parser.set_defaults(func=listinfo)

    qry_parser = subparsers.add_parser(
        "query",
        aliases=["q", "qry"],
        help="Execute the choosen query",
    )

    qry_parser.add_argument(
        "query",
        metavar="QUERYNAME",  # meaning of the argument
        action="store",
        help="Selects the query (template) to use in combo with the passed variables",
    )

    qry_parser.add_argument(
        "-v",
        "--var",
        nargs=2,  # each -v should have 2 arguments
        metavar=("NAME", "VALUE"),  # meaning/purpose of those arguments
        action="append",  # multiple -v can be combined
        help=(
            "Multiple entries will add different named "
            "variables to the querying process"
        ),
    )

    qry_parser.add_argument(
        "-o",
        "--output",
        metavar="FILE|-",  # meaning of the argument
        default="-",  # stdout
        action="store",
        help="Specifies where to write the output, can be - for stdout.",
    )

    qry_parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help=(
            "Force writing output, do not check "
            "if output files already exist."
        ),
    )

    qry_parser.add_argument(
        "-u",
        "--url",
        default="https://fair-ease-iddas.maris.nl/sparql/query",  # fair-ease
        action="store",
        help=(
            "Specify the url for the sparql endpoint to query. "
            "Defaults to Fair-Ease IDDAS"
        ),
    )

    qry_parser.set_defaults(func=query)

    return parser


def _main(*args_list) -> bool:
    """The main entry point to this module."""
    args = get_arg_parser().parse_args(args_list)
    success = args.func(args)
    return success


def main():
    success: bool = _main(*sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
