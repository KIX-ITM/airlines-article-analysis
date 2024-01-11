import csv
import os

import spacy

import setting

'''
TODO:
- csv読み取り
- 自然言語処理
    - 類似文書の検索
        - GiNZAでタイトルをベクトル化
            - 学習済みの単語ベクトルを利用してテキストをベクトル化出来る
        - 類似度を求める
            - それぞれのタイトルごとの類似度を算出
        - 参考：https://dev.classmethod.jp/articles/try-cosine-similarity-using-ginza-and-spacy/
    - 記事のタグ付け
        - 固有表現抽出
            - 固有表現ごとの出現回数をカウント
            - 出現するタイトルIDも記録
- BIインポート用csvデータ作成    
'''

class Analysis:

    nlp = None
    vector_lists = []
    named_entity_lists = []

    @classmethod
    def init_spacy(cls):
        # 自然言語処理に使うライブラリの初期化
        cls.nlp = spacy.load('ja_ginza')
        config = {
            'overwrite_ents': True
        }
        ruler = cls.nlp.add_pipe('entity_ruler', config=config)
        patterns = []
        for data in TitleData.group_lists:
            # group_listの単語を固有表現として認識するよう登録
            patterns.append(dict(
                label="Group",
                pattern=data[1]
            ))
        ruler.add_patterns(patterns)

    @classmethod
    def create_similarity_csv_data(cls):
        # 類似度リストをcsvに書き出し
        similarities = cls._create_similarity_lists()
        header = ["id", "title_id_1", "title_id_2", "similarity"]
        Csv.export_csv(setting.SIMILARITY_FILE_PATH, header, similarities)

    @classmethod
    def create_named_entity_csv_data(cls):
        # 固有表現リストをcsvに書き出し
        cls.named_entity_lists = cls._create_named_entity_lists()
        header = ["id", "named_entity", "label", "title_id_count", "title_id_list"]
        Csv.export_csv(setting.NAMED_ENTITY_FILE_PATH, header, cls.named_entity_lists)

    @classmethod
    def create_article_tag_csv_data(cls):
        article_tag_lists = cls._create_article_tag_lists()
        header = ["id", "title_id", "named_entity_id"]
        Csv.export_csv(setting.ARTICLE_TAG_FILE_PATH, header, article_tag_lists)


    @classmethod
    def create_vector_lists(cls):
        # 記事タイトルことのベクトルリスト
        for data in TitleData.title_lists:
            title_id = data[0]
            text = data[2]
            cls.vector_lists.append([title_id, cls._vectorization(text)])

    @classmethod
    def _create_article_tag_lists(cls):
        # 記事タグリスト作成
        article_tag_lists = []
        count = 0
        named_entity_dict = cls._create_named_entity_dict()
        for key in named_entity_dict.keys():
            title_list = named_entity_dict[key]
            for t in title_list:
                count += 1
                id = "A{:0>5}".format(str(count))
                title_id = t
                named_entity_id = key
                article_tag_lists.append([id, title_id, named_entity_id])
        return article_tag_lists


    @classmethod
    def _create_named_entity_dict(cls):
        # 記事タグリスト作成の前準備
        # key:named_entity_id value:title_id_list の辞書作成
        named_entity_dict = {}
        for data in cls.named_entity_lists:
            named_entity_dict[data[0]] = data[4]

        return named_entity_dict


    @classmethod
    def _create_named_entity_lists(cls):
        named_entity_lists = []
        count = 1
        for data in cls.vector_lists:
            title_id = data[0]
            for ent in data[1].ents:
                index = [i for i, _ in enumerate(named_entity_lists) if ent.text == _[1]]
                if len(index) == 0:
                    # リストに固有表現が登録されていない場合は新規追加
                    id = "N{:0>5}".format(str(count))
                    text = ent.text
                    label = ent.label_
                    title_id_count = 1
                    title_id_list = [title_id]
                    named_entity_lists.append([id, text, label, title_id_count, title_id_list])
                    count += 1
                else:
                    # 登録されている場合はタイトルIDのカウント+1,タイトルIDのリスト追加を行う
                    i = index[0]
                    named_entity_lists[i][3] += 1
                    named_entity_lists[i][4].append(title_id)

        return named_entity_lists

    @classmethod
    def _vectorization(cls, text):
        # テキストのベクトル化処理
        return cls.nlp(text)

    @classmethod
    def _create_similarity_lists(cls):
        # 類似度毎にID付与
        similarities = []
        count = 1
        for i, data1 in enumerate(cls.vector_lists):
            title_id1 = data1[0]
            doc1 = data1[1]
            for j, data2 in enumerate(cls.vector_lists):
                title_id2 = data2[0]
                doc2 = data2[1]
                if i < j:
                    # 重複を避ける
                    id = "S{:0>8}".format(str(count))
                    similarity = cls._calculate_similarity(doc1, doc2)
                    similarities.append([id, title_id1, title_id2, similarity])
                    count += 1
        return similarities

    @classmethod
    def _calculate_similarity(cls, doc1, doc2):
        # 類似度の算出
        return doc1.similarity(doc2)



