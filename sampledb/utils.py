#!/usr/bin/env python
##############################################################################
#
# xpdacq            by Billinge Group
#                   Simon J. L. Billinge sb2896@columbia.edu
#                   (c) 2016 trustees of Columbia University in the City of
#                        New York.
#                   All rights reserved
#
# File coded by:    Timothy Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
import os
import shutil
import pandas as pd

def composition_analysis(compstring):
    """Pulls out elements and their ratios from the config file.

    compstring   -- chemical composition of the sample, e.g.,
                    "NaCl", "H2SO4", "La0.5 Ca0.5 Mn O3".  Blank
                    characters are ignored, unit counts can be omitted.
                    It is critical to use proper upper-lower case for atom
                    symbols as this is used to delimit them in the formula.

    Returns a list of atom symbols and a corresponding list of their counts.
    """
    import re
    # remove all blanks
    compbare = re.sub('\s', '', compstring)
    # reusable error message
    # make sure there is at least one uppercase character in the compstring
    upcasechars = any(str.isupper(c) for c in compbare)
    if not upcasechars and compbare:
        emsg = 'invalid chemical composition "%s"' % compstring
        raise ValueError(emsg)
    # split at every upper-case letter, possibly followed by a lower case
    # one and charge specification
    namefracs = re.split('([A-Z][a-z]?(?:[1-8]?[+-])?)', compbare)[1:]
    names = namefracs[0::2]
    # use unit count when empty, convert to float otherwise
    getfraction = lambda s: (s == '' and 1.0 or float(s))
    fractions = [getfraction(w) for w in namefracs[1::2]]
    return names, fractions


