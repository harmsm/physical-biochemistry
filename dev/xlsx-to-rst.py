#!/usr/bin/env python3
__description__ = \
"""
Convert a class schedule, in xlsx format, into .rst format for display on a
web page.

Assumes xlsx file has "schedule" tab with following columns:
    ("Week","Date","Topic","Due","Reading","Material")

Optionally looks for "links" tab with columns:
    ("link_name","link_url")
These columns map between aliases for links in the schedule and actual link
urls.
"""
__author__ = "Michael J. Harms"
__date__ = "2019-10-02"
__usage__ = "./xlsx_to_rst.py schedule.xlsx"

import numpy as np
import pandas as pd
from xlrd import XLRDError

import sys

def _update_link_dict(new_key,new_value,current_dict):
    """
    Update a link dictionary, checking for alias collisions.
    """

    try:
        current_dict[new_key]
        err = "link key {} is not unique.\n".format(items[j])
        raise ValueError(err)
    except:
        current_dict[new_key] = new_value

    return current_dict


def xlsx_to_rst(schedule_file,
                base_url="https://github.com/harmsm/physical-biochemistry/blob/master/",
                col_to_keep=("Week","Date","Topic","Due","Reading","Material")):

    # Read schedule and drop unnecessary columns
    df = pd.read_excel(schedule_file,sheet_name="schedule")
    df = df.filter(items=col_to_keep,axis=1)

    # Read dictionary of links.  If none specified, will be empty dict
    try:
        link_df = pd.read_excel(schedule_file,sheet_name="links")
        link_dict = dict(zip(link_df["link_name"],link_df["link_url"]))
    except XLRDError:
        link_dict = {}

    # Fix NaN -> ""
    for c in df:
        for i, r in enumerate(df[c]):
            try:
                if np.isnan(r):
                    df.loc[i,c] = ""
            except TypeError:
                pass

    # -------------------------------------------------------------------------
    # Split and add links
    # -------------------------------------------------------------------------

    # Process "Due" column, looking for items that start with HW
    hw_links = {}
    for i, r in enumerate(df["Due"]):
        items = [item.strip() for item in r.split(",")]
        for j in range(len(items)):
            if items[j].startswith("HW"):
                try:
                    link_target = link_dict[items[j]]
                except KeyError:
                    link_target = "MISSING_LINK"
                items[j] = "{}_".format(items[j])
                hw_links = _update_link_dict(items[j],link_target,hw_links)
        if len(items) == 1 and items[0] == "":
            items = ["---"]

        df.loc[i,"Due"] = ", ".join(items)

    # Process "Reading" column, looking for items that start with MoL and
    # SSTB.  These are treated specially (read, hacked).  Other items are
    # assumed to be links.
    reading_links = {}
    for i, r in enumerate(df["Reading"]):
        items = [item.strip() for item in r.split(",")]

        if len(items) == 1 and items[0] == "":
            items = ["---"]

        else:
            for j in range(len(items)):
                if not items[j].startswith("MoL"):

                    if items[j].startswith("SSTB"):
                        link_target = "readings/sstb.pdf"

                    elif items[j] == "":
                        continue

                    else:
                        try:
                            link_target = link_dict[items[j]]
                        except KeyError:
                            link_target = "MISSING_LINK"

                    # Clean up and make look like a link
                    items[j] = "`{}`_".format(items[j])

                    reading_links = _update_link_dict(items[j],link_target,reading_links)

        df.loc[i,"Reading"] = ", ".join(items)

    # Process "Material" column. Items are assumed to be links.
    material_links = {}
    for i, r in enumerate(df["Material"]):
        items = [item.strip() for item in r.split(",")]

        if len(items) == 1 and items[0] == "":
            items = ["---"]

        else:

            for j in range(len(items)):

                try:
                    link_target = link_dict[items[j]]
                except KeyError:
                    link_target = "MISSING_LINK"

                # Clean up and make look like a link
                items[j] = "`{}`_".format(items[j])

                material_links = _update_link_dict(items[j],link_target,material_links)

        df.loc[i,"Material"] = ", ".join(items)

    # Proess "Topic" column.  Items are assumed to be links.
    lab_links = {}
    for i, r in enumerate(df["Topic"]):
        if r.startswith("Lab"):

            link_alias = "`{}`_".format(r.strip())

            try:
                link_target = link_dict[r.strip()]
            except KeyError:
                link_target = "MISSING_LINK"

            lab_links = _update_link_dict(link_alias,link_target,lab_links)

            df.loc[i,"Topic"] = link_alias


    # Find length of columns for construction of rst.
    col_length = {}
    for c in df:

        tmp = [len(c)]
        for i, r in enumerate(df[c]):

            tmp.append(len("{}".format(r).strip()))

        col_length[c] = max(tmp)

    # -------------------------------------------------------------------------
    # Build RST
    # -------------------------------------------------------------------------

    # Construct elements of correct length to build table
    header_strings = []
    row_strings = []
    fmt_strings = []
    for c in df:
        header_strings.append("+=" + (col_length[c] + 1)*"=")
        row_strings.append("+-" + (col_length[c] + 1)*"-")
        fmt_strings.append("| {{:{:}}} ".format(col_length[c]))
    header_strings.append("+")
    row_strings.append("+")

    # Row and header lines
    row = "-".join(row_strings)
    header = "=".join(header_strings)

    # Start with a row
    out = [row]

    # Create names of columns
    tmp_out = []
    for i, c in enumerate(df):
        tmp_out.append(fmt_strings[i].format(c))
    tmp_out.append("|")
    out.append(" ".join(tmp_out))

    # Add header break
    out.append(header)

    # Build rst row for every row in the dataframe
    for r in df.iterrows():
        tmp_out = []
        for i, c in enumerate(df):
            tmp_out.append(fmt_strings[i].format(r[1][c]))
        tmp_out.append("|")
        out.append(" ".join(tmp_out))
        out.append(row)

    # Construct links below the table (to keep the table human-readable)
    out.append("")
    if base_url[-1] == "/":
        base_url = base_url[:-1]

    # Deal with reading links
    out.append(".. reading links")
    for k in reading_links:
        alias = k[:-1]
        link = reading_links[k]
        if link[0:4] not in ["http","ftp:"]:
            link = "{}/{}".format(base_url,link)
        out.append(".. _{}: {}".format(alias,link))
    out.append("")

    # Deal with material links
    out.append(".. material links")
    for k in material_links:
        alias = k[:-1]
        link = material_links[k]
        if link[0:4] not in ["http","ftp:"]:
            link = "{}/{}".format(base_url,link)
        out.append(".. _{}: {}".format(alias,link))
    out.append("")

    # Deal with lab links
    out.append(".. lab links")
    for k in lab_links:
        alias = k[:-1]
        link = lab_links[k]
        if link[0:4] not in ["http","ftp:"]:
            link = "{}/{}".format(base_url,link)
        out.append(".. _{}: {}".format(alias,link))
    out.append("")

    # Deal with homework links
    out.append(".. homework links")
    for k in hw_links:
        alias = k[:-1]
        link = hw_links[k]
        if link[0:4] not in ["http","ftp:"]:
            link = "{}/{}".format(base_url,link)
        out.append(".. _{}: {}".format(alias,link))
    out.append("")

    return out


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    try:
        schedule_file = argv[0]
    except IndexError:
        err = "Incorrect arguments. Usage:\n\n{}\n\n".format(__usage__)
        raise ValueError(err)

    out = xlsx_to_rst(schedule_file)

    print("\n".join(out))

if __name__ == "__main__":
    main()
