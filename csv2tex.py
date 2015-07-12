#!/usr/bin/env python3
import configparser as cp
from sys import argv,exit
from numpy import genfromtxt
from math import log,floor
from getopt import gnu_getopt

################################################################################
#                                                                              #
#    csv2tex.py                                                                #
#    Copyright (C) 2015  Lucas Luigi Treffenstädt (lucas@treffenstaedt.de)     #
#                                                                              #
#    This program is free software; you can redistribute it and/or modify      #
#    it under the terms of the GNU General Public License as published by      #
#    the Free Software Foundation; either version 2 of the License, or         #
#    (at your option) any later version.                                       #
#                                                                              #
#    This program is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU General Public License for more details.                              #
#                                                                              #
#    You should have received a copy of the GNU General Public License along   #
#    with this program; if not, write to the Free Software Foundation, Inc.,   #
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.               #
#                                                                              #
################################################################################

def getColumn(config, section):
    if("column" in config.options(section)):
        return int(config.get(section,"column"))-1
    else:
        print("Error: no column defined for "+section)
        exit(1)

def getError(config, section):
    if("error" in config.options(section)):
        return int(config.get(section,"error"))-1
    else:
        return None

def getAlignment(config, section):
    if("alignment" in config.options(section)):
        return config.get(section,"alignment")
    else:
        return "c"

def getTitle(config, section):
    if("title" in config.options(section)):
        return config.get(section,"title")
    else:
        return section

def getPrecision(config, section):
    if("precision" in config.options(section)):
        return int(config.get(section,"precision"))
    else:
        return None

def getScale(config, section):
    if("scale" in config.options(section)):
        return float(config.get(section,"scale"))
    else:
        return 1

def getErrorScale(config, section,scale):
    if("error_scale" in config.options(section)):
        return float(config.get(section,"error_scale"))
    else:
        return scale

###########################################################

options,arguments=gnu_getopt(argv[1:],"i:c:o:h",["in=","out=","conf=","help"])
options=dict(options)
if("--help" in options or "-h" in options):
    print("Usage: csv2tex [OPTIONS]\n  -i file, --in=file\n    read data from file\n    default: in.dat\n\n  -o file, --out=file\n    write table to file\n    default: out.tex\n\n  -c file, --conf=file\n    read configuration from file\n    default: csv2tex.conf")
    exit(0)
if("--in" in options):
    infile=options["--in"]
elif("-i" in options.keys()):
    infile=options["-i"]
else:
    infile="in.dat"
if("--out" in options):
    outfile=options["--out"]
elif("-o" in options.keys()):
    outfile=options["-o"]
else:
    outfile="out.tex"
if("--conf" in options):
    conffile=options["--conf"]
elif("-c" in options.keys()):
    conffile=options["-c"]
else:
    conffile="csv2tex.conf"
if(arguments!=[]):
    print("Unrecognized Options: "+str(arguments))
    print("Usage: csv2tex [OPTIONS]\n  -i file, --in=file\n    read data from file\n    default: in.dat\n\n  -o file, --out=file\n    write table to file\n    default: out.tex\n\n  -c file, --conf=file\n    read configuration from file\n    default: csv2tex.conf")
    exit(1)

print("reading configuration file "+conffile)
config=cp.ConfigParser(interpolation=None)
cfg=config.read(conffile)
if(cfg==[]):
    print("    Error: Configuration file not found")
    exit(1)

print("reading data file "+infile)
try:
    data = genfromtxt(infile)
except OSError:
    print("    Error: data file not found or unreadable")
    exit(1)

formatierung={}
daten={}
fehler={}
precision={}
align=""
header=""
for section in config.sections():
    column=getColumn(config,section)
    error=getError(config,section)
    scale=getScale(config,section)
    error_scale=getErrorScale(config,section,scale)
    title=getTitle(config,section)
    alignment=getAlignment(config,section)
    precision[section]=getPrecision(config,section)
    align+=alignment
    if(header==""):
        header+=title
    else:
        header+="&"+title

    formatierung[section]="${x:1.{precision:1.0f}f}"
    daten[section]=data[:,column]*scale
    if(error != None):
        formatierung[section]+=" \pm {s:1.{precision_s:1.0f}f}$"
        fehler[section]=data[:,error]*error_scale
    else:
        formatierung[section]+="$"

print("writing to output file "+outfile)
try:
    with open(outfile, "w") as output:
        output.write("\\begin{{tabular}}{{{align:s}}}\n".format(align=align))
        output.write("\\toprule\n")
        output.write(header+"\\\\\n")
        output.write("\\midrule\n")
        for line in range(len(next(iter(daten.values())))):
            zeile=""
            for section in config.sections():
                if(zeile!=""):
                    zeile+="&"
                form=formatierung[section]
                x=daten[section][line]
                if section in fehler:
                    s=fehler[section][line]
                    if(precision[section]==None):
                        prec=-floor(log(s)/log(10))
                    else:
                        prec=precision[section]
                    s=round(s,prec)
                    x=round(x,prec)
                    zeile+=form.format(precision=max(prec,0),x=x,precision_s=max(prec,0),s=s)
                else:
                    if(precision[section]==None):
                        prec=0
                    else:
                        prec=precision[section]
                    zeile+=form.format(precision=prec,x=x)
            zeile+="\\\\\n"
            output.write(zeile)
        output.write("\\bottomrule\n")
        output.write("\\end{tabular}\n")
except Exception:
    print("  writing failed")
    exit(1)
print("    done")