class ExceltoYaml:
    # maintain regularly, aligned with spreadsheet header
    NAME_FIELD = ['Collaborators', 'Sample Maker', 'Lead Experimenter', ]
    COMMA_SEP_FIELD = ['cif name(if exists)', 'User supplied tags']
    PHASE_FIELD = ['Phase Info [required]']
    SAMPLE_NAME_FIELD = ['Sample Name [required]']
    BKGD_SAMPLE_NAME_FIELD = ['Sample-name of sample background']
    DICT_LIKE_FIELD = ['structural database ID for phases'] # return a dict
    # special key for high-dimensional sample phase mapping
    HIGH_D_MD_MAP_KEYWORD = ['gridscan_mappedin']

    # real fields goes into metadata store
    _NAME_FIELD = list(map(lambda x: x.lower().replace(' ', '_'),
                           NAME_FIELD))
    _COMMA_SEP_FIELD = list(map(lambda x: x.lower().replace(' ', '_'),
                                COMMA_SEP_FIELD))
    _SAMPLE_NAME_FIELD = list(map(lambda x: x.lower().replace(' ', '_'),
                                  SAMPLE_NAME_FIELD))
    _BKGD_SAMPLE_NAME_FIELD = list(map(lambda x: x.lower().replace(' ', '_'),
                                       BKGD_SAMPLE_NAME_FIELD))
    _PHASE_FIELD = list(map(lambda x: x.lower().replace(' ', '_'),
                            PHASE_FIELD))
    _DICT_LIKE_FIELD = list(map(lambda x: x.lower().replace(' ', '_'),
                                DICT_LIKE_FIELD))

    def __init__(self, src_dir):
        self.pd_dict = None
        self.sa_md_list = None
        self.src_dir = src_dir

    def load(self, saf_num):
        xl_f = [f for f in os.listdir(self.src_dir) if
                f in (str(saf_num)+'_sample.xls',
                      str(saf_num)+'_sample.xlsx')]
        if not xl_f:
            raise FileNotFoundError("no spreadsheet exists in {}\n"
                                    "have you put it in with correct "
                                    "naming scheme: '<SAF_num>_sample.xlsx'"
                                    "yet?".format(self.src_dir))

        self.pd_dict = pd.read_excel(os.path.join(self.src_dir,
                                                  xl_f.pop()),
                                     skiprows=[1])

        self.sa_md_list = self._pd_dict_to_dict_list(self.pd_dict.to_dict())

    def parse_sample_md(self):
        """parse a list of sample metadata into desired format"""
        parsed_sa_md_list = []
        for sa_md in self.sa_md_list:
            parsed_sa_md = {}
            for k, v in sa_md.items():
                k = str(k).lower()
                v = str(v)
                k = k.strip().replace(' ', '_')
                v = v.replace('/', '_')  # make sure yaml path correct

                # name fields
                if k in self._NAME_FIELD:
                    try:
                        comma_sep_list = self._comma_separate_parser(v)
                        parsed_name = []
                        for el in comma_sep_list:
                            parsed_name.extend(self._name_parser(el))
                    except ValueError:
                        parsed_name = v
                    parsed_sa_md.setdefault(k, [])
                    parsed_sa_md.get(k).extend(parsed_name)

                # phase fields
                elif k in self._PHASE_FIELD:
                    try:
                        (composition_dict,
                         phase_dict,
                         composition_str) = self._phase_parser(v)
                    except ValueError:
                        composition_dict = v
                        phase_dict = v
                    finally:
                        parsed_sa_md.update({'sample_composition':
                                             composition_dict})
                        parsed_sa_md.update({'sample_phase':
                                             phase_dict})
                        parsed_sa_md.update({'composition_string':
                                             composition_str})

                # comma separated fields
                elif k in self._COMMA_SEP_FIELD:
                    try:
                        comma_sep_list = self._comma_separate_parser(v)
                        # print("successfully parsed comma-sep-field {} -> {}"
                        #      .format(v, comma_sep_list))
                    except ValueError:
                        comma_sep_list = v
                    parsed_sa_md.setdefault(k, [])
                    parsed_sa_md.get(k).extend(comma_sep_list)

                # sample name field
                elif k in self._SAMPLE_NAME_FIELD:
                    _k = 'sample_name' # normalized name
                    parsed_sa_md.update({_k: v.replace(' ','_')})

                # bkgd name field
                elif k in self._BKGD_SAMPLE_NAME_FIELD:
                    _k = 'bkgd_sample_name'
                    parsed_sa_md.update({_k:
                                         v.strip().replace(' ', '_')})

                # dict-like field
                elif k in self._DICT_LIKE_FIELD:
                    parsed_sa_md.update({k: self._dict_like_parser(v)})

                # other fields don't need to be parsed
                else:
                    parsed_sa_md.update({k: v})

            parsed_sa_md_list.append(parsed_sa_md)
        self.parsed_sa_md_list = parsed_sa_md_list

    def create_yaml(self, bt):
        """instantiate xpdacq.beamtime.Sample objects based on parsed md

        it also validate if bkgd_sample_name has already appeared as a
        sample_name. If not, it issues a warning

        Parameters
        ----------
        bt : xpdacq.Beamtime object
            an object carries SAF, PI_last and other information

        Returns
        -------
        None
        """
        sample_name_set = set([d['sample_name'] for d in
                               self.parsed_sa_md_list])
        no_bkgd_sample_name_list = []
        for d in self.parsed_sa_md_list:
            bkgd_name = d.get('bkgd_sample_name')
            sample_name = d.get('sample_name')
            if bkgd_name not in sample_name_set:
                no_bkgd_sample_name_list.append(sample_name)
            Sample(bt, d)
        if no_bkgd_sample_name_list:
            print("INFO: If you want to associate a background sample,"
                  " e.g., empty kapton tube, with samples,\nplace the"
                  " sample-name of the background sample in the"
                  " column {}\nof the sample excel spreadsheet.\n"
                  "The following samples do not have "
                  "background_samples associated with them\n"
                  "(typically background samples won't have "
                  "associated background samples):\n{}\n"
                  .format(self._BKGD_SAMPLE_NAME_FIELD,
                          no_bkgd_sample_name_list))
        print("*** End of import Sample object ***")


    def _pd_dict_to_dict_list(self, pd_dict):
        """ parser of pd generated dict to a list of valid sample dicts

        Parameters
        ----------
        pd_dict : dict
            dict generated from pandas.to_dict method

        Return:
        -------
        sa_md_list : list
            a list of dictionaries. Each element is a sample dictionary
        """

        row_num = len(list(pd_dict.values())[0])
        sa_md_list = []
        for i in range(row_num):
            sa_md = {}
            for key in pd_dict.keys():
                sa_md.update({key: pd_dict[key][i]})
            sa_md_list.append(sa_md)

        return sa_md_list

    def _dict_like_parser(self, input_str):
        """ parser for dictionary output"""
        output_dict = {}
        dict_meta = input_str.split(',')
        for el in dict_meta:
            if len(el.split(':')) == 1:
                key = el.split(':').pop()
                val = 'N/A'  # capture default
            else:
                key, val = el.split(':')
            output_dict.update({key.strip(): val.strip()})

        return output_dict

    def _comma_separate_parser(self, input_str):
        """ parser for comma separated fields

        Parameters
        ----------
        input_str : str
            a string contains a series of units that are separated by
            commas.

        Returns
        -------
        output_list : list
            a list contains comma separated element parsed strings.
        """
        element_list = input_str.split(',')
        output_list = list(map(lambda x: x.strip(), element_list))
        return output_list

    def _name_parser(self, name_str):
        """assume a name string

        Returns
        -------
        name_list : list
            a list of strings in [<first_name>, <last_name>] form
        """
        name_list = name_str.split(' ')
        if len(name_list) > 2:
            name_list = [name_str]
        return name_list  # [first, last]

    def _phase_parser(self, phase_str):
        """parser for field with <chem formula>: <phase_amount>

        Parameters
        ----------
        phase_str : str
            a string contains a series of <chem formula> : <phase_amount>.
            Each phase is separated by a comma.

        Returns
        -------
        composition_dict : dict
            a dictionary contains {element: stoichiometry}.
        phase_dict : dict
            a dictionary contains relative ratio of phases.
        composition_str : str
            a string with the format PDF transfomation software
            takes. default is pdfgetx

        Examples
        --------
        rv = cls._phase_parser('NaCl:1, Si:2')
        rv[0] # {'Na':0.33, 'Cl':0.33, 'Si':0.67}
        rv[1] # {'Nacl':0.33, 'Si':0.67}
        rv[2] # 'Na0.33Cl0.5Si0.5'

        Raises:
        -------
        ValueError
            if ',' is not specified between phases
        """
        phase_dict = {}
        composition_dict = {}
        composition_str = ''

        compound_meta = phase_str.split(',')
        # figure out ratio between phases
        for el in compound_meta:
            el = el.strip()
            # there is no ":" in the string            
            if ':' not in el:
                # take whatever alpha numeric string before symbol
                # to be the chemical element
                symbl = [char for char in el if not char.isalnum()]
                if symbl:
                    # take the first symbol
                    symbl_ind = el.find(symbl[0])
                    com = el[:symbl_ind]
                else:
                    # simply take whole string
                    com = el
                amount = 1.0
            else:
                meta = el.split(':')
                # there is a ":" but nothing follows
                if len(meta[1])==0:
                    com = meta[0]
                    amount = 1.0
                # presumably valid input
                else:
                    com, amount = meta
            # construct phase dict
            # special case: mapping 
            if com in self.HIGH_D_MD_MAP_KEYWORD:
                phase_dict.update({com.strip(): amount.strip()})
                composition_str = 'N/A'
                composition_dict = {}
            # normal case, e.g. {'Ni':0.5, 'NaCl':0.5}
            elif isinstance(amount, str):
                amount = amount.strip()
                amount = amount.replace('%', '')

            # construct the not normalized phase dict
            phase_dict.update({com.strip(): float(amount)})

        # normalize phase ratio for composition dict
        total = sum(phase_dict.values())
        for k, v in phase_dict.items():
            ratio = round(v/total, 2)
            phase_dict[k] = ratio

        # construct composition_dict
        for k, v in phase_dict.items():
            el_list, sto_list = composition_analysis(k.strip())
            for el, sto in zip(el_list, sto_list):
                # element appears in different phases, adds up
                if el in composition_dict:
                    val = composition_dict.get(el)
                    val += sto * ratio
                    composition_dict.update({el: val})
                else:
                    # otherwise, just update it
                    composition_dict.update({el: sto * ratio})

        # finally, construct composition_str
        for k,v in sorted(composition_dict.items()):
            composition_str += str(k)+str(v)

        return composition_dict, phase_dict, composition_str

excel_to_yaml = ExceltoYaml()
