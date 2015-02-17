#! /usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
import argparse

ZONE = "zone01"
NODE_PREFIX = "node-"
NODE_SUFFIX = "." + ZONE
DEFAULT_NUMBER_OF_WORKERS = 15
DEFAULT_POWER = "172800000000"
DEFAULT_NUMBER_OF_CORES = 1
DEFAULT_BAND_WIDTH = "200Mbps"
DEFAULT_LATENCY = "0.0005"

def node_name(idx):
    return "%s%d%s" % (NODE_PREFIX, idx, NODE_SUFFIX)

def disk_name(idx):
    return "disk-%d" % idx

def main():
    parser = argparse.ArgumentParser(description='generator platform xml for MRSG.')

    parser.add_argument('-w', '--number-of-workers', type=int, default=DEFAULT_NUMBER_OF_WORKERS, help="number of worker nodes")
    parser.add_argument('-p', '--power',                       default=DEFAULT_POWER,             help="power of a core")
    parser.add_argument('-c', '--number-of-cores', type=int,   default=DEFAULT_NUMBER_OF_CORES,   help="number of cores in a node")
    parser.add_argument('-b', '--band-width',                  default=DEFAULT_BAND_WIDTH,        help="band width")
    parser.add_argument('-l', '--latency',                     default=DEFAULT_LATENCY,           help="latency")
    parser.add_argument(      '--without-disk',                action='store_true',               help="Does not generate disks")
    parser.add_argument('--read',                              default='550MBps',                 help="disk read")
    parser.add_argument('--write',                             default='475MBps',                 help="disk write")

    parser.add_argument('prefix', metavar='OUTPUT_PREFIX', help='prefix of output XML files')

    args = parser.parse_args()

    cluster  = "%s.xml" % args.prefix
    deploy   = "%s.deploy.xml" % args.prefix
    contents = "%s.contents.txt" % args.prefix
    nhosts = args.number_of_workers + 1

    with open(cluster, "w") as f:
        platform = etree.Element('platform', {"version": str(3)})
        autonomous_system = etree.SubElement(platform, 'AS', {"id": ZONE, "routing": "Full"})

        if not args.without_disk:
            st = etree.SubElement(autonomous_system, 'storage_type', {
                'id': 'single_HDD', 'model': 'linear_no_lat', 'size': '10240TB', 'content': contents, 'content_type': "txt_unix"})
            etree.SubElement(st, 'model_prop', {'id': 'Bwrite', 'value': args.write})
            etree.SubElement(st, 'model_prop', {'id': 'Bread',  'value': args.read})
            etree.SubElement(st, 'model_prop', {'id': 'Bconnection',  'value': args.read}) # TODO: Specify by an argument.

            for i in range(nhosts):
                etree.SubElement(autonomous_system, 'storage', {'id': 'Disk%d' % i, 'typeId': 'single_HDD', 'attach': node_name(i)})

            for i in range(nhosts):
                etree.SubElement(autonomous_system, 'link', {'id': 'link%d' % i, 'bandwidth': str(args.band_width), 'latency': str(args.latency)})

            for i in range(nhosts):
                h = etree.SubElement(autonomous_system, 'host', {
                    'id': node_name(i),
                    'power': str(args.power), 
                    'core': str(args.number_of_cores)})
                etree.SubElement(h, 'mount', {'storageId': 'Disk%d' % i, 'name': '/tmp'})

            for i in range(nhosts):
                for j in range(i+1, nhosts):
                    r = etree.SubElement(autonomous_system, 'route', {
                        'src': node_name(i),
                        'dst': node_name(j)})
                    etree.SubElement(r, 'link_ctn', { 'id': 'link%d' % i})
                    etree.SubElement(r, 'link_ctn', { 'id': 'link%d' % j})

        else:
            cluster_attr = {
                    "id": "Cluster",
                    "prefix": NODE_PREFIX,
                    "suffix": NODE_SUFFIX,
                    "radical": "0-%d" % args.number_of_workers,
                    "power": args.power,
                    "core": str(args.number_of_cores),
                    "bw": args.band_width,
                    "lat": args.latency
            }

            etree.SubElement(autonomous_system, 'cluster', cluster_attr)

        f.write(etree.tostring(platform, encoding="UTF-8",
            xml_declaration=False,
            pretty_print=True,
            doctype='<!DOCTYPE platform SYSTEM "http://simgrid.gforge.inria.fr/simgrid.dtd">'))

    with open(deploy, "w") as f:

        platform = etree.Element('platform', {"version": str(3)})

        etree.SubElement(platform, 'process', {"host": node_name(0), "function": "master"})
        for i in range(1, nhosts):
            e = etree.SubElement(platform, 'process', {"host": node_name(i), "function": "worker"})

        f.write(etree.tostring(platform, encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
            doctype='<!DOCTYPE platform SYSTEM "http://simgrid.gforge.inria.fr/simgrid.dtd">'))

    if not args.without_disk:
        with open(contents, "w") as f:
            size = 1024 * 1024 * 1024 * 1024 # 1TB
            f.write("/0.txt %d\n" % size)

if __name__ == '__main__':
    main()



