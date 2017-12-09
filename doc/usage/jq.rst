.. _jq:

########
jq usage
########


*****
About
*****
``jq`` is a lightweight and flexible command-line JSON processor.
It works on all popular platforms like Linux, Mac OSX and Windows.

Please visit https://stedolan.github.io/jq/ for more information and download.


*****
Usage
*****
You can use it for pretty-printing output from the ad-hoc mode commands of ``p2n``,
but also for filtering and even reformatting.


Pretty-printing
===============
Just pipe JSON output into "``jq .``"::

    p2n adhoc dump --expression='TA=lentille' --with-family --with-register --format=ops | jq .

and voilà::

    [
      {
        "application_date": "2010-07-29",
        "application_year": "2010",
        "application_number_docdb": "CN2010075569W",
        "application_number_epodoc": "WO2010CN75569",
        "publication_date": "2011-02-10",
        "publication_year": "2011",
        "publication_number_docdb": "WO2011015115A1",
        "publication_number_epodoc": "WO2011015115",
        "country": "WO",
        "kind": "A1",
        "document_number": "WO2011015115A1",
        "family_id": "43543927",
        "title": {
          "fr": "CAPOT DE MODULE DE PUCE DE DEL POLYCRISTALLINE UNIQUE HAUTE PUISSANCE POUR ÉCLAIRAGE DE RUE",
          "en": "LIGHT SHELL OF HIGH POWER SINGLE POLYCRYSTALLINE LED CHIP MODULE OF STREET LAMP"
        },
        "abstract": {
          "en": "A light shell of a high power single polycrystalline LED chip module ...",
          "fr": "L'invention concerne un capot de module de puce de DEL polycristalline unique haute puissance pour éclairage ..."
        },
        "classifications": {
          "IPCR": [
            "F21V3/02",
            "F21V17/00",
            "F21V17/14",
            "F21W131/103"
          ],
          "IPC": [],
          "CPC": [
            "F21V3/00",
            "F21V17/14",
            "F21V17/164",
            "F21W2131/103",
            "F21Y2115/10"
          ]
        },
        "applicants": [
          {
            "country": "CN",
            "name": "YANG JANSEN"
          },
          {
            "country": "CN",
            "name": "CHEN HONG"
          }
        ],
        "inventors": [
          {
            "country": "CN",
            "name": "YANG JANSEN"
          },
          {
            "country": "CN",
            "name": "CHEN HONG"
          }
        ],
        "register": {
          "designated_states": [
            "AL",
            "AT",
            "BE",
            "BG",
            [...]
          ]
        },
      }

    [...]


Filtering
=========
Just display list of ``document_number`` fields::

    p2n adhoc dump --expression='TA=lentille' --with-family --with-register --format=ops | jq '.[] | .document_number'

Output::

    "WO2011015115A1"
    "CN101988689A"
    "CN101988689B"
    "CA2694840A1"
    "AT553722T"
    "CN101808594A"


Reformatting
============
Display list of document numbers featuring register information, along with their designated states::

    p2n adhoc dump --expression='TA=lentille' --with-family --with-register --format=ops | jq '.[] | select(.register) | {number: .document_number, states: .register.designated_states}'

::

    {
      "number": "WO2007091761A1",
      "states": [
        "AT",
        "BE",
        "BG",
        "CH",
        [...]

    {
      "number": "EP0191689A1",
      "states": [
        "CH",
        "DE",
        "FR",
        "GB",
        "IT",
        "LI",
        "NL"
      ]
    }

    [...]

