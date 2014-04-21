"""
This is the main file for perprof
"""

SUPPORT_MP = ['eps', 'pdf', 'png', 'ps', 'svg']
SUPPORT_TIKZ = ['tex', 'pdf']

import gettext
import os.path
import sys
import warnings

THIS_DIR, THIS_FILENAME = os.path.split(__file__)
THIS_TRANSLATION = gettext.translation('perprof',
        os.path.join(THIS_DIR, 'locale'))
_ = THIS_TRANSLATION.gettext

def process_arguments(args):
    """Generates the dictionaries with options"""
    parser_options = {
            'free_format': args.free_format,
            'files': args.file_name,
            'success': args.success.split(','),
            'maxtime': args.maxtime,
            'mintime': args.mintime,
            'use_obj_func': args.use_objective_function,
            'use_primal': args.use_primal_infeasibility,
            'use_dual': args.use_dual_infeasibility,
            'infeas_tol': args.infeasibility_tolerance
            }

    profiler_options = {
            'lang': args.lang,
            'cache': args.cache,
            'files': args.file_name,
            'force': args.force,
            'standalone': args.standalone,
            'semilog': args.semilog,
            'black_and_white': args.black_and_white,
            'output': args.output,
            'pgfplot_version': args.pgfplotcompat,
            'tau': args.tau,
            'pdf_verbose': args.pdf_verbose
            }

    if args.background is None:
        profiler_options['background'] = None
    else:
        # Set a tuple of integer
        profiler_options['background'] = tuple([int(i) for i in
            args.background.split(',')])
        assert len(profiler_options['background']) == 3, \
                _("RGB for background must have 3 integers")
    if args.page_background is None:
        profiler_options['page_background'] = None
    else:
        profiler_options['page_background'] = tuple([int(i) for i in args.page_background.split(',')])
        assert len(profiler_options['page_background']) == 3, \
                _("RGB for page background must have 3 integers")

    if args.eps:
        profiler_options['output_format'] = 'eps'
    elif args.pdf:
        profiler_options['output_format'] = 'pdf'
    elif args.png:
        profiler_options['output_format'] = 'png'
    elif args.ps:
        profiler_options['output_format'] = 'ps'
    elif args.svg:
        profiler_options['output_format'] = 'svg'
    elif args.tex:
        profiler_options['output_format'] = 'tex'
    else:
        if args.mp:
            profiler_options['output_format'] = 'png'
        elif args.tikz:
            profiler_options['output_format'] = 'pdf'
        else:
            profiler_options['output_format'] = None

    if args.mp and profiler_options['output_format'] not in SUPPORT_MP:
        raise NotImplementedError(_("Output option {} not supported by "
                "matplotlib").format(profiler_options['output_format'].upper()))
    elif args.tikz and profiler_options['output_format'] not in SUPPORT_TIKZ:
        raise NotImplementedError(_("Output option {} not supported by "
                "TikZ").format(profiler_options['output_format'].upper()))
    elif args.raw and profiler_options['output_format']:
        raise NotImplementedError(
                _("--raw does not support output except standard output"))

    if args.subset:
        with open(args.subset, 'r') as subset_file:
            parser_options['subset'] = [l.strip() for l in subset_file]
        if len(parser_options['subset']) == 0:
            raise AttributeError(_("ERROR: Subset is empty"))
    else:
        parser_options['subset'] = []

    return parser_options, profiler_options

