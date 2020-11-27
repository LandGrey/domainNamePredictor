#!/usr/bin/env python3
# coding: utf-8
# A simple modernized enterprise domain name predictor and generator
#
# Build By LandGrey
#

import os
import sys
import time
import argparse
import itertools
from tld import get_tld
try:
    import ConfigParser
except ImportError as e:
    import configparser as ConfigParser


def guess_main_domain(name):
    tld = get_tld(name, fix_protocol=True)
    top_domain = name[:-len(tld) - 1].split(".")[-1] + "." + tld
    return top_domain


def unique(seq, idfun=None):
    if idfun is None:
        def idfun(x): return x
    seen = {}
    results = []
    for item in seq:
        marker = idfun(item)
        if marker in seen:
            continue
        seen[marker] = 1
        results.append(item)
    return results


def awesome_factory(join_string, elements, mix_join=None):
    element_number = 3 if len(elements) >= 3 else 2
    for length in range(2, element_number + 1):
        for x in itertools.combinations(elements, length):
            for y in itertools.product(*x):
                for z in itertools.permutations(y):
                    yield join_string.join(z)
                    if mix_join and len(z) >= 3:
                        yield join_string.join(z[:-1]) + mix_join + z[-1]
                        yield z[0] + mix_join + join_string.join(z[1:])


def read_all_domain_names(content):
    init_domain_names = []

    if os.path.isfile(content):
        with open(content, 'r') as f:
            for name in f.readlines():
                name = name.strip()
                if name:
                    init_domain_names.append(name)

    return init_domain_names


def get_configuration(mode):
    config_dict = {
        'environment': [],
        'version': [],
        'role': [],
        'technology': [],
        'service': [],
        'monitor': [],
        'time': [],
        'space': [],
        'area': [],
        'proxy': [],
        'number': [],
        'application': []
    }
    regular_path = os.path.join(current_dir, "rules", "regular.cfg")

    if mode:
        cfg_path = os.path.join(current_dir, "rules", "predictor-{}.cfg".format(mode))
    else:
        cfg_path = os.path.join(current_dir, "rules", "predictor-default.cfg")

    for cfg in [regular_path, cfg_path]:
        try:
            config = ConfigParser.ConfigParser(allow_no_value=True)
            config.optionxform = str
            config.read(cfg)
            for s in config.sections():
                for o in config.options(s):
                    config_dict[s].append(o)
        except Exception as e:
            exit("[-] parse config file: {} error".format(cfg))
    return config_dict


def name_filter(name, original_domain, domain_prefix):
    js_chunk = []
    if "-" in name:
        for v1 in name.split("."):
            for v2 in v1.split("-"):
                js_chunk.append(v2)
    else:
        js_chunk = name.split(".")

    name_length = len(name)
    js_chunk_length = len(js_chunk)

    if js_chunk_length >= 3:
        # drop      aa.bb.cc/aa-bb-cc/aa-bb.cc/aa.bb-cc     too short name
        if name_length <= (js_chunk_length * 2 + js_chunk_length - 1):
            return None
        # drop      aaaaaa-bbbbbb-cccccc        too long name
        if name.count("-") >= js_chunk_length - 1 and name_length >= (js_chunk_length * 6 + js_chunk_length - 1):
            return None
        # drop      aaaaaaaa./-bbbbbbbb./-cccccccc  too long name
        if name_length >= (js_chunk_length * 8 + js_chunk_length - 1):
            return None

    if domain_prefix:
        if domain_prefix in js_chunk:
            if len(js_chunk) <= 3:
                return name + "." + original_domain[len(domain_prefix) + 1:]
        else:
            return name + "." + original_domain
    else:
        return name + "." + original_domain
    return None


