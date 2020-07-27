import argparse
from exporters.to_svg import ToSvg
from exporters.to_excel import ToExcel
from core import Layer

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export an Att&ck layer as a svg image')
    parser.add_argument('-m', '--mode', choices=['svg', 'excel'], required=True, help='The form to export the layers in')
    parser.add_argument('input', nargs='+', help='Path(s) to the file to export')
    parser.add_argument('-s','--source', choices=['taxii', 'local'], default='taxii', help='What source to utilize when building the matrix')
    parser.add_argument('--local', help='Path to the local resource if --source=local', default=None)
    parser.add_argument('-o','--output', nargs='+', help='Path(s) to the exported svg file', required=True)
    args = parser.parse_args()
    print(args)
    if len(args.output) != len(args.input):
        print('Mismatched number of output filepaths to input file paths. Exiting...')

    for entry in args.input:
        print('{}/{} - Beginning processing {}'.format(args.input.index(entry) + 1, len(args.input), entry))
        lay = Layer()
        try:
            lay.from_file(entry)
        except:
            print('Unable to load {}. Skipping...'.format(entry))
            continue
        if args.mode=='excel':
            exy = ToExcel(domain=lay.layer.domain, source=args.source, local=args.local)
            exy.to_xlsx(lay, filepath=args.output[args.input.index(entry)])
        else:
            svy = ToSvg(domain=lay.layer.domain, source=args.source, local=args.local)
            svy.to_svg(lay, filepath=args.output[args.input.index(entry)])
        print('{}/{} - Finished processing {}'.format(args.input.index(entry) + 1, len(args.input), entry))


else:
    print('This script is intended as a commandline wrapper for exporting scripts in the library. '
          'It will only work if run as the main script.')