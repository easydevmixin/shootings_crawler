        except Exception as ex:
            print("Error checking robots.txt file: {}".format(ex))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--warranty", help="Check out the warranty.", action="store_true")
    parser.add_argument("-c", "--conditions", help="Check out the conditions summary.",
                        action="store_true")

    args = parser.parse_args()

    if args.warranty:
        license.show_warranty()
    elif args.conditions:
        license.show_contitions()
    else:
        try:
#!/usr/bin/env python

# -*- coding: utf-8 -*-

import argparse

import license


