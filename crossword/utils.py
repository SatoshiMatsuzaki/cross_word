#!/usr/bin/env python
# -*- coding: utf-8 -*-


def _replace_hyphen(text):
    """

    :param text:
    :return:
    """

    table = {
        'アカサタナハマヤラワガザダバパヷ': 'ア',
        'イキシチニヒミヰリギジヂビピヸ': 'イ',
        'ウクスツヌフムユルヴグズヅブプ': 'ウ',
        'エケセテネヘメヱレゲゼデベペヹ': 'エ',
        'オコソトノホモヨロヲゴゾドボポヺ': 'オ',
    }

    try:
        index_hyphen = text.index('ー')

        while index_hyphen != -1:
            pre_ = text[index_hyphen - 1]
            for k, v in table.items():
                if pre_ in k:
                    text = ''.join([text[:index_hyphen], v, text[index_hyphen + 1:]])
                    break
            index_hyphen = text.index('ー')
    except ValueError:
        pass

    return text


def _upper_zen_katakana(text):
    """

    :param text:
    :return:
    """

    table = {
        'ァ': 'ア',
        'ィ': 'イ',
        'ゥ': 'ウ',
        'ェ': 'エ',
        'ォ': 'オ',
        'ヵ': 'カ',
        'ヶ': 'ケ',
        'ッ': 'ツ',
        'ャ': 'ヤ',
        'ュ': 'ユ',
        'ョ': 'ヨ',
    }

    result = text

    for k, v in table.items():
        result = result.replace(k, v)

    return result
