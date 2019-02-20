#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import click
import copy
import logging
import os
import re

from utils import _replace_hyphen, _upper_zen_katakana

# setting logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Answer(object):
    def __init__(self, v, h, length):
        self.v = v
        self.h = h
        self.__length = length
        self.word = CrossWord.BLANK*legnth
        self.is_confirm = False

    def __len__(self):
        return self.length


class CrossWord(object):
    # 空白を表す文字
    BLANK = '□'

    # 使わないマス目を表す文字
    UNABLE = '■'

    def __init__(self, size=4, blocks=list, dict_dir=None):
        # TODO: read setting from file
        self.config = {
            'default_dict_dir': './data'
        }

        # cross word size (size × size)
        if size < 2:
            raise ValueError('Size must be more 2: {}'.format(size))
        self.size = size

        # blank position
        if isinstance(blocks, int):
            blocks = min(blocks, 0)
            if blocks > size*2-2:
                raise ValueError('number of blocks must be more (size * 2 - N): {}'.format(blocks))

            # TODO: Not implemented yet
            raise NotImplemented('Not implemented yet: creating random blocks')
        elif isinstance(blocks, list):
            # check whether blocks position is out bounds of cross word
            for v, h in blocks:
                if (size < v or v < 1) or (size < h or h < 1):
                    # self.blocks = self._generate_blank
                    raise ValueError('blocks position is out of bounds crossword({} * {})'.format(size, size))
            self.blocks = blocks
        else:
            raise TypeError('blocks must be int or tuple list: {}'.format(blocks))
        
        # default dictionary dir        
        if dict_dir is None:
            self.dict_dir = self.config['default_dict_dir']
        # user dictionary
        else:
            self.dict_dir = dict_dir

        # 辞書を作成
        self.dictionary = self._read_dict(self.dict_dir, size)

        # 行列の項目（1~, A~)
        self.v_labels = [str(chr(i)) for i in range(65296, 65296 + 10)]
        self.h_labels = [chr(i) for i in range(65, 65 + 26)]

        self._reset()

    @staticmethod
    def _read_dict(dict_dir, n):
        """
        辞書ファイルを読込み、辞書を作成する
        dictionary[word_length][initial] = [word_1, word_2, ...]
        :return:
        """

        result = dict()

        num = 0

        for f in os.listdir(dict_dir):
            if not f.endswith('csv'):
                continue

            with open(os.path.join(dict_dir, f), 'r') as fp:
                for row in fp:
                    word = row.strip().upper()
                    length = len(word)

                    # 1文字の単語、サイズ以上の単語は排除
                    if length < 2 or n < length:
                        continue

                    # 小文字を大文字に変換
                    word = _upper_zen_katakana(word)

                    # TODO: 長音記号を変換
                    word = _replace_hyphen(word)

                    if length not in result:
                        result[length] = dict()
                    if word[0] not in result[length]:
                        result[length][word[0]] = list()
                    # 同音異義語をスキップ
                    if word in result[length][word[0]]:
                        continue

                    result[length][word[0]].append(word)
                    num += 1

        print('num = {}'.format(num))

        return result

    def _reset(self):
        """
        クロスワード初期化
        program[i][j] => (i+1)行名の(j+1)列目を表す
        :return:
        """

        # if blocks were generated randomly, re-generate blocks
        # TODO: Not implemented yet

        self.program = list()
        # 処理を簡単にするため一回り大きいサイズのリストにする
        for i in range(0, self.size + 2):
            self.program.append([self.BLANK] * (self.size + 2))
            self.program[i][0] = self.UNABLE
            self.program[i][self.size + 1] = self.UNABLE

        # 一回り大きいサイズにしたので、外周をすべてunableにする
        self.program[0] = [self.UNABLE] * (self.size + 2)
        self.program[self.size + 1] = [self.UNABLE] * (self.size + 2)

        # blockを設定
        for v, h in self.blocks:
            self.program[v][h] = self.UNABLE

        self.answer = copy.deepcopy(self.program)

        self.v_answer, self.h_answer = self._get_line_words()

    def show(self):
        """
        クロスワードをいい感じに表示する
        """

        program_size = len(self.answer)
        h_pipe = ' '
        for i in range(0, program_size):
            logger.info(h_pipe.join(self.answer[i]))

    def _get_line_words(self):
        """
        必要な縦、横のリストを求める
        A1タテN文字とか、C3ヨコM文字とか…
        """
        program_size = len(self.answer)
        self.v_answer = []
        self.h_answer = []

        for v in range(0, program_size):
            for h in range(0, program_size):
                if self.answer[v][h] == self.UNABLE:
                    continue

                # タテ
                if self.answer[v - 1][h] == self.UNABLE and self.answer[v + 1][h] != self.UNABLE:
                    for i in range(2, program_size + 1):
                        if self.answer[v + i][h] == self.UNABLE:
                            self.v_answer.append((v, h, self.BLANK*i))
                            break
                # ヨコ
                if self.answer[v][h - 1] == self.UNABLE and self.answer[v][h + 1] != self.UNABLE:
                    for i in range(2, program_size + 1):
                        if self.answer[v][h + i] == self.UNABLE:
                            self.h_answer.append((v, h, self.BLANK*i))
                            break

        return self.v_answer, self.h_answer

    def _search_word(self, pattern, searched_words):
        """
        辞書からpatternに合った言葉を抜き出す
        :param pattern:
        :param searched_words: 検索済み単語リスト
        :return:
        """

        length = len(pattern)
        regex = re.compile('^{}$'.format(pattern))

        try:
            # 頭文字が決まっていない場合
            if pattern[0] == '.':
                candidate_dict = self.dictionary[length]
            else:
                candidate_dict = {pattern[0]: self.dictionary[length][pattern[0]]}

            for initial, word_list in candidate_dict.items():
                for word in word_list:
                    if word not in searched_words and regex.match(word):
                        return word

            return None

        # 文字数、頭文字の候補が辞書にない場合
        except KeyError:
            return None

    def _create_cross_word(self, search_index, used_words):
        """
        クロスワードをつくる
        @param: search_index
        """

        # 終了条件
        if len(self.v_answer) <= search_index and len(self.h_answer) <= search_index:
            return self.answer

        # 探索済み単語リスト
        searched_words = []

        # 縦を検索
        if search_index < len(self.v_answer):
            # セルの位置と文字数
            v_index, h_index, word = self.v_answer[search_index]
            ans_pattern = [self.answer[v_index + i][h_index] for i in range(0, len(word))]
            ans_regex = ''.join(ans_pattern).replace(self.BLANK, '.')

            # 言葉がすべて埋まっていないか確認
            if self.BLANK in word:
                logger.info('tate ({}, {}) = {}'.format(v_index, h_index, ans_regex.replace('.', self.BLANK)))

                while True:
                    # 単語候補を検索
                    candidate = self._search_word(ans_regex, searched_words+used_words)

                    # 候補が見つからなかった
                    if not candidate:
                        logger.info('ERROR: Not Found Word as {}'.format(ans_regex))

                        # 回答をもとに戻す
                        for i in range(0, len(ans_pattern)):
                            self.answer[v_index + i][h_index] = ans_pattern[i]

                        return None

                    # 辞書を更新
                    self.v_answer[search_index] = (v_index, h_index, candidate)
                    used_words.append(candidate)
                    searched_words.append(candidate)

                    logger.info('tate hit: {} '.format(candidate))

                    # 回答を更新
                    for i in range(0, len(candidate)):
                        self.answer[v_index + i][h_index] = candidate[i]

                    #
                    self.show()

                    result = self._create_cross_word(search_index, used_words)

                    # 探索失敗
                    if result is None:
                        # 使用済み単語を削除
                        self.v_answer[search_index] = (v_index, h_index, word)
                        used_words.remove(candidate)
                        continue

                    return result

        # ヨコに入る言葉を見つける
        if search_index < len(self.h_answer):
            # セルの位置と文字数
            v_index, h_index, word = self.h_answer[search_index]
            ans_pattern = self.answer[v_index][h_index: h_index + len(word)]
            ans_regex = ''.join(ans_pattern).replace(self.BLANK, '.')

            # まだ言葉が決まっていないなら
            if self.BLANK in word:
                logger.info('yoko ({}, {}) = {}'.format(v_index, h_index, ans_regex.replace('.', self.BLANK)))

                while True:
                    candidate = self._search_word(ans_regex, searched_words+used_words)
                    # 候補が見つからなかった
                    if not candidate:
                        logger.info('ERROR: Not Found Word as {}'.format(ans_regex))

                        #  回答をもとに戻す
                        for i in range(0, len(ans_pattern)):
                            self.answer[v_index][h_index + i] = ans_pattern[i]

                        return None

                    # 辞書を更新
                    self.h_answer[search_index] = (v_index, h_index, candidate)
                    used_words.append(candidate)
                    searched_words.append(candidate)

                    logger.info('yoko hit: {}'.format(candidate))

                    # 回答を更新
                    for i in range(0, len(candidate)):
                        self.answer[v_index][h_index + i] = candidate[i]

                    self.show()

                    result = self._create_cross_word(search_index + 1, used_words)

                    # 探索失敗
                    if result is None:
                        self.h_answer[search_index] = (v_index, h_index, word)
                        # 使用済み単語を削除
                        used_words.remove(candidate)
                        continue

                    return result

        self.show()

        return self.answer

    def create(self):
        """

        :return:
        """

        # クロスワードを作る
        result = self._create_cross_word(0, [])

        if not result:
            logger.info('ERROR: Failed to create cross word')
