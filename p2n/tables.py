# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import logging
from p2n.util import filterdict, dictproduct

logger = logging.getLogger(__name__)


def pivottables_data_brevets(document_list):
    """
    Compute data suitable for feeding to PivotTable.js from Patent2NetBrevet data model.

    Obtains a list of document dictionaries in the legacy Patent2Net brevet format,
    filters each dictionary by designated keys and normalizes/flattens the dictionaries
    by expanding all entries containing multivalued attributes to all combinations
    (cartesian product).

    This is because PivotTable.js assumes all attributes to be scalar values
    (i.e. strings or numbers) and not objects, see also:
    https://github.com/nicolaskruchten/pivottable/wiki/Input-Formats
    """

    fields = [
        'label', 'country', 'kind', 'year',
        #'priority-active-indicator',
        #'prior-Date',
        'applicant', 'inventor', 'representative',
        'IPCR4', 'IPCR7',
        "Inventor-Country", "Applicant-Country",
        # "CPC", "equivalents", excluded due to exploding amount of entries after multivalue expansion
    ]

    expanded_list = []
    for document in document_list:

        # Use only designated fields, skip others
        document = filterdict(document, fields)

        # Compute cartesian product
        expanded = dictproduct(document)

        # Add list of expanded products
        expanded_list += expanded

    return expanded_list
