import argparse


def main(opt):
    if opt.is_inference_mode:
        pass
    else:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Network Protocol Fuzzer')
    parser.add_argument('target', metavar='network_protocol',
                        help='Fuzz testing on network protocol')
    parser.add_argument('--inference', dest='is_inference_mode', action='store_true',
                        default=False, help='Infer network protocol')
    exit(main(parser.parse_args()))