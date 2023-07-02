# from itertools import chain
# import pycrfsuite
# import sklearn
# from sklearn.metrics import classification_report
# from sklearn.preprocessing import LabelBinarizer

import codecs

class CorpusReader(object):
    '''
        コーパス読み込みクラス
    '''
    def __init__(self, path):
        
        '''
            (読み込みファイル形式)
            一行（形態素解析された１単語）
            mecab変換形式 -> [, -> \t]変換 -> 最終列にラベルを貼tたもの
        '''
        with codecs.open(path, encoding='utf-8') as f:
            sent = []
            sents = []  # 一記事の形態素解析要素
            for line in f:
                if line == '\n':
                    sents.append(sent)
                    sent = []
                    continue
                morph_info = line.strip().split('\t')
                sent.append(morph_info)

        train_num = int(len(sents) * 0.9)
        self.__train_sents = sents[:train_num]  # 記事の9割を訓練データ
        self.__test_sents = sents[train_num:] # 残り1割をテストデータ

    def iob_sents(self, name):
        '''
            訓練データ、テストデータのゲッタ
        '''
        if name == 'train':
            return self.__train_sents
        elif name == 'test':
            return self.__test_sents
        else:
            return None