def get_main_domain_similar_domain_names(main_domain_name, config):
    results = []

    environment = config['environment']
    role = config['role']
    technology = config['technology']
    service = config['service']
    proxy = config['proxy']
    version = config['version']
    monitor = config['monitor']
    time = config['time']
    space = config['space']
    area = config['area']
    application = config['application']

    small_lists = [environment, role, technology, service, monitor, proxy]
    all_lists = small_lists[:]
    for ex in [version, time, space, area, application]:
        all_lists.append(ex)

    for one_lists in all_lists:
        for item in one_lists:
            results.append(item + "." + main_domain_name)

    for js in [".", "-"]:
        for name in awesome_factory(js, small_lists):
            nf = name_filter(name, main_domain_name, None)
            if nf:
                results.append(nf)

    for name in awesome_factory("-", small_lists, mix_join="."):
        nf = name_filter(name, main_domain_name, None)
        if nf:
            results.append(nf)

    return results


def get_normal_domain_similar_domain_names(domain_name, config):
    results = []

    environment = config['environment']
    role = config['role']
    technology = config['technology']
    service = config['service']
    monitor = config['monitor']
    proxy = config['proxy']

    prefix = domain_name.split(".")[0]
    small_lists = [[prefix], environment, role, technology, service, monitor, proxy]

    for js in [".", "-"]:
        for name in awesome_factory(js, small_lists):
            nf = name_filter(name, domain_name, prefix)
            if nf:
                results.append(nf)

    for name in awesome_factory("-", small_lists, mix_join="."):
        nf = name_filter(name, domain_name, prefix)
        if nf:
            results.append(nf)

    return results


def get_single_similar_domain_names(original_domain, predictor_mode):
    config = get_configuration(mode=predictor_mode)
    main_domain = guess_main_domain(original_domain)
    is_main_domain = True if original_domain == main_domain else False
    if is_main_domain:
        return get_main_domain_similar_domain_names(main_domain, config)
    else:
        return get_normal_domain_similar_domain_names(original_domain, config)


def printer(_predictor_mode, _output_path, _begin_time, _count):
    print("[+] current mode: [{0}]\n" 
          "[+] A total of  : {1:} lines\n"
          "[+] Store in    : {2} \n"
          "[+] Cost        : {3} seconds".format(_predictor_mode, _count, _output_path, str(time.time() - _begin_time)[:6]))


if __name__ == "__main__":
    begin_time = time.time()
    ascii_banner = r'''
                _   _
               (.)_(.)
            _ (   _   ) _
           / \/`-----'\/ \
         __\ ( (     ) ) /__
         )   /\ \._./ /\   (
          )_/ /|\   /|\ \_(     
                                    dnp.py
'''

    try:
        current_dir = os.path.dirname(os.path.join(os.path.abspath(sys.argv[0]))).encode('utf-8').decode()
    except UnicodeError:
        try:
            current_dir = os.path.dirname(os.path.abspath(sys.argv[0])).decode('utf-8')
        except UnicodeError:
            current_dir = "."
            exit('[*] Please move dnp.py script to full ascii path, than apply it')
    output_path = os.path.join(current_dir, 'results')
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    print(ascii_banner)
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='domain_name', default='', help='single domain name')
    parser.add_argument('-f', dest='file_path', default='', help='domain names file path')
    parser.add_argument('-m', dest='predictor_mode', default='default', choices=['default', 'simple'], help='choose predictor mode: [default, simple]')
    parser.add_argument('-o', '--output', dest='output', default='', help='result output path')
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    args = parser.parse_args()

    input_name = args.domain_name
    input_file = args.file_path
    predictor_mode = args.predictor_mode
    output_path = args.output \
        if args.output else os.path.join(output_path, (input_name if input_name else str(begin_time)[4:10]) + "-" + predictor_mode + ".txt")

    count = 0
    with open(output_path, 'w') as f:
        if input_name:
            for x in unique(get_single_similar_domain_names(input_name, predictor_mode)):
                count += 1
                f.write(x + "\n")
        else:
            join_results = []
            for ns in read_all_domain_names(input_file):
                join_results.extend(get_single_similar_domain_names(ns, predictor_mode))
            for x in unique(join_results):
                count += 1
                f.write(x + "\n")

    printer(predictor_mode, output_path, begin_time, count)
