#!/usr/bin/env python

import argparse
import logging
import json
from   pprint import pprint
import sys

class BareosConfigurationSchema:
    def __init__( self, json ):
        self.json = json

    def getResources(self):
        return sorted(filter( None, self.json.keys()) )

    def getResource(self, resourcename):
        return self.json[resourcename]

    def getResourceDirectives(self, resourcename):
        return sorted(filter( None, self.getResource(resourcename).keys()) )

    def getResourceDirective(self, resourcename, directive, deprecated=None):
        # TODO:
        # deprecated:
        #   None:  include deprecated
        #   False: exclude deprecated
        #   True:  only deprecated
        return self.json[resourcename][directive]


class BareosConfigurationSchema2Latex:
    def __init__( self, json ):
        self.json = json
        self.schema = BareosConfigurationSchema( json )

    def open(self, filename = None, mode = 'r'):
        if filename:
            self.out=open( filename, mode )
        else:
            self.out=sys.stdout

    def close(self):
        if self.out != sys.stdout:
            self.out.close()

    def getResources(self):
        result = "\\begin{itemize}\n"
        for i in self.schema.getResources():
            if i:
                result += "  \\item " + i + "\n"
        result += "\\end{itemize}\n"
        return result

    def getResourceDirectivesTable(self, resourcename):
        result="\\begin{center}\n"
        result+="\\begin{tabular}{l | l | l | l}\n"
        result+=" name & type of data & required & default value \\\\ \n"
        result+="\\hline \n"
        for directive in self.schema.getResourceDirectives(resourcename):
            data=self.schema.getResourceDirective(resourcename, directive)

            m="{"
            extra=""

            if data.get( 'equals' ):
                datatype="= \\dt{"+data['datatype']+"}"
            else:
                datatype="\{ \\dt{"+data['datatype']+"} \}"

            deprecated=""
            if data.get( 'deprecated' ):
                extra="deprecated"
                m="\\textit{"
            required=""
            if data.get( 'required' ):
                extra="required"
                m="\\textbf{"
            default=""
            if data.get( 'default_value' ):
                default=data.get( 'default_value' )

            result+=m+directive + "} & " + m + datatype + "} & " + m + default + "} & " + m + extra + "}\\\\ \n"
        result+="\\end{tabular}\n"
        result+="\\end{center}\n"
        result+="\n"
        return result

    def writeResourceDirectivesTable(self, resourcename, filename=None):
        self.open(filename, "w")
        self.out.write( self.getResourceDirectivesTable( resourcename ) )
        self.close()

    def getResourceDirectives(self, resourcename):
        result="\\begin{description}\n\n"
        for directive in self.schema.getResourceDirectives(resourcename):
            data=self.schema.getResourceDirective(resourcename, directive)

            datatype="\\dt{"+data['datatype']+"}"
            deprecated=""
            if data.get( 'deprecated' ):
                deprecated="deprecated"
            required=""
            if data.get( 'required' ):
                required="required"
            default=""
            if data.get( 'default_value' ):
                default=data.get( 'default_value' )

            result+="\\xdirective{dir}{"+directive+"}{"+datatype+"}{"+required+"}{"+default+"}{"+deprecated+"}{%\n"
            result+="}\n\n" 
        result+="\\end{description}\n\n"
        return result

    def writeResourceDirectives(self, resourcename, filename=None):
        self.open(filename, "w")
        self.out.write( self.getResourceDirectives( resourcename ) )
        self.close()

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s %(module)s.%(funcName)s: %(message)s', level=logging.INFO)
    logger = logging.getLogger()

    parser = argparse.ArgumentParser()
    parser.add_argument( '-d', '--debug', action='store_true', help="enable debugging output" )
    parser.add_argument("filename", help="load json file")
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    with open(args.filename) as data_file:
        data = json.load(data_file)
    #pprint(data)

    #print data.keys()

    schema = BareosConfigurationSchema( data )
    latex = BareosConfigurationSchema2Latex( data )
    #print schema.getResources()
    for resource in schema.getResources():
        logger.info( "resource: " + resource )
        latex.writeResourceDirectives(resource, "autogenerated/director-resource-"+resource+"-description.tex")
        latex.writeResourceDirectivesTable(resource, "autogenerated/director-resource-"+resource+"-table.tex")