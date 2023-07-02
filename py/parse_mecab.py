import sys
import MeCab

m = MeCab.Tagger ("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd ")

def parse_mecab_list(sentence):
    mecab_sentence_str = m.parse(sentence)
    mecab_sentence_list = [word.replace(",", "\t") for word in mecab_sentence_str.split("\n")] 
    mecab_sentence_list_add_zero = [word + "\t0"for word in mecab_sentence_list[:-2]]

    
    return mecab_sentence_list_add_zero

def parse_mecab_document_list(document):
    document_list = []
    for sentence in document.split("\n") :
        document_list.append(parse_mecab_list(sentence))
    return document_list

def write_mecab_parse(document, filename):
    mecab_list = parse_mecab_document_list(document)
    with open(filename, "w") as fout:
        for article in mecab_list:
            fout.write("\n".join(article) + "\n\n")

if __name__ == "__main__":
    with open(sys.argv[1], "r") as fin:
        write_mecab_parse(fin.read(), sys.argv[2])