def set_arguments(args):
    """
    Set all the arguments of perprof
    """
    import argparse

    parser = argparse.ArgumentParser(
            description=_('A python module for performance profiling '
            '(as described by Dolan and Moré).'),
            fromfile_prefix_chars='@')

    backend_args = parser.add_argument_group(_("Backend options"))
    backend = backend_args.add_mutually_exclusive_group(required=True)
    backend.add_argument('--mp', action='store_true',
            help=_('Use matplotlib as backend for the plot. Default '
            'output: PNG'))
    backend.add_argument('--tikz', action='store_true',
            help=_('Use LaTex/TikZ/pgfplots as backend for the plot. '
            'Default output: PDF'))
    backend.add_argument('--raw', action='store_true',
            help=_('Print raw data. Default output: standard output'))

    output_format_args = parser.add_argument_group(_("Output formats"))
    output_format = output_format_args.add_mutually_exclusive_group()
    output_format.add_argument('--eps', action='store_true',
            help=_('The output file will be a EPS file'))
    output_format.add_argument('--pdf', action='store_true',
            help=_('The output file will be a PDF file'))
    output_format.add_argument('--png', action='store_true',
            help=_('The output file will be a PNG file'))
    output_format.add_argument('--ps', action='store_true',
            help=_('The output file will be a PS file'))
    output_format.add_argument('--svg', action='store_true',
            help=_('The output file will be a SVG file'))
    output_format.add_argument('--tex', action='store_true',
            help=_('The output file will be a (La)TeX file'))

    tikz_options = parser.add_argument_group(_("TikZ options"))
    tikz_options.add_argument('--standalone', action='store_true',
            help=_('Create the header as a standalone to the tex file, '
                    'enabling compilation of the result'))
    tikz_options.add_argument('--pgfplotcompat', type=float, default=None,
            help=_('Set pgfplots backwards compatibility mode to given version'))

    parser.add_argument('--lang', '-l', choices=['en', 'pt_BR'], default='en',
            help=_('Set language for axis label'))
    parser.add_argument('--free-format', action='store_true',
            help=_('When parsing file handle all non `c` character as `d`'))
    parser.add_argument('--pdf-verbose', action='store_true',
            help=_('Print output of pdflatex'))
    parser.add_argument('--black-and-white', action='store_true',
            help=_('Use only black color.'))
    parser.add_argument('--background',
            help=_('RGB values separated by commas for the background color '
                    'of the plot. (Values in the 0,255 range)'))
    parser.add_argument('--page-background',
            help=_('RGB values separated by commas for the background color '
                    'of the page. (Values in the 0,255 range)'))
    parser.add_argument('--semilog', action='store_true',
            help=_('Use logarithmic scale for the x axis of the plot'))
    parser.add_argument('--success', type=str, default='c',
            help=_('Flags that are interpreted as success, '
                    'separated by commas.  Default: `c`'))
    parser.add_argument('--maxtime', type=float, default=float('inf'),
            help=_('Sets a maximum time for a solved problem. Any problem with a '
                    'time greater than this will be considered failed.'))
    parser.add_argument('--mintime', type=float, default=0,
            help=_('Sets a minimum time for a solved problem. Any problem with a '
                    'time smaller than this will have the time set to this.'))
    parser.add_argument('--use-objective-function', action='store_true',
            help=_('Use objective function value on comparison'))
    parser.add_argument('--use-primal-infeasibility', action='store_true',
            help=_('Use primal infeasibility value to determine convergence'))
    parser.add_argument('--use-dual-infeasibility', action='store_true',
            help=_('Use dual infeasibility value to determine convergence'))
    parser.add_argument('--infeasibility-tolerance', type=float, default=1e-4,
            help=_('Tolerance for the primal and dual infeasibilities'))

    parser.add_argument('-c', '--cache', action='store_true',
            help=_('Enable cache.'))
    parser.add_argument('-s', '--subset',
            help=_('Name of a file with a subset of problems to compare'))
    parser.add_argument('--tau', type=float,
            help=_('Limit the x-axis based this value'))
    parser.add_argument('-f', '--force', action='store_true',
            help=_('Force overwrite the output file'))
    parser.add_argument('-o', '--output',
            help=_('Name of the file to use as output '
                    '(the correct extension will be add)'))

    parser.add_argument('--demo', action='store_true',
            help=_('Use examples files as input'))
    parser.add_argument('file_name', nargs='*',
            help=_('The name of the files to be used for '
                    'the performance profiling (for demo use `--demo`)'))

    parsed_args = parser.parse_args(args)

    # Set input files for demo
    if parsed_args.demo:
        if parsed_args.file_name:
            warnings.warn(_("Using demo mode. Ignoring input files."),
                    UserWarning)
        parsed_args.file_name = [
                os.path.join(THIS_DIR, 'examples/alpha.table'),
                os.path.join(THIS_DIR, 'examples/beta.table'),
                os.path.join(THIS_DIR, 'examples/gamma.table')]
    elif len(parsed_args.file_name) <= 1:
        raise ValueError(_("You must provide at least two input files."))

    return parsed_args

def main():
    """This is the entry point when calling perprof."""

    try:
        args = set_arguments(sys.argv[1:])

        parser_options, profiler_options = process_arguments(args)

        if args.mp:
            # matplotlib
            from . import matplotlib

            data = matplotlib.Profiler(parser_options, profiler_options)
            data.plot()
        elif args.tikz:
            if profiler_options['output_format'] == 'pdf' and args.output is None:
                print(_("ERROR: When using PDF output, you need to provide "
                        "the name of the output file."))
            else:
                # tikz
                from . import tikz

                data = tikz.Profiler(parser_options, profiler_options)
                data.plot()
        elif args.raw:
            # raw
            from . import prof
            print('raw')

            print(prof.Pdata(parser_options, profiler_options))
    except ValueError as error:
        print(error)
    except NotImplementedError as error:
        print(error)
