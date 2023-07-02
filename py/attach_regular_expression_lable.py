import re
import sys
import parse_mecab

''' クラス化したい '''
pattern = r"[\d,，\. .一二三四五六七八九十百千万億兆京]*(円|ユーロ)"
regular_dic = { r"[\d,，\. .一二三四五六七八九十百千万億兆京]*(円|ユーロ)":"MNY",
r"(\d{4})年(\d{1,2})月(\d{1,2})日":"DAT"
}
 
def get_match_index(sentence, pattern):
    ''' 正規表現のpatternに一致したsentenceを返す '''
    find_iter = []

    for match in re.finditer(pattern, sentence) :
        find_iter.append(match.span())

    find_index = []
    find_index.extend([list(range(tpl[0], tpl[1]))for tpl in find_iter ])

    find_index = [e for lst in find_index for e in lst]

    return find_index

def get_surface_word(mecab_list):
    return "".join([word.split("\t")[0] for word in mecab_list])


def attach_regular_expression_label(document, filename, regular_dic):
    document_list = parse_mecab.parse_mecab_document_list(document)

    end_article_num = 0
    article_num = len(document_list)
    for article in document_list[:]:
        end_article_num += 1
        print ("%d / %d" % (end_article_num, article_num))

        for pattern, label_name in regular_dic.items():
            str_len = 0
            find_index = get_match_index(get_surface_word(article), pattern)
            for i, word in enumerate(article):
                word_list = word.split("\t")
                str_len += len(word_list[0])
                if str_len - 1 in find_index:
                   reword = word_list[:-2]
                   if word_list[-1] == "0" and i != 0 and "B-" + label_name in article[i - 1] :
                       reword.append("I-" + label_name)
                   else:
                       reword.append("B-" + label_name)

                   article[i] = "\t".join(reword) 

        with open(filename, "w") as fout:
            for article in document_list:
                fout.write("\n".join(article) + "\n\n")

if __name__ == "__main__":
    with open(sys.argv[1], "r") as fin:
        attach_regular_expression_label(fin.read(), sys.argv[2], regular_dic)
