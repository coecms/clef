# row for this tbale looks like:
# dataset_id, name, 
from clef.update_collections import *
import click
import json

def dset_args(f):
    args = [
        click.option('--dataset', '-d', 'dname',  multiple=False, help="Dataset name as defined in clef.db Dataset table"),
        click.option('--version', '-v', multiple=False, help="Dataset version as defined in clef.db Dataset table"),
        click.option('--format', '-f', 'fformat', multiple=False, type=click.Choice(['netcdf','grib','HDF5','binary']),
                      help="Dataset file fomrmat as defined in clef.db Dataset table"),
        click.option('--input_file', '--ifile', '-i', multiple=False, help="Input json file containing the rest of variables information"),
    ]
    for c in reversed(args):
        f = c(f)
    return f

def read_json(ifile):
    ''' Read variable information from a text file and returns a list of dictionaries.
        Each dictionary represents a row to be added to the Variable table
    :input: ifile input json file with keys: grid, resolution, fdate, tdate,levels, frequency, varlist
                  varlist is a list of dictionaries one for variable with keys: name, standard_name,
                  units, cmor_name, long_name
    :return: rows list of dictionaries
    ''' 
    # create empty rows list
    rows=[]
    # open json file and read data as dictionary
    with open(ifile) as f:
        lines = f.readlines()
    for l in lines:
        r={}
        r['cmor_name'],r['stream'],r['realm'] = l[:-1].split(',')
        rows.append(r)
    return rows 

def blip():

    # open table
    #rows = read_json(ifile)
    dname='ERAI'
    fformat='netcdf'
    version='1.0'
    ifile='up_erai_var.txt'
    rows = read_json(ifile) 
    identifiers=['cmor_name']
    
    # bulk add to table
    update_variable_table(rows,identifiers,dname,fformat,version)

if __name__ == "__main__":
    blip()
