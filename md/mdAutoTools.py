# Copyright (c) 2010, Lawrence Livermore National Security, LLC
# Produced at Lawrence Livermore National Laboratory
# LLNL-CODE-462894
# All rights reserved.
#
# This file is part of MixDown. Please read the COPYRIGHT file
# for Our Notice and the LICENSE file for the GNU Lesser General Public
# License.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License (as published by
# the Free Software Foundation) version 3 dated June 2007.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
#  You should have recieved a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os, re
import mdMake, mdDefines, mdTarget, utilityFunctions

from md import  mdMake, mdDefines, mdTarget, utilityFunctions
from mdLogger import *

def isAutoToolsProject(path):
    if os.path.exists(os.path.join(path, "configure")) or\
       os.path.exists(os.path.join(path, "configure.ac")) or\
       os.path.exists(os.path.join(path, "configure.in")):
        return True
    return False

def getInstallDir(command):
    prefix = ""
    regex = re.compile(r"[\.\/]?configure.*--prefix=([A-Za-z0-9\/\.]+)")
    match = regex.search(command)
    if match != None:
        prefix = match.group(1)
    return prefix

def generateConfigureFiles(path, name, verbose=True):
    command = getPreconfigureCommand(path)
    if command != "":
        if verbose:
            Logger().writeMessage("Generating build files...", name)
        returnCode = utilityFunctions.executeSubProcess(command, path)
        if returnCode != 0:
            return False
    return True

def getDependancies(path, name="", verbose=True):
    deps = []
    if not os.path.isdir(path) or not os.path.exists(os.path.join(path, "configure")):
        return None

    if verbose:
        Logger().writeMessage("Analyzing 'configure --help' output", name)
    helpFileName = os.path.join(path, "configure_help.log")
    helpFile = open(helpFileName, "w")
    try:
        returnCode = utilityFunctions.executeSubProcess("./configure --help", path, helpFile.fileno())
    finally:
        helpFile.close()
    if returnCode != 0:
        return None

    try:
        helpFile = open(helpFileName, "r")
        regexp = re.compile(r"--with-([a-zA-Z\-_]+)=(?:PREFIX|PATH|DIR)")
        for line in helpFile:
            match = regexp.search(line)
            if match != None:
                foundDep = match.group(1)
                foundDep = mdTarget.normalizeName(foundDep)
                if not foundDep in deps:
                    deps.append(foundDep)
    finally:
        helpFile.close()

    return deps

# Commands
def getPreconfigureCommand(path):
    if os.path.exists(os.path.join(path, "configure.ac")) or os.path.exists(os.path.join(path, "configure.in")):
        return "autoreconf -i"
    else:
        return ""

def getConfigureCommand(target):
    command = "./configure " + mdDefines.surround(mdDefines.mdAutoToolsPrefix[0]) + " " + mdDefines.surround(mdDefines.mdAutoToolsCompilers[0])
    for dependancy in target.dependsOn:
        command += " --with-" + dependancy + "=" + mdDefines.surround(mdDefines.mdPrefix[0])
    return command

def getBuildCommand():
    return mdMake.getBuildCommand()

def getInstallCommand():
    return mdMake.getInstallCommand()

def getCleanCommand():
    return mdMake.getCleanCommand()
