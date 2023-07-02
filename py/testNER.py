from itertools import chain
import pycrfsuite
import sklearn
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer

from corpus_reader import CorpusReader

def is_hiragana(ch):
    # 平仮名ならTrue
    return 0x3040 <= ord(ch) <= 0x309F

def is_katakana(ch):
    # カタカナならTrue
    return 0x30A0 <= ord(ch) <= 0x30FF

def get_character_type(ch):
    '''
    入力文字列の種類判別
    @param  文字
    @return 種類の文字列
    '''
    if ch.isspace():
        return 'ZSPACE'
    elif ch.isdigit():
        return 'ZDIGIT'
    elif ch.islower():
        return 'ZLLET'
    elif ch.isupper():
        return 'ZULET'
    elif is_hiragana(ch):
        return 'HIRAG'
    elif is_katakana(ch):
        return 'KATAK'
    else:
        return 'OTHER'

def get_character_types(string):
    '''
    文字列に存在する文字の種類を取得
    （CRFで学習する際に用いる情報の一つ）
    @param  str 文字列
    @return strに存在する文字の種類 
    '''
    character_types = map(get_character_type, string)
    character_types_str = '-'.join(sorted(set(character_types)))

    return character_types_str


def extract_pos_with_subtype(morph):
    '''
    一単語の品詞情報を”全て”取得
    （CRFで学習する際に用いる情報の一つ）
    @param  morph   1単語
    @return 品詞情報（["名詞","固有名詞","組織"]）
    '''
    idx = morph.index('*')

    return '-'.join(morph[1:idx])

def word2features(sent, i):
    '''
        学習に使うデータをリスト化して生成
        @param  i   index
        @return リスト化されたデータ
    '''
    
    
    word = sent[i][0]
    chtype = get_character_types(sent[i][0])
    postag = extract_pos_with_subtype(sent[i])
    features = [
        'bias',
        'word=' + word,
        'type=' + chtype,
        'postag=' + postag,
    ]
    if i >= 2:
        word2 = sent[i-2][0]
        chtype2 = get_character_types(sent[i-2][0])
        postag2 = extract_pos_with_subtype(sent[i-2])
        iobtag2 = sent[i-2][-1]
        features.extend([
            '-2:word=' + word2,
            '-2:type=' + chtype2,
            '-2:postag=' + postag2,
            '-2:iobtag=' + iobtag2,
        ])
    else:
        features.append('BOS')

    if i >= 1:
        word1 = sent[i-1][0]
        chtype1 = get_character_types(sent[i-1][0])
        postag1 = extract_pos_with_subtype(sent[i-1])
        iobtag1 = sent[i-1][-1]
        features.extend([
            '-1:word=' + word1,
            '-1:type=' + chtype1,
            '-1:postag=' + postag1,
            '-1:iobtag=' + iobtag1,
        ])
    else:
        features.append('BOS')

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        chtype1 = get_character_types(sent[i+1][0])
        postag1 = extract_pos_with_subtype(sent[i+1])
        features.extend([
            '+1:word=' + word1,
            '+1:type=' + chtype1,
            '+1:postag=' + postag1,
        ])
    else:
        features.append('EOS')

    if i < len(sent)-2:
        word2 = sent[i+2][0]
        chtype2 = get_character_types(sent[i+2][0])
        postag2 = extract_pos_with_subtype(sent[i+2])
        features.extend([
            '+2:word=' + word2,
            '+2:type=' + chtype2,
            '+2:postag=' + postag2,
        ])
    else:
        features.append('EOS')

    return features


def sent2features(sent):
    ''' 1記事の学習データを生成 '''
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    ''' ラベル取得（形態素データの一番最後の列に貼ってある） '''
    return [morph[-1] for morph in sent]


def sent2tokens(sent):
    '''
        表層形を取得（単語そのもの）
    '''
    return [morph[0] for morph in sent]




c = CorpusReader('hironsan.txt')
train_sents = c.iob_sents('train')
test_sents = c.iob_sents('test')
X_train = [sent2features(s) for s in train_sents]
y_train = [sent2labels(s) for s in train_sents]

X_test = [sent2features(s) for s in test_sents]
y_test = [sent2labels(s) for s in test_sents]

trainer = pycrfsuite.Trainer(verbose=False)

for xseq, yseq in zip(X_train, y_train):
    trainer.append(xseq, yseq)

trainer.set_params({
    'c1': 1.0,   # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 50,  # stop earlier

    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})

trainer.train('model.crfsuite')

tagger = pycrfsuite.Tagger()
tagger.open('model.crfsuite')

example_sent = test_sents[0]
print(' '.join(sent2tokens(example_sent)))

print("Predicted:", ' '.join(tagger.tag(sent2features(example_sent))))
print("Correct:  ", ' '.join(sent2labels(example_sent)))


