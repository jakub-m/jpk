#!/usr/bin/env python2.7
# encoding: utf-8

import codecs
import logging
import os
import re
import sys


FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, filename='diagnostyka.txt', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)


OUTPUT_TPL='''
KodFormularza;kodSystemowy;wersjaSchemy;WariantFormularza;CelZlozenia;DataWytworzeniaJPK;DataOd;DataDo;NazwaSystemu;NIP;PelnaNazwa;Email;LpSprzedazy;NrKontrahenta;NazwaKontrahenta;AdresKontrahenta;DowodSprzedazy;DataWystawienia;DataSprzedazy;K_10;K_11;K_12;K_13;K_14;K_15;K_16;K_17;K_18;K_19;K_20;K_21;K_22;K_23;K_24;K_25;K_26;K_27;K_28;K_29;K_30;K_31;K_32;K_33;K_34;K_35;K_36;K_37;K_38;K_39;LiczbaWierszySprzedazy;PodatekNalezny;LpZakupu;NrDostawcy;NazwaDostawcy;AdresDostawcy;DowodZakupu;DataZakupu;DataWplywu;K_43;K_44;K_45;K_46;K_47;K_48;K_49;K_50;LiczbaWierszyZakupow;PodatekNaliczony
JPK_VAT;JPK_VAT (3);1-1;3;0;:data_wytworzenia_jpk:;:data_od:;:data_do:;nazwa programu ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;:nip:;:pelna_nazwa:;:email:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;1;:nr_kontrahenta:;:nazwa_kontrahenta:;:adres_kontrahenta:;:dowod_sprzedarzy:;:data_wystawienia:;:data_sprzedarzy:;;;;;;;;;;:k_19:;:k_20:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;1;:podatek_nalezny:;;;;;;;;;;;;;;;;;;
'''

def _main():
    in_fname = detect_input_file()
    logger.info('input file name: %s', in_fname)
    out_fname = get_out_fname(in_fname)
    logger.info('out_fname: %s', out_fname)
    if os.path.exists(out_fname):
        raise ValueError("Plik {} już istnieje, usuń go i spróbuj jeszcze raz.".format(out_fname))
    with codecs.open(in_fname, encoding='utf-8') as h:
        vars = read_variables(h.read())
    logger.info("vars: %s", vars)
    out_str = produce_output(vars)
    with codecs.open(out_fname, 'w', encoding='utf-8') as h:
        h.write(out_str)
    logger.info('done!')
    print('Zrobione! Plik wynikowy to {}'.format(out_fname))


def detect_input_file():
    dir_ = os.getcwd()
    logger.info("detect_input_file: %s", dir_)
    files = os.listdir(dir_)
    logger.info("detect_input_file: %s", files)
    candidates = [f for f in files if f.startswith("JPK_VAT") and f.endswith(".txt")]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError("Potrzebuję dokładnie jednego pliku zaczynającego się na JPK_VAT, z rozszeżeniem .txt")


def get_out_fname(in_fname):
    base, ext = os.path.splitext(in_fname)
    return base + ".csv"


def read_variables(str_):
    d = {}
    for k, v in re.findall(ur'(:\S+:)\s*(.*)?$', str_, re.MULTILINE):
        d[k] = v.strip()
    return d


def produce_output(vars):
    tpl = OUTPUT_TPL.strip()
    for k in vars:
        tpl = tpl.replace(k, vars[k])
    return tpl


def main():
    try:
        _main()
    except Exception as e:
        logger.exception("Something went wrong")
        print("Błąd! " + e.message)
        sys.exit(1)

main()


# TODO data wytworzenia jpk
# TODO walidacja formatow
# TODO brakujace pola