class Csv:

    @classmethod
    def import_csv(cls, path):
        # csvファイルデータをリストに変換
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            next(csv_reader)
            for row in csv_reader:
                data.append(row)
        return data

    @classmethod
    def export_csv(cls, path, header, data):
        # リストデータをcsvにエクスポート（上書き）
        with open(path, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)


class TitleData:

    imported_title_lists = []
    title_lists = []
    group_lists = []

    @classmethod
    def create_lists(cls):
        # csv書き出し前準備
        # 記事タイトル一覧とグループ一覧のリストを生成
        cls._join_raw_data_file()
        cls._create_title_lists()
        cls._create_group_lists()
        cls._replace_group_column()

    @classmethod
    def create_csv_data(cls):
        # 記事タイトルリストとグループリストのcsvファイル生成
        title_header = ["id", "group_id", "title", "datetime"]
        Csv.export_csv(setting.TITLE_FILE_PATH, title_header, cls.title_lists)
        group_header = ["id", "group"]
        Csv.export_csv(setting.GROUP_FILE_PATH, group_header, cls.group_lists)

    @classmethod
    def _join_raw_data_file(cls):
        # スクレイピングデータの読込み前準備
        # 複数のスクレイピングファイルを1つにまとめる
        lists = []
        combined_data = []
        condition = 'article_title_raw_data_'
        for filename in os.listdir(setting.DIR_PATH):
            if filename.startswith(condition):
                path = setting.DIR_PATH + "/" + filename
                lists.append(Csv.import_csv(path))
        for l in lists:
            combined_data.extend(l)
        header = setting.RAW_DATA_HEADER
        Csv.export_csv(setting.RAW_DATA_FILE_PATH, header, combined_data)


    @classmethod
    def _replace_group_column(cls):
        # 記事タイトルリストのグループ名をグループIDに変更
        for data in cls.title_lists:
            group = data[1]
            group_id = [_[0] for _ in cls.group_lists if _[1] == group]
            data[1] = group_id[0] if len(group_id) > 0 else None

    @classmethod
    def _create_title_lists(cls):
        # 記事タイトルリストを作成
        cls.imported_title_lists = Csv.import_csv(setting.RAW_DATA_FILE_PATH)
        cls._add_columns()
        cls._delete_space()

    @classmethod
    def _create_group_lists(cls):
        # グループリストを作成
        group = [_[1] for _ in cls.title_lists]
        group = list(set([_ for _ in group if group.count(_) > 1]))
        count = 1
        for g in group:
            if not bool(g):
                continue
            id = "G{:0>5}".format(str(count))
            cls.group_lists.append([id, g])
            count += 1

    @classmethod
    def _delete_space(cls):
        # 不要なスペース文字を削除
        for data in cls.title_lists:
            data[1] = data[1].replace("\u3000", " ")
            data[2] = data[2].replace("\u3000", " ")

    @classmethod
    def _add_columns(cls):
        # 記事タイトルリストにIDと会社名の列を追加
        for i, data in enumerate(cls.imported_title_lists):
            id = "T{:0>5}".format(str(i + 1))
            words = data[0].split("、", 1)
            group = words[0] if len(words) > 1 else ""
            named_entity_ids = None

            cls.title_lists.append([id, group, data[0], data[1]])



if __name__ == "__main__":
    TitleData.create_lists()
    Analysis.init_spacy()
    Analysis.create_vector_lists()
    Analysis.create_named_entity_csv_data()
    Analysis.create_similarity_csv_data()
    Analysis.create_article_tag_csv_data()
    # TitleData.add_named_entity_column()
    TitleData.create_csv_data()
