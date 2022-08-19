#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 Ryan Mackenzie White <ryan.white@nrc-cnrc.gc.ca>
#
# Distributed under terms of the Copyright © 2022 National Research Council Canada. license.

"""

"""
from setuptools import setup, find_packages

def main():
    setup(
        name="m_layer_register",
        packages=find_packages(exclude=["tests","docs","tests.*","docs.*"]),
        install_requires=[]
    )

if __name__ == "__main__":
    main()



    
