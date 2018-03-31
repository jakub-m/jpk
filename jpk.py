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


OUTPUT_TPL=u'''
KodFormularza;kodSystemowy;wersjaSchemy;WariantFormularza;CelZlozenia;DataWytworzeniaJPK;DataOd;DataDo;NazwaSystemu;NIP;PelnaNazwa;Email;LpSprzedazy;NrKontrahenta;NazwaKontrahenta;AdresKontrahenta;DowodSprzedazy;DataWystawienia;DataSprzedazy;K_10;K_11;K_12;K_13;K_14;K_15;K_16;K_17;K_18;K_19;K_20;K_21;K_22;K_23;K_24;K_25;K_26;K_27;K_28;K_29;K_30;K_31;K_32;K_33;K_34;K_35;K_36;K_37;K_38;K_39;LiczbaWierszySprzedazy;PodatekNalezny;LpZakupu;NrDostawcy;NazwaDostawcy;AdresDostawcy;DowodZakupu;DataZakupu;DataWplywu;K_43;K_44;K_45;K_46;K_47;K_48;K_49;K_50;LiczbaWierszyZakupow;PodatekNaliczony
JPK_VAT;JPK_VAT (3);1-1;3;0;:data_wytworzenia_jpk:;:data_od:;:data_do:;nazwa programu ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;:nip:;:pelna_nazwa:;:email:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;1;:nr_kontrahenta:;:nazwa_kontrahenta:;:adres_kontrahenta:;:dowod_sprzedarzy:;:data_wystawienia:;:data_sprzedarzy:;;;;;;;;;;:k_19:;:k_20:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;1;:podatek_nalezny:;;;;;;;;;;;;;;;;;;
'''

INPUT_FILE_PREFIX = "wypelnij_JPK_VAT"
OUTPUT_FILE_PREFIX = "JPK_VAT"

def _main():
    in_fname = detect_input_file()
    logger.info(u'input file name: %s', in_fname)
    out_fname = get_out_fname(in_fname)
    logger.info(u'out_fname: %s', out_fname)
    if os.path.exists(out_fname):
        raise ValueError(u"Plik {} już istnieje, usuń go i spróbuj jeszcze raz.".format(out_fname))
    with codecs.open(in_fname, encoding='utf-8') as h:
        vars = read_variables(h.read())
    logger.info(u"vars: %s", vars)
    validate_vars(vars)
    out_str = produce_output(vars)
    with codecs.open(out_fname, 'w', encoding='utf-8') as h:
        h.write(out_str)
    logger.info(u'done!')
    print(u'Zrobione! Plik wynikowy to {}'.format(out_fname))


def detect_input_file():
    dir_ = os.getcwd()
    logger.info(u"detect_input_file: %s", dir_)
    files = os.listdir(dir_)
    logger.info(u"detect_input_file: %s", files)
    candidates = [f for f in files if f.startswith(INPUT_FILE_PREFIX) and f.endswith(".txt")]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError(u"Potrzebuję dokładnie jednego pliku zaczynającego się na {}, z rozszerzeniem .txt".format(INPUT_FILE_PREFIX))


def get_out_fname(in_fname):
    if not in_fname.startswith(INPUT_FILE_PREFIX):
        raise ValueError("Bad input file name: ".format(in_fname))
    base, ext = os.path.splitext(in_fname[len(INPUT_FILE_PREFIX):])
    return u"{}{}.csv".format(OUTPUT_FILE_PREFIX, base)


def validate_vars(vars):
    check_vars_types(vars)
    check_vars_match_template(vars)


def check_vars_match_template(vars):
    template_keys = read_variable_keys(OUTPUT_TPL)
    vars_keys = set(vars.keys())
    unknown_keys_in_template = template_keys - vars_keys
    if unknown_keys_in_template:
        raise ValueError(u'Nie podałeś wartoście dla: {}'.format(u', '.join(sorted(unknown_keys_in_template))))
    unknown_keys_in_input = vars_keys - template_keys
    if unknown_keys_in_input:
        raise ValueError(u'Nie wiem co to za pole wejściowe: {}'.format(u', '.join(sorted(unknown_keys_in_input))))


def check_vars_types(vars):
    check_vars_date(vars, 'data_od')
    check_vars_date(vars, 'data_do')
    check_vars_date(vars, 'data_wystawienia')
    check_vars_date(vars, 'data_sprzedarzy')
    check_vars_nip(vars, 'nip')
    check_vars_nip(vars, 'nr_kontrahenta')
    check_vars_int(vars, 'k_19')
    check_vars_int(vars, 'k_20')
    check_vars_int(vars, 'podatek_nalezny')


def check_vars_date(vars, key):
    if key not in vars:
        return
    m = re.match(ur'\d{4}-\d{2}-\d{2}$', vars[key])
    if m is None:
        raise ValueError(u'Pole {} powinno być w formacie YYYY-MM-DD (np 2018-01-23)'.format(key))


def check_vars_nip(vars, key):
    if key not in vars:
        return
    m = re.match(ur'\d{10}$', vars[key])
    if m is None:
        raise ValueError(u'Pole {} powinno zawierać NIP (10 cyfr)'.format(key))


def check_vars_int(vars, key):
    if key not in vars:
        return
    m = re.match(r'\d+$', vars[key])
    if m is None:
        raise ValueError(u'Pole {} powinno zawierać liczbę (bez kropek i przecinków)'.format(key))


def read_variables(str_):
    d = {}
    for k, v in re.findall(ur':(\S+):\s*(.*)?$', str_, re.MULTILINE):
        d[k] = v.strip()
    return d


def read_variable_keys(str_):
    return set(k.strip() for k in re.findall(ur':([^\s:;]+):', str_, re.MULTILINE))


def produce_output(vars):
    tpl = OUTPUT_TPL.strip()
    for k in vars:
        tpl = tpl.replace(':{}:'.format(k), vars[k])
    return tpl


def main():
    try:
        _main()
    except Exception as e:
        logger.exception(u"Something went wrong")
        print(u"Błąd! " + e.message)
        sys.exit(1)

main()